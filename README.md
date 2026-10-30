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

Create a new script by copying `scripts/short_template.json`, then edit the title and seven narration segments. Keep the seven beats in order: hook, context, alternative, math, risk, takeaway, CTA. The current visual template maps these seven beats to its seven illustrated scene types, so narration must follow that order until the scene library is expanded.

### Render any script from GitHub Actions

Open **Actions → Render Money Stickman Short → Run workflow**, choose the JSON file path and output basename. The workflow renders the MP4, runs technical QA, and uploads the MP4 plus metadata as an artifact.

### Local render

```bash
SHORT_SPEC=scripts/your_topic.json OUTPUT_NAME=money-stickman-your-topic npm run render:short
python scripts/qa_video.py output/money-stickman-your-topic.mp4
```

This is a reusable script-driven pipeline, not yet an AI storyboard generator: the seven scene illustrations are a reusable template. A later scene-library upgrade can add more visual types without changing the TTS/timeline/render core.


## Semantic storyboard planner (new)

Before rendering, the pipeline now runs a local, rule-based planner over every narration beat. It classifies beats into finance scene types (budget/spending, investing, growth, debt, housing, risk, goals, or general explainer), extracts drawable entity tags and numeric emphasis labels, and writes a storyboard JSON beside the MP4. It uses no external API key or paid model.

Run its tests with:

```bash
python -m unittest discover -s tests -v
```

The planner is the first semantic layer, not a claim of fully generated artwork yet. The existing SVG renderer still draws its current scene library; the next increment will connect these scene plans to a broader reusable SVG asset library and per-word caption timing.
