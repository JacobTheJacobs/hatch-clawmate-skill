# hatch-clawmate-skill

[![License: Apache-2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](./LICENSE.txt)
[![Branch: master](https://img.shields.io/badge/branch-master-black.svg)](../../tree/master)
[![Skill: hatch-pet](https://img.shields.io/badge/codex-skill-green.svg)](./SKILL.md)

Clean Git-backed source for the `hatch-pet` / `hatch-clawmate` Codex skill.

## Behavior

- Normal pet generation uses Codex-auth Image Gen first.
- Grounded row jobs use Codex-auth paths that can attach the listed input images.
- `OPENAI_API_KEY` is optional and is only used for the external OpenAI Images API fallback.
- Normal Codex runs must not ask the user for `OPENAI_API_KEY`.

## Repository Layout

- `SKILL.md`: skill contract and operating rules
- `scripts/`: deterministic prep, ingest, QA, packaging, and fallback orchestration
- `references/`: animation row definitions, QA rubric, and contract docs
- `agents/`: bundled agent config

## Install

Use this repository as the single source of truth, then install local skill entries as junctions or symlinks that point back to the repo.

### PowerShell install

```powershell
git clone git@github.com:JacobTheJacobs/hatch-clawmate-skill.git `
  "$HOME\Documents\Playground\hatch-clawmate-skill-clean"

$repo = "$HOME\Documents\Playground\hatch-clawmate-skill-clean"
$targets = @(
  "$HOME\.agents\skills\hatch-clawmate",
  "$HOME\.agents\skills\hatch-pet",
  "$HOME\.codex\skills\hatch-clawmate",
  "$HOME\.codex\skills\hatch-pet"
)

foreach ($target in $targets) {
  if (Test-Path -LiteralPath $target) {
    Remove-Item -LiteralPath $target -Recurse -Force
  }
  New-Item -ItemType Junction -Path $target -Target $repo | Out-Null
}
```

### Verify install

```powershell
Get-ChildItem "$HOME\.agents\skills","$HOME\.codex\skills" |
  Where-Object { $_.Name -match "hatch|clawmate" } |
  Select-Object Name, LinkType, Target
```

Expected result: both `hatch-pet` and `hatch-clawmate` resolve to the same repository path.

## Update

Pull the repo, then keep the existing junction installs in place:

```powershell
git -C "$HOME\Documents\Playground\hatch-clawmate-skill-clean" pull --ff-only
```

If you previously installed loose copies instead of links, remove them and rerun the install block above.

## Usage Notes

- Sequential runs are supported when the user explicitly says not to use subagents.
- Row jobs must not be prompt-only; they must use the `input_images` listed in `imagegen-jobs.json`.
- `scripts/generate_pet_images.py` prefers Codex-auth generation and only uses the external Images API if the Codex-auth paths fail and `OPENAI_API_KEY` exists.

## License

Licensed under [Apache-2.0](./LICENSE.txt).
