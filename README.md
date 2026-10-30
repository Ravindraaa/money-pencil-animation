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
