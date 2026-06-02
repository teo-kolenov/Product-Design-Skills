# token-health-analysis

Reusable AI skill to generate an HTML token strategy analysis and health report from:

1. Figma design URL.
2. JSON token file.
3. Plain text token files.

This skill uses model-neutral command syntax and a shared HTML template so it can be used with Claude Code, OpenAI Codex, and GitHub Copilot style workflows.

## What It Generates

A single dashboard HTML file (default `token-strategy-dashboard.html`) containing:

1. Header with source metadata and generated date.
2. Overall health score ring.
3. Token architecture health metric cards.
4. Naming and semantic consistency checks.
5. Reuse and scalability panels with charts.
6. Semantic duplicate evidence table.
7. Direct CSS color override evidence table.
8. Token inventory by collection/group/type/modes.
9. Footer note.

Design highlights in the current template:

1. Color-accented status system (ok/warn/fail).
2. White card backgrounds for check cards and metric cards.
3. Ring chart + horizontal bars for scannable metrics.
4. Duplicate-pair cards with A/B color accents.

## HELP Command

Use:

```text
/token-health-analysis HELP
```

Expected behavior:

1. Return usage instructions.
2. Do not edit files.

## Command Syntax

```text
/token-health-analysis HELP
/token-health-analysis FIGMA <figma-url> [OUTPUT <path>]
/token-health-analysis JSON <path-to-json> [OUTPUT <path>]
/token-health-analysis TEXT <path1[,path2,...]> [OUTPUT <path>]
```

## Template Contract

The skill fills placeholders in:

`templates/token-strategy-dashboard.template.html`

Core placeholders include:

1. `{{reportTitle}}`, `{{reportSubtitle}}`, `{{sourceLabel}}`, `{{generatedDate}}`, `{{headerBadges}}`
2. `{{healthScorePercent}}`, `{{healthScoreLabel}}`, `{{healthScoreColor}}`, `{{healthRingStats}}`
3. `{{metricCards}}`, `{{consistencyChecks}}`
4. `{{reuseBarRows}}`, `{{reuseNote}}`, `{{modeCoverageRows}}`, `{{modeCoverageNote}}`
5. `{{semanticDuplicateRows}}`, `{{semanticDuplicatesCount}}`
6. `{{directOverrideRows}}`, `{{directOverridesCount}}`
7. `{{inventoryRows}}`, `{{footerText}}`

Note: The complete placeholder reference with exact HTML snippets is documented at the top of the template file.

## Health Score

The recommended score formula in the skill:

```text
healthScore = round(
    (aliasLayerCoverage * 0.35) +
    (namingPatternCompliance * 0.25) +
    (modeCoverage * 0.20) +
    (100 - min(semanticDuplicates / totalTokens * 100, 100)) * 0.20
)
```

Color thresholds:

1. `>= 80` -> `var(--c-ok-60)`
2. `>= 60` -> `var(--c-warn-40)`
3. `< 60` -> `var(--c-danger-50)`

## Examples

```text
/token-health-analysis FIGMA: https://www.figma.com/design/hSguih2ix
```

```text
/token-health-analysis JSON ./token-health-analysis/examples/sample-token-input.json OUTPUT ./token-strategy-dashboard.html
```

```text
/token-health-analysis TEXT ./tokens.txt,./styles.css OUTPUT ./reports/token-health.html
```

## Input Notes

1. Figma mode: use connector/tooling if available; otherwise export to JSON and continue with JSON mode.
2. JSON mode: preferred format is in `schema/token-health-input.schema.json`.
3. TEXT mode: supports CSS vars, `key:value`, and `key=value` token lines.

## Output Rules

1. Generate one self-contained HTML file with inline CSS.
2. Keep all required sections in the template output.
3. Keep table headers and status colors readable.
4. Ensure duplicate/override totals match rendered rows.
5. Write to default output (`token-strategy-dashboard.html`) unless `OUTPUT` is provided.

## Package Structure

```text
token-health-analysis/
├── SKILL.md
├── README.md
├── agents/
│   ├── claude.yaml
│   ├── copilot.yaml
│   └── openai.yaml
├── templates/
│   └── token-strategy-dashboard.template.html
├── schema/
│   └── token-health-input.schema.json
└── examples/
    ├── prompt-examples.md
    └── sample-token-input.json
```

## Compatibility

This skill intentionally avoids model-specific command syntax. It should be portable as long as the host agent can:

1. Read files.
2. Parse text/JSON.
3. Write an HTML output file.

Optional enhancements (when available):

1. Figma connector for direct extraction.
2. Repository search for CSS literal color override detection.
