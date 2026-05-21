# hatch-clawmate-skill

[![License: Apache-2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](./LICENSE.txt)
[![Codex Skill](https://img.shields.io/badge/codex-skill-hatch--pet-green.svg)](./SKILL.md)
[![GitHub Repo](https://img.shields.io/badge/github-JacobTheJacobs%2Fhatch--clawmate--skill-black.svg)](https://github.com/JacobTheJacobs/hatch-clawmate-skill)
[![GitHub Stars](https://img.shields.io/github/stars/JacobTheJacobs/hatch-clawmate-skill?style=flat)](https://github.com/JacobTheJacobs/hatch-clawmate-skill/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/JacobTheJacobs/hatch-clawmate-skill?style=flat)](https://github.com/JacobTheJacobs/hatch-clawmate-skill/issues)
[![Last Commit](https://img.shields.io/github/last-commit/JacobTheJacobs/hatch-clawmate-skill?style=flat)](https://github.com/JacobTheJacobs/hatch-clawmate-skill/commits/master)

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

### Requirements

- Codex installed and logged in (`codex login`)
- Git installed
- On Windows: prefer junctions (no admin required)
- On macOS/Linux: prefer symlinks

### Choose an install location

Recommended repo location (matches the examples below):

- Windows: `%USERPROFILE%\Documents\Playground\hatch-clawmate-skill-clean`
- macOS/Linux: `~/Documents/Playground/hatch-clawmate-skill-clean`

If you keep repos elsewhere, just update `$repo` / `$REPO` in the commands.

### Agent install prompt

Copy and paste this into Codex or another local coding agent:

```text
Install the `hatch-clawmate-skill` repository as the single source of truth for the local `hatch-pet` / `hatch-clawmate` skill.

Repository:
- git@github.com:JacobTheJacobs/hatch-clawmate-skill.git

Target repo path:
- $HOME\Documents\Playground\hatch-clawmate-skill-clean

Install requirements:
- Clone or update the repo at the target path.
- Remove any old installed copies at:
  - $HOME\.agents\skills\hatch-clawmate
  - $HOME\.agents\skills\hatch-pet
  - $HOME\.codex\skills\hatch-clawmate
  - $HOME\.codex\skills\hatch-pet
- Reinstall only as junctions or symlinks pointing to the repo path.
- Verify that both names, `hatch-pet` and `hatch-clawmate`, resolve to the same repo in both `.agents\skills` and `.codex\skills`.

Behavior requirements:
- Normal pet generation uses Codex-auth Image Gen first.
- `OPENAI_API_KEY` is optional and only for the external OpenAI Images API fallback.
- Do not ask for `OPENAI_API_KEY` during normal Codex-auth runs.

After installation, report:
- the final repo path
- the git branch and commit
- the installed junction/symlink targets
```

### Windows (PowerShell)

This creates 4 junctions so both skill names resolve to the same repo in both Codex and Agents.

```powershell
git clone git@github.com:JacobTheJacobs/hatch-clawmate-skill.git `
  "$HOME\Documents\Playground\hatch-clawmate-skill-clean"

$repo = "$HOME\Documents\Playground\hatch-clawmate-skill-clean"
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { "$HOME\.codex" }
$targets = @("$HOME\.agents\skills", "$codexHome\skills")
$names = @("hatch-clawmate","hatch-pet")

foreach ($root in $targets) {
  foreach ($name in $names) {
    $target = Join-Path $root $name
    if (Test-Path -LiteralPath $target) {
      Remove-Item -LiteralPath $target -Recurse -Force
    }
    New-Item -ItemType Junction -Path $target -Target $repo | Out-Null
  }
}
```

### macOS/Linux (bash)

This creates 4 symlinks so both skill names resolve to the same repo in both Codex and Agents.

```bash
git clone git@github.com:JacobTheJacobs/hatch-clawmate-skill.git \
  "$HOME/Documents/Playground/hatch-clawmate-skill-clean"

REPO="$HOME/Documents/Playground/hatch-clawmate-skill-clean"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"

mkdir -p "$HOME/.agents/skills" "$CODEX_HOME/skills"

for root in "$HOME/.agents/skills" "$CODEX_HOME/skills"; do
  for name in hatch-clawmate hatch-pet; do
    rm -rf "$root/$name"
    ln -s "$REPO" "$root/$name"
  done
done
```

### Verify install (Windows PowerShell)

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { "$HOME\.codex" }
Get-ChildItem "$HOME\.agents\skills","$codexHome\skills" |
  Where-Object { $_.Name -match "hatch|clawmate" } |
  Select-Object Name, LinkType, Target
```

Expected result: both `hatch-pet` and `hatch-clawmate` resolve to the same repository path.

## Update

Pull the repo, then keep the existing junction installs in place:

```powershell
git -C "$HOME\Documents\Playground\hatch-clawmate-skill-clean" pull --ff-only
```

On macOS/Linux:

```bash
git -C "$HOME/Documents/Playground/hatch-clawmate-skill-clean" pull --ff-only
```

If you previously installed loose copies instead of links, remove them and rerun the install block above.

## Usage Notes

- Sequential runs are supported when the user explicitly says not to use subagents.
- Row jobs must not be prompt-only; they must use the `input_images` listed in `imagegen-jobs.json`.
- `scripts/generate_pet_images.py` prefers Codex-auth generation and only uses the external Images API if the Codex-auth paths fail and `OPENAI_API_KEY` exists.

## License

Licensed under [Apache-2.0](./LICENSE.txt).
