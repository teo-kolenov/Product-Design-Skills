# token-health-analysis

Reusable AI skill to generate an HTML token strategy analysis and health report from:

1. Figma design URL.
2. JSON token file.
3. Plain text token files.

This skill is written with model-neutral command syntax so it can be used with Claude Code, OpenAI Codex, and GitHub Copilot style workflows.

## What It Generates

A single dashboard HTML file (default `token-strategy-dashboard.html`) containing:

1. Token health metrics.
2. Naming and semantic checks.
3. Reuse and scalability panels.
4. Semantic duplicate evidence.
5. Direct CSS override evidence.
6. Token inventory.

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

## Examples

```text
/token-health-analysis FIGMA https://www.figma.com/design/hSgrh1izjHNg45OBD37Z7j/General-style-guide-KEENETIC?node-id=9307-4709
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
