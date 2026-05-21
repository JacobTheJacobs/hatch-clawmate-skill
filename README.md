# hatch-clawmate-skill

Clean Git-backed source for the `hatch-pet` / `hatch-clawmate` Codex skill.

## Behavior

- Normal pet generation uses Codex-auth Image Gen first.
- Grounded row jobs should use Codex-auth paths that can attach the listed input images.
- `OPENAI_API_KEY` is optional and is only used for the external OpenAI Images API fallback.
- Normal Codex runs must not ask the user for `OPENAI_API_KEY`.

## Install

Install the skill from this repository as the single source of truth for local skill copies.
