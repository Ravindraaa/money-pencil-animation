from __future__ import annotations

import asyncio
import json
import math
import shutil
import subprocess
import sys
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path

import edge_tts
from playwright.sync_api import sync_playwright
from scene_planner import build_storyboard

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
WORK = ROOT / "work"
SPEC_PATH = Path(__import__("os").environ.get("SHORT_SPEC", str(ROOT / "scripts/short_01.json"))).resolve()
SPEC = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
OUTPUT_NAME = __import__("os").environ.get("OUTPUT_NAME", SPEC_PATH.stem.replace("short_", "money-stickman-"))
VOICE = SPEC.get("voice", "en-US-GuyNeural")
FPS = int(SPEC.get("fps", 30))
WIDTH = int(SPEC.get("width", 1080))
HEIGHT = int(SPEC.get("height", 1920))


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def probe_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        check=True, capture_output=True, text=True
    )
    return float(result.stdout.strip())


async def synthesize(segment: str, destination: Path) -> None:
    communicate = edge_tts.Communicate(segment, VOICE, rate="-8%", volume="+0%")
    await communicate.save(str(destination))


def main() -> int:
    for binary in ("ffmpeg", "ffprobe"):
        if shutil.which(binary) is None:
            raise SystemExit(f"Required executable not found: {binary}")

    OUT.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    audio_dir = WORK / "audio"
    frames_dir = WORK / "frames"
    audio_dir.mkdir(exist_ok=True)
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir()

    segments = SPEC["segments"]
    audio_paths: list[Path] = []
    for index, text in enumerate(segments):
        destination = audio_dir / f"segment_{index:02d}.mp3"
        asyncio.run(synthesize(text, destination))
        audio_paths.append(destination)

    durations = [probe_duration(path) for path in audio_paths]
    # Short pauses between sentences let the viewer process each visual beat.
    pause_seconds = 0.22
    silence = WORK / "pause.mp3"
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
         "-t", str(pause_seconds), "-c:a", "libmp3lame", "-q:a", "9", str(silence)])
    timeline = []
    cursor = 0.0
    for index, duration in enumerate(durations):
        timeline.append({"start": cursor, "end": cursor + duration, "text": segments[index]})
        cursor += duration + (pause_seconds if index < len(durations) - 1 else 0.0)
    total_duration = cursor

    storyboard = build_storyboard(segments)
    for item, scene in zip(timeline, storyboard["scenes"]):
        item["scene"] = scene
    storyboard_path = OUT / f"{OUTPUT_NAME}-storyboard.json"
    storyboard_path.write_text(json.dumps(storyboard, indent=2), encoding="utf-8")
    timeline_path = WORK / "timeline.json"
    timeline_path.write_text(json.dumps({"duration": total_duration, "segments": timeline}), encoding="utf-8")
    concat_file = WORK / "audio_concat.txt"
    concat_entries = []
    for index, path in enumerate(audio_paths):
        concat_entries.append(f"file '{path.resolve().as_posix()}'\n")
        if index < len(audio_paths) - 1:
            concat_entries.append(f"file '{silence.resolve().as_posix()}'\n")
    concat_file.write_text("".join(concat_entries), encoding="utf-8")
    narration = WORK / "narration.mp3"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
         "-c:a", "libmp3lame", "-q:a", "3", str(narration)])

    handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 8765), handler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    frame_count = math.ceil(total_duration * FPS)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT}, device_scale_factor=1)
        page.goto("http://127.0.0.1:8765/src/index.html?timeline=/work/timeline.json", wait_until="load")
        page.wait_for_function("window.renderAt !== undefined")
        for frame in range(frame_count):
            timestamp = frame / FPS
            page.evaluate("(t) => window.renderAt(t)", timestamp)
            page.screenshot(path=str(frames_dir / f"frame_{frame:06d}.png"))
        browser.close()
    server.shutdown()
    server.server_close()

    silent_video = WORK / "silent.mp4"
    final_video = OUT / f"{OUTPUT_NAME}.mp4"
    run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", str(frames_dir / "frame_%06d.png"),
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-an", str(silent_video)])
    run(["ffmpeg", "-y", "-i", str(silent_video), "-i", str(narration),
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
         "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(final_video)])

    metadata = {
        "title": SPEC["title"],
        "description": (
            "Educational content from The Money Stickman. Examples and projections are "
            "illustrative only, not promises or personal financial advice. Verify figures, "
            "assumptions, fees, taxes, and local rules before making financial decisions.\n\n"
            "Follow The Money Stickman for practical money lessons."
        ),
        "hashtags": ["#PersonalFinance", "#MoneyHabits", "#InvestingBasics", "#MoneyStickman"],
        "voice": VOICE,
        "duration_seconds": round(total_duration, 2),
        "fps": FPS,
        "resolution": f"{WIDTH}x{HEIGHT}",
        "storyboard_file": storyboard_path.name,
        "scene_planner": storyboard["planner"],
        "scene_count": storyboard["scene_count"]
    }
    (OUT / f"{OUTPUT_NAME}-metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Rendered: {final_video}")
    print(f"Duration: {total_duration:.2f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())