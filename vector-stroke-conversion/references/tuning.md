# Tuning Notes

Use these knobs when output looks off:

- `sample_step` in `path_to_fill_geom`:
  - Lower (e.g. `0.06`) to preserve tiny curvature details.
  - Higher (e.g. `0.12`) for faster conversion and simpler output.

- `interpolation_distance` in `centerline_lines_for_poly`:
  - Lower creates denser centerline extraction.
  - Higher creates fewer segments and can remove tiny artifacts.

- `poly.area >= 8.0` prune gate:
  - Increase if small details are being lost.
  - Decrease if small noisy branches remain.

- `length_threshold` in `prune_spurs`:
  - Increase to remove more dangling branches.
  - Decrease to preserve more detail.

- Width candidates (`candidates` list):
  - Expand range if the icon family is unusually thin or thick.
  - Keep values near `1.55-1.75` for standard 64x64 icon sets.

- `line.simplify(0.03)` and smoothing gate (`line.length > 2.0`):
  - Reduce simplify tolerance if corners flatten too much.
  - Increase smoothing gate if tiny dots deform.
