---
name: rstroke-conversion
description: Convert filled SVG icon outlines into true centerline stroke paths so stroke width stays editable in Figma while preserving the original canvas, proportions, and close visual geometry. Use when a user asks to convert SVG icons from filled contour shapes to editable strokes, requests stroke-width-editable assets, or asks to apply the same stroke-conversion pattern to additional SVG files.
---

# Rstroke Conversion

Use this skill to transform icon-like SVG files (filled outline shapes) into stroke-editable SVG output.

## Workflow

1. Run the converter script on the source SVG.
2. Verify output keeps the same `width`, `height`, and `viewBox`.
3. Check that all output vectors are `fill="none"` and have `stroke` + `stroke-width`.
4. If visual bugs remain, tune parameters using [references/tuning.md](references/tuning.md).

## Quick Start

Install dependencies in your active Python environment:

```bash
python3 -m pip install svgpathtools shapely centerline
```

Convert one SVG:

```bash
python3 scripts/convert_svg_to_strokes.py /absolute/path/icon.svg
```

This writes:

- `/absolute/path/icon_stroke_paths_refined.svg`

## Common Commands

Force output path:

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

## Output Expectations

Expect the script to print:

- output file path
- number of stroke lines generated
- geometry overlap score (IoU)

For icon assets similar to this project, IoU near `0.95+` is typical.

## Resources

- `scripts/convert_svg_to_strokes.py`: Main converter implementation.
- [references/tuning.md](references/tuning.md): Parameter tuning guidance for edge cases.
