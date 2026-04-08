# rstroke-conversion

Convert filled SVG icon outlines into true centerline stroke paths so stroke width stays editable in Figma, while preserving original canvas size, proportions, and geometry as closely as possible.

## What This Skill Does

`rstroke-conversion` is a Codex skill for transforming icon-like SVGs where linework is encoded as **filled contour shapes** into SVGs with real **stroke paths**.

This is useful when you need to:

- edit stroke width in Figma after import,
- keep icon proportions and layout unchanged,
- preserve original geometry with high overlap accuracy.

## Core Benefits

- Converts filled outline shapes into editable stroke paths.
- Preserves `width`, `height`, and `viewBox`.
- Produces stroke-only vectors (`fill="none"` + `stroke` + `stroke-width`).
- Auto-selects stroke width by geometry overlap (IoU-based fit).
- Supports targeted tuning for hard icons with compound paths and tiny details.

## Typical Workflow

1. Run converter on source SVG.
2. Validate output canvas attributes (`width`, `height`, `viewBox`).
3. Ensure vectors are stroke-based and editable.
4. If visual artifacts remain, tune extraction parameters.

## Installation

Install dependencies in your Python environment:

```bash
python3 -m pip install svgpathtools shapely centerline
```

## Usage

Convert one SVG:

```bash
python3 scripts/convert_svg_to_strokes.py /absolute/path/icon.svg
```

Default output:

```text
/absolute/path/icon_stroke_paths_refined.svg
```

### Common Commands

Force custom output path:

```bash
python3 scripts/convert_svg_to_strokes.py /abs/in.svg -o /abs/out.svg
```

Force one stroke color:

```bash
python3 scripts/convert_svg_to_strokes.py /abs/in.svg --stroke-color "#6D7881"
```

Force stroke width (skip auto-fit):

```bash
python3 scripts/convert_svg_to_strokes.py /abs/in.svg --stroke-width 1.65
```

## Output Contract

A successful conversion should:

- keep original `width`, `height`, `viewBox`,
- output stroke-based paths suitable for Figma editing,
- print summary metrics:
  - output file path,
  - stroke line count,
  - geometry overlap score (IoU).

For many 64x64 icon sets, IoU around `0.95+` is expected.

## Tuning Guidance

If details are missing or corners look off, tune parameters documented in:

- `references/tuning.md`

Common levers:

- sampling step,
- centerline interpolation distance,
- spur pruning threshold,
- simplification/smoothing aggressiveness,
- stroke width candidate set.

## Repository Structure

```text
rstroke-conversion/
├── SKILL.md
├── scripts/
│   └── convert_svg_to_strokes.py
└── references/
    └── tuning.md
```

## Limitations

- Very complex compound paths may need targeted parameter tuning.
- Decorative micro-shapes can require relaxed pruning to preserve detail.
- Some icon families may need custom stroke width ranges.

## License

Add your project license here (for example, MIT).
