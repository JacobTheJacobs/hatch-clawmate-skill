# hatch-clawmate-skill

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE.txt)
[![Codex Skill](https://img.shields.io/badge/codex-skill-hatch--clawmate-green.svg)](./SKILL.md)
[![GitHub Repo](https://img.shields.io/badge/github-JacobTheJacobs%2Fhatch--clawmate--skill-black.svg)](https://github.com/JacobTheJacobs/hatch-clawmate-skill)

Official source repository for the `hatch-clawmate` Codex skill.

## Behavior

- Normal clawmate generation uses Codex-auth Image Gen first.
- Grounded row jobs use Codex-auth paths that can attach the listed input images.
- `OPENAI_API_KEY` is optional and is only used for the external OpenAI Images API fallback.
- Normal Codex runs must not ask the user for `OPENAI_API_KEY`.

## Repository Layout

- `SKILL.md`: skill contract and operating rules
- `scripts/`: deterministic prep, ingest, QA, packaging, and fallback orchestration
- `references/`: animation row definitions, QA rubric, and contract docs
- `agents/`: bundled agent config

## Install

```powershell
git clone git@github.com:JacobTheJacobs/hatch-clawmate-skill.git `
  "$HOME\Documents\Playground\hatch-clawmate-skill-clean"

$repo = "$HOME\Documents\Playground\hatch-clawmate-skill-clean"
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { "$HOME\.codex" }

$targets = @(
  "$HOME\.agents\skills\hatch-clawmate",
  "$codexHome\skills\hatch-clawmate"
)

foreach ($target in $targets) {
  if (Test-Path -LiteralPath $target) {
    Remove-Item -LiteralPath $target -Recurse -Force
  }
  New-Item -ItemType Junction -Path $target -Target $repo | Out-Null
}
```

## Update

```powershell
git -C "$HOME\Documents\Playground\hatch-clawmate-skill-clean" pull --ff-only
```

## License

Licensed under [MIT](./LICENSE.txt).
