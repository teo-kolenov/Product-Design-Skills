#!/usr/bin/env python3
"""Convert filled SVG icon paths into stroke-editable centerline paths.

This script is designed for icon-style SVGs where thick outlines are encoded
as filled shapes. It extracts centerlines, preserves the canvas geometry, and
outputs stroke paths that are editable in Figma.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

from centerline.geometry import Centerline
from shapely.geometry import LineString, MultiLineString, Polygon
from shapely.ops import linemerge, unary_union
from svgpathtools import parse_path

Point = Tuple[float, float]


def signed_area(points: Sequence[Point]) -> float:
    area = 0.0
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        area += x1 * y2 - x2 * y1
    return area / 2.0


def parse_svg_root(svg_text: str) -> ET.Element:
    try:
        return ET.fromstring(svg_text)
    except ET.ParseError as exc:
        raise SystemExit(f"Invalid SVG: {exc}") from exc


def find_path_elements(svg_text: str) -> List[Tuple[str, str, str]]:
    # Returns (pre_attrs, d, post_attrs)
    return re.findall(r'<path([^>]*)d="([^"]+)"([^>]*)/?>', svg_text)


def attr_value(attrs: str, name: str) -> str | None:
    m = re.search(rf"\b{name}\s*=\s*\"([^\"]+)\"", attrs)
    if m:
        return m.group(1)
    m = re.search(rf"\b{name}\s*=\s*'([^']+)'", attrs)
    return m.group(1) if m else None


def path_to_fill_geom(d: str, evenodd: bool, sample_step: float = 0.08):
    subpaths = parse_path(d).continuous_subpaths()
    polys: List[Polygon] = []
    signs: List[int] = []
    areas: List[float] = []

    for sp in subpaths:
        pts: List[Point] = []
        for seg in sp:
            n = max(2, int(seg.length() / sample_step))
            for j in range(n):
                z = seg.point(j / n)
                pts.append((float(z.real), float(z.imag)))
        z_last = sp[-1].point(1)
        pts.append((float(z_last.real), float(z_last.imag)))
        if pts and pts[0] != pts[-1]:
            pts.append(pts[0])
        if len(pts) < 4:
            continue

        poly = Polygon(pts)
        if not poly.is_valid:
            poly = poly.buffer(0)
        if poly.is_empty:
            continue

        sa = signed_area(pts)
        polys.append(poly)
        signs.append(1 if sa > 0 else -1)
        areas.append(abs(sa))

    if not polys:
        return Polygon()

    if evenodd:
        geom = None
        for p in polys:
            geom = p if geom is None else geom.symmetric_difference(p)
        return geom

    # Approximate nonzero winding: largest ring defines outer direction.
    outer_sign = signs[max(range(len(areas)), key=lambda i: areas[i])]
    primary = [p for p, s in zip(polys, signs) if s == outer_sign]
    opposite = [p for p, s in zip(polys, signs) if s != outer_sign]

    geom = unary_union(primary)
    if opposite:
        geom = geom.difference(unary_union(opposite))
    return geom


def centerline_lines_for_poly(poly: Polygon, interpolation_distance: float = 0.18) -> List[LineString]:
    if poly.area < 0.02:
        return []
    try:
        cl = Centerline(poly, interpolation_distance=interpolation_distance).geometry
    except Exception:
        return []

    merged = linemerge(unary_union(cl))
    if merged.geom_type == "LineString":
        return [merged]
    if merged.geom_type == "MultiLineString":
        return list(merged.geoms)
    return []


def prune_spurs(lines: Iterable[LineString], length_threshold: float = 1.2, snap_decimals: int = 3) -> List[LineString]:
    current = [LineString(line.coords) for line in lines if line.length > 0.03]
    changed = True
    while changed:
        changed = False
        degree: dict[Tuple[float, float], int] = {}
        endpoints: List[Tuple[Tuple[float, float], Tuple[float, float]]] = []

        for line in current:
            a = line.coords[0]
            b = line.coords[-1]
            ka = (round(a[0], snap_decimals), round(a[1], snap_decimals))
            kb = (round(b[0], snap_decimals), round(b[1], snap_decimals))
            degree[ka] = degree.get(ka, 0) + 1
            degree[kb] = degree.get(kb, 0) + 1
            endpoints.append((ka, kb))

        kept: List[LineString] = []
        for line, (ka, kb) in zip(current, endpoints):
            is_leaf = (degree[ka] == 1) or (degree[kb] == 1)
            if is_leaf and line.length < length_threshold:
                changed = True
                continue
            kept.append(line)
        current = kept

    return current


def smooth_points(points: Sequence[Point], weight: float = 0.22, iterations: int = 1) -> List[Point]:
    pts = list(points)
    for _ in range(iterations):
        if len(pts) < 3:
            return pts
        out: List[Point] = [pts[0]]
        for i in range(len(pts) - 1):
            p0 = pts[i]
            p1 = pts[i + 1]
            q = ((1 - weight) * p0[0] + weight * p1[0], (1 - weight) * p0[1] + weight * p1[1])
            r = (weight * p0[0] + (1 - weight) * p1[0], weight * p0[1] + (1 - weight) * p1[1])
            out.extend([q, r])
        out.append(pts[-1])
        pts = out
    return pts


def fmt(v: float) -> str:
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return s if s else "0"


def line_to_svg_d(line: LineString) -> str:
    simp = line.simplify(0.03, preserve_topology=False)
    pts = list(simp.coords)
    if len(pts) < 2:
        pts = list(line.coords)

    if len(pts) >= 6 and line.length > 2.0:
        pts = smooth_points(pts, weight=0.22, iterations=1)

    if len(pts) >= 4 and line.length > 2.0:
        d = f"M{fmt(pts[0][0])} {fmt(pts[0][1])}"
        for i in range(1, len(pts) - 1):
            cx, cy = pts[i]
            nx, ny = pts[i + 1]
            mx, my = ((cx + nx) / 2.0, (cy + ny) / 2.0)
            d += f" Q{fmt(cx)} {fmt(cy)} {fmt(mx)} {fmt(my)}"
        d += f" T{fmt(pts[-1][0])} {fmt(pts[-1][1])}"
        return d

    d = f"M{fmt(pts[0][0])} {fmt(pts[0][1])}"
    for x, y in pts[1:]:
        d += f" L{fmt(x)} {fmt(y)}"
    return d


def default_output_path(input_svg: Path, suffix: str) -> Path:
    return input_svg.with_name(f"{input_svg.stem}{suffix}.svg")


def choose_stroke_width(ml: MultiLineString, orig_geom, candidates: Sequence[float]) -> Tuple[float, float]:
    best_w = candidates[0]
    best_iou = -1.0
    for w in candidates:
        stroked = ml.buffer(w / 2.0, cap_style=1, join_style=1, resolution=16)
        inter = stroked.intersection(orig_geom).area
        uni = stroked.union(orig_geom).area
        iou = inter / uni if uni else 0.0
        if iou > best_iou:
            best_iou = iou
            best_w = w
    return best_w, best_iou


def convert(input_svg: Path, output_svg: Path, stroke_color: str | None, stroke_width: float | None) -> Tuple[float, int]:
    svg_text = input_svg.read_text(encoding="utf-8")
    root = parse_svg_root(svg_text)
    width = root.get("width", "64")
    height = root.get("height", "64")
    view_box = root.get("viewBox", "0 0 64 64")

    path_matches = find_path_elements(svg_text)
    if not path_matches:
        raise SystemExit("No <path> elements found in input SVG.")

    orig_geom = None
    line_records: List[Tuple[LineString, str]] = []

    for pre, d, post in path_matches:
        attrs = pre + " " + post
        evenodd = ('fill-rule="evenodd"' in attrs) or ("fill-rule='evenodd'" in attrs)
        fill_geom = path_to_fill_geom(d, evenodd=evenodd, sample_step=0.08)
        if fill_geom.is_empty:
            continue

        path_color = stroke_color or attr_value(attrs, "fill") or "#6D7881"
        if path_color.lower() == "none":
            path_color = "#6D7881"

        orig_geom = fill_geom if orig_geom is None else unary_union([orig_geom, fill_geom])

        polys = [fill_geom] if fill_geom.geom_type == "Polygon" else list(getattr(fill_geom, "geoms", []))
        for poly in polys:
            raw = centerline_lines_for_poly(poly, interpolation_distance=0.18)
            if poly.area >= 8.0:
                raw = prune_spurs(raw, length_threshold=1.2, snap_decimals=3)
            for ln in raw:
                if ln.length >= 0.03:
                    line_records.append((ln, path_color))

    if not line_records:
        raise SystemExit("Centerline extraction produced no lines. Try a simpler icon SVG.")

    all_lines = [ln for ln, _ in line_records]
    ml = MultiLineString([list(line.coords) for line in all_lines])

    if stroke_width is None:
        candidates = [1.5, 1.55, 1.6, 1.65, 1.68, 1.7, 1.72, 1.75, 1.8]
        best_w, iou = choose_stroke_width(ml, orig_geom, candidates)
    else:
        best_w = stroke_width
        _, iou = choose_stroke_width(ml, orig_geom, [stroke_width])

    svg_out = ET.Element(
        "svg",
        {
            "xmlns": "http://www.w3.org/2000/svg",
            "width": str(width),
            "height": str(height),
            "viewBox": str(view_box),
            "fill": "none",
        },
    )

    for line, color in line_records:
        ET.SubElement(
            svg_out,
            "path",
            {
                "d": line_to_svg_d(line),
                "fill": "none",
                "stroke": color,
                "stroke-width": f"{best_w:.5f}",
                "stroke-linecap": "round",
                "stroke-linejoin": "round",
            },
        )

    ET.ElementTree(svg_out).write(str(output_svg), encoding="utf-8", xml_declaration=False)
    return iou, len(line_records)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert filled SVG icon paths into stroke-editable centerline paths for Figma."
    )
    parser.add_argument("input_svg", type=Path, help="Path to source SVG")
    parser.add_argument("-o", "--output", type=Path, help="Path to output SVG")
    parser.add_argument(
        "--suffix",
        default="_stroke_paths_refined",
        help="Suffix for output filename when --output is not provided",
    )
    parser.add_argument("--stroke-color", help="Force one stroke color (default: preserve per-path fill color)")
    parser.add_argument("--stroke-width", type=float, help="Force stroke width (default: auto-fit)")

    args = parser.parse_args()

    input_svg = args.input_svg.expanduser().resolve()
    if not input_svg.exists():
        raise SystemExit(f"Input SVG not found: {input_svg}")

    output_svg = args.output.expanduser().resolve() if args.output else default_output_path(input_svg, args.suffix)

    iou, line_count = convert(
        input_svg=input_svg,
        output_svg=output_svg,
        stroke_color=args.stroke_color,
        stroke_width=args.stroke_width,
    )

    print(f"[OK] Wrote: {output_svg}")
    print(f"[OK] Stroke lines: {line_count}")
    print(f"[OK] Geometry overlap (IoU): {iou:.4f}")


if __name__ == "__main__":
    main()
