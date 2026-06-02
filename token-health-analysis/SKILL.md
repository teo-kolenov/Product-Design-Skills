---
name: token-health-analysis
description: Generate a token strategy analysis and health report HTML from a Figma URL, token JSON, or plain text token files. Includes a HELP command and model-neutral command syntax.
argument-hint: "HELP | FIGMA <url> [OUTPUT <path>] | JSON <path> [OUTPUT <path>] | TEXT <path[,path...]> [OUTPUT <path>]"
---

# /token-health-analysis

Generate a reusable token strategy analysis dashboard as an HTML file.

## Goal

Produce a single HTML report with:

1. Token Architecture Health metrics.
2. Naming and semantic consistency checks.
3. Reuse and scalability insights.
4. Semantic duplicate evidence table.
5. Direct CSS color override evidence table.
6. Token inventory by collection/group/type/modes.

Default output file: `token-strategy-dashboard.html`

## Command Contract

Use the command in one of these forms:

```text
/token-health-analysis HELP
/token-health-analysis FIGMA <figma-url> [OUTPUT <path>]
/token-health-analysis JSON <path-to-json> [OUTPUT <path>]
/token-health-analysis TEXT <path1[,path2,...]> [OUTPUT <path>]
```

### HELP Behavior

If the user calls `HELP` (or `--help`), return usage instructions only and do not modify files.

Return this block:

```text
Token Health Analysis Skill

Usage:
  /token-health-analysis HELP
  /token-health-analysis FIGMA <figma-url> [OUTPUT <path>]
  /token-health-analysis JSON <path-to-json> [OUTPUT <path>]
  /token-health-analysis TEXT <path1[,path2,...]> [OUTPUT <path>]

Accepted inputs:
  - Figma file link (design URL)
  - JSON token file (preferred: schema in schema/token-health-input.schema.json)
  - Plain text files with tokens (CSS vars, key:value, key=value)

Output:
  - HTML dashboard file (default: token-strategy-dashboard.html)

Examples:
  /token-health-analysis FIGMA https://www.figma.com/design/<fileKey>/<name>?node-id=1-2
  /token-health-analysis JSON ./tokens.json OUTPUT ./reports/token-health.html
  /token-health-analysis TEXT ./tokens.txt,./styles.css
```

## Input Modes

### 1) FIGMA mode

Input: Figma design URL.

Preferred flow:

1. Extract `fileKey` and `node-id` from URL when present.
2. If a Figma connector is available, fetch token and component context from the file.
3. If connector is unavailable, request exported token JSON and continue via JSON mode.

### 2) JSON mode

Input: path to a JSON file.

1. Parse JSON directly if it matches the provided schema.
2. If schema differs, map fields into normalized structure (see Normalization Rules).

### 3) TEXT mode

Input: one or many text files (comma-separated).

Parse tokens using these patterns:

1. CSS variable: `--token-name: value;`
2. Key/value: `token.name: value`
3. Key/value: `token-name = value`
4. Optional mode suffixes in names or blocks: `light`, `dark`, `desktop`, `mobile`

## Normalization Rules

Normalize every discovered token to this shape:

```json
{
  "name": "color-brand-50",
  "value": "#007BBE",
  "collection": "Colors",
  "group": "global/brand",
  "type": "COLOR",
  "modes": ["Light", "Dark"],
  "description": ""
}
```

### Naming checks

Use this naming regex for compliance:

`^[a-z0-9]+(-[a-z0-9]+)+$`

### Duplicate semantics heuristics

Flag potential semantic duplicates when one of these is true:

1. Same value and same role semantics with different names.
2. Name segment order inversion (example: `color-primary-*` vs `primary-color-*`).
3. Equivalent role prefixes (`form-*`, `tertiary-*`, `link-*`) mapped to identical intent.

## Metrics Calculation

Compute at minimum:

1. Total tokens.
2. Global token violations (tokens that bypass base/global layer policy).
3. Alias layer coverage.
4. Orphaned aliases.
5. Average alias chain depth.
6. Naming pattern compliance percent.
7. Semantic duplicates count.
8. Direct CSS literal color overrides count.
9. Mode coverage by component where data exists.

If any metric lacks input data, show `N/A` and include assumptions in a note.

## HTML Output Requirements

Generate one self-contained HTML file with inline CSS and no build step.

Preferred base template:

`templates/token-strategy-dashboard.template.html`

Required sections:

1. Header (project/file metadata).
2. `Token Architecture Health` (metric cards).
3. `Naming & Semantic Consistency` (check rows).
4. `Reuse & Scalability` (reuse and mode coverage panels).
5. `Semantic Duplicates Detected` (table with pair, evidence, normalization target).
6. `Direct CSS Color Overrides` (table with literal values and replacements).
7. `Token Inventory - Variable Collections`.
8. Footer (source + generated date).

Use readable typography and color accents to improve scanability.

## Validation Checklist

Before finishing:

1. Verify output HTML is valid and opens without runtime errors.
2. Ensure all tables have headers and readable text contrast.
3. Ensure duplicate and override counts match listed rows.
4. Ensure output path exists and file is written.

## Model-Agnostic Rules

1. Keep command syntax plain text.
2. Avoid model-specific APIs when generic alternatives exist.
3. Prefer deterministic calculations over narrative-only analysis.
4. When connectors are missing, gracefully fallback to JSON/TEXT mode.
