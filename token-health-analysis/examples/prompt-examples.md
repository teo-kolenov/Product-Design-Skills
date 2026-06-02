# Prompt Examples

These examples are intentionally plain so they can be used in Claude Code, OpenAI Codex, and GitHub Copilot style chats.

## 1) Show help

```text
/token-health-analysis HELP
```

## 2) Analyze from Figma URL

```text
/token-health-analysis FIGMA https://www.figma.com/design/hSgrh1izjHNg45OBD37Z7j/General-style-guide-KEENETIC?node-id=9307-4709 OUTPUT ./token-strategy-dashboard.html
```

## 3) Analyze from JSON

```text
/token-health-analysis JSON ./token-health-analysis/examples/sample-token-input.json OUTPUT ./token-strategy-dashboard.html
```

## 4) Analyze from text files

```text
/token-health-analysis TEXT ./DESIGN.md,./token-notes.txt OUTPUT ./token-strategy-dashboard.html
```

## 5) Request only usage guidance

```text
Use token-health-analysis HELP and explain each argument with one short example.
```
