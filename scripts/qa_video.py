from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/qa_video.py <video.mp4>")
    video = Path(sys.argv[1])
    if not video.is_file() or video.stat().st_size < 100_000:
        raise SystemExit("FAIL: output missing or suspiciously small")
    raw = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video)
    ], text=True)
    data = json.loads(raw)
    streams = data.get("streams", [])
    v = next((s for s in streams if s.get("codec_type") == "video"), None)
    a = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if not v or not a:
        raise SystemExit("FAIL: both video and audio streams are required")
    duration = float(data["format"]["duration"])
    if v.get("width") != 1080 or v.get("height") != 1920:
        raise SystemExit(f"FAIL: expected 1080x1920, got {v.get('width')}x{v.get('height')}")
    if duration < 25 or duration > 90:
        raise SystemExit(f"FAIL: unexpected duration {duration:.2f}s")
    if v.get("codec_name") != "h264":
        raise SystemExit(f"FAIL: expected H.264, got {v.get('codec_name')}")
    fps_parts = v.get("avg_frame_rate", "0/1").split("/")
    actual_fps = float(fps_parts[0]) / float(fps_parts[1]) if float(fps_parts[1]) else 0
    if abs(actual_fps - 30) > 0.01:
        raise SystemExit(f"FAIL: expected 30 FPS, got {actual_fps:.3f}")
    print(f"PASS: {video} | {duration:.2f}s | 1080x1920 | H.264 + {a.get('codec_name')} | {video.stat().st_size:,} bytes")
    return 0

if __name__ == "__main__":
    sys.exit(main())