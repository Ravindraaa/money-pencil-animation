# The Money Stickman — Pencil Animation Studio

A deterministic, reusable pencil-sketch animation pipeline for vertical YouTube Shorts and horizontal long-form videos.

## First pilot
**The $7 Coffee That Could Cost You $50,000** — an illustrative compounding example, not a forecast or promise.

## Requirements
- Node.js 20+
- Python 3.11+
- FFmpeg
- Playwright Chromium

## Local setup
```bash
npm ci
python -m pip install -r requirements.txt
npx playwright install chromium
```

## Render the pilot
```bash
npm run render:short
```
The rendered MP4 and metadata are written to `output/`.

## Design principles
- Original SVG pencil-drawn artwork; no stock assets or unlicensed music.
- Time-driven scenes: the same timestamp always produces the same frame.
- Narration-first timing, readable captions, and non-clipping audio mix.
- QA checks for duration, dimensions, frame rate, audio stream, and output file integrity.

## Note on the money example
The stated future value is a hypothetical illustration using regular contributions and an assumed annual return. Actual market returns vary, and fees, taxes, inflation, and missed contributions change results. This is educational content, not personal financial advice.


## Reusable Shorts workflow

The renderer now accepts a script JSON file and output name through environment variables:

- `SHORT_SPEC`: path to a JSON script under `scripts/`
- `OUTPUT_NAME`: output basename (no extension)

Create a new script by copying `scripts/short_template.json`, then edit the title and seven narration segments. Use any number of non-empty narration segments. Each beat is classified by the local semantic planner and rendered with a topic-matched pencil illustration (budget, investing, growth, debt, housing, risk, goals, or general explainer). The planner is deterministic and does not require a paid API key.

### Render any script from GitHub Actions

Open **Actions → Render Money Stickman Short → Run workflow**, choose the JSON file path and output basename. The workflow renders the MP4, runs technical QA, and uploads the MP4 plus metadata as an artifact.

### Local render

```bash
SHORT_SPEC=scripts/your_topic.json OUTPUT_NAME=money-stickman-your-topic npm run render:short
python scripts/qa_video.py output/money-stickman-your-topic.mp4
```

This is a reusable script-in/video-out pipeline. A local semantic planner creates a storyboard for every narration beat, the SVG scene renderer chooses a matching illustration, and the renderer exports an MP4, metadata JSON, and storyboard JSON. The planner is deterministic rule-based classification, not an LLM-generated custom drawing system; the visual library can be expanded independently of the TTS and timeline core.
