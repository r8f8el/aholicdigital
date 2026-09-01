---
name: superdesign
description: "Design or redesign frontend UI, presentations, and graphics on the Superdesign canvas with a choice of leading AI models. Use whenever the user wants to design a page, feature, flow, slide deck, or brand-new product; improve or reproduce existing UI; compare design results across top models; explore visual variants; set or extract a design system; build reusable components or multi-page flows; create presentations; or create posters and marketing graphics, even if they never say the word 'design tool'. Also supports generating supporting image or video assets when a design needs them."
---

# Superdesign

Superdesign helps you find design inspiration and generate or iterate design drafts on an infinite canvas, with multiple leading models available for different design tasks and side-by-side exploration. When a design needs a new visual asset, it can also provide image and video generation.

## CLI Usage

Superdesign runs entirely through its CLI: `npx --yes @superdesign/cli@latest [command]`

### Main Commands:
- `get-design --draft-id <draftId> [--output <path>]` — Fetch HTML content for a specific draft.
- `fetch-design-nodes --project-id <projectId>` — Get all design draft nodes for a project.
- `create-project --title <title>` — Create a new SuperDesign project.
- `iterate-design-draft --draft-id <id> -p "<prompt>" --mode replace|branch` — Iterate on an existing draft.
- `extract-website --url <url>` — Extract a website's design DNA.
- `import-design-draft --project-id <id> --title <title> --html-file <file>` — Import custom HTML into canvas.
