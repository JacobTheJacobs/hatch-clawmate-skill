#!/usr/bin/env python3
"""Secondary image generation fallback for Codex pet base art and row strips."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ALL_STATES = [
    "idle",
    "running-right",
    "running-left",
    "waving",
    "jumping",
    "failed",
    "waiting",
    "running",
    "review",
    "coding",
    "communicating",
    "monitoring",
    "read-file",
    "syncing",
    "system",
    "run-tool",
    "reaction",
    "web-fetch",
    "web-search",
    "working",
    "vibe",
    "write-to-file",
]
CANONICAL_BASE_PATH = "references/canonical-base.png"


def parse_states(raw: str) -> list[str]:
    if raw.strip().lower() == "all":
        return ALL_STATES
    states = [item.strip() for item in raw.split(",") if item.strip()]
    unknown = sorted(set(states) - set(ALL_STATES))
    if unknown:
        raise SystemExit(f"unknown state(s): {', '.join(unknown)}")
    return states


def load_manifest(run_dir: Path) -> dict[str, object]:
    path = run_dir / "imagegen-jobs.json"
    if not path.exists():
        raise SystemExit(f"job manifest not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def manifest_jobs(manifest: dict[str, object]) -> list[dict[str, object]]:
    jobs = manifest.get("jobs")
    if not isinstance(jobs, list):
        raise SystemExit("invalid imagegen-jobs.json: jobs must be a list")
    return [job for job in jobs if isinstance(job, dict)]


def resolve_run_path(run_dir: Path, raw: str) -> Path:
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = run_dir / path
    return path.resolve()


def select_jobs(
    manifest: dict[str, object],
    *,
    states: list[str],
    skip_base: bool,
    job_ids: list[str],
) -> list[dict[str, object]]:
    selected_ids = set(job_ids)
    if not selected_ids:
        if not skip_base:
            selected_ids.add("base")
        selected_ids.update(states)
    selected = [job for job in manifest_jobs(manifest) if job.get("id") in selected_ids]
    missing = selected_ids - {str(job.get("id")) for job in selected}
    if missing:
        raise SystemExit(f"unknown job id(s): {', '.join(sorted(missing))}")
    return selected


def run_image_edit(
    *,
    model: str,
    prompt_file: Path,
    image_paths: list[Path],
    output_json: Path,
    size: str,
    api_key: str,
) -> dict[str, object]:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "curl",
        "-sS",
        "-X",
        "POST",
        "https://api.openai.com/v1/images/edits",
        "-H",
        f"Authorization: Bearer {api_key}",
        "-F",
        f"model={model}",
    ]
    for image_path in image_paths:
        command.extend(["-F", f"image[]=@{image_path}"])
    command.extend(
        [
            "-F",
            f"prompt=<{prompt_file}",
            "-F",
            f"size={size}",
            "-F",
            "output_format=png",
            "-o",
            str(output_json),
        ]
    )
    subprocess.run(command, check=True)
    response = json.loads(output_json.read_text(encoding="utf-8"))
    if response.get("error"):
        raise SystemExit(json.dumps(response["error"], indent=2))
    return response


def run_image_generation(
    *,
    model: str,
    prompt_file: Path,
    output_json: Path,
    size: str,
    api_key: str,
) -> dict[str, object]:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "curl",
        "-sS",
        "-X",
        "POST",
        "https://api.openai.com/v1/images/generations",
        "-H",
        f"Authorization: Bearer {api_key}",
        "-F",
        f"model={model}",
        "-F",
        f"prompt=<{prompt_file}",
        "-F",
        f"size={size}",
        "-F",
        "output_format=png",
        "-o",
        str(output_json),
    ]
    subprocess.run(command, check=True)
    response = json.loads(output_json.read_text(encoding="utf-8"))
    if response.get("error"):
        raise SystemExit(json.dumps(response["error"], indent=2))
    return response


def decode_response(response: dict[str, object], output_image: Path) -> None:
    data = response.get("data")
    if not isinstance(data, list) or not data:
        raise SystemExit("image API response did not contain data[0]")
    first = data[0]
    if not isinstance(first, dict) or not isinstance(first.get("b64_json"), str):
        raise SystemExit("image API response did not contain data[0].b64_json")
    output_image.parent.mkdir(parents=True, exist_ok=True)
    output_image.write_bytes(base64.b64decode(first["b64_json"]))


def latest_generated_image() -> Path | None:
    root = Path.home() / ".codex" / "generated_images"
    if not root.exists():
        return None
    images = list(root.rglob("ig_*.png"))
    if not images:
        return None
    return max(images, key=lambda p: p.stat().st_mtime)


def compact_codex_imagegen_prompt(spec_text: str, prompt_file: Path) -> str:
    state = prompt_file.stem
    visual_state = {
        "system": "process-attention",
        "run-tool": "tool-use",
        "web-fetch": "retrieval",
        "web-search": "searching",
        "write-to-file": "saving",
        "read-file": "reading",
        "vibe": "personality-flourish",
    }.get(state, state)
    frame_match = re.search(r"Output exactly\s+(\d+)\s+separate animation frames", spec_text)
    frames = frame_match.group(1) if frame_match else "the requested number of"
    action_match = re.search(r"Animation action:\s*(.+?)(?:\n\n|\Z)", spec_text, re.S)
    action = " ".join(action_match.group(1).split()) if action_match else state.replace("-", " ")
    action = (
        action.replace("system-state", "process")
        .replace("run-tool", "tool-use")
        .replace("web-fetch", "retrieval")
        .replace("web-search", "search")
        .replace("write-to-file", "saving")
        .replace("read-file", "reading")
        .replace("never smoking", "no detached smoke effects")
        .replace("smoking", "smoke effects")
    )

    return (
        "Use the built-in image generation tool (`image_gen`) to generate EXACTLY ONE image.\n"
        "Create a single horizontal sprite strip for a Codex digital pet.\n"
        f"Animation label: {visual_state}. Frames: exactly {frames}, arranged left-to-right in one row.\n"
        f"Action: {action}.\n"
        "Use the attached layout guide only for frame count, spacing, centering, and safe padding.\n"
        "Use the attached base/canonical image as the exact identity reference.\n"
        "Generate a wide horizontal strip, not a square character sheet. Spread poses across the full width. "
        "The first and last frame slots must each contain a complete visible pet pose.\n"
        "Pet identity: tiny cute bat-hero mascot, black cowl with short ears, black cape, "
        "gray suit, yellow belt, big friendly eyes, chibi proportions.\n"
        "Style: pixel-art-adjacent Codex pet sprite, thick dark outline, flat cel shading, "
        "limited palette, crisp readable silhouette, tiny limbs.\n"
        "Background: perfectly flat pure magenta #FF00FF chroma-key across the whole strip.\n"
        "Rules: no text, labels, visible grids, guide marks, scenery, shadows, glows, blur, "
        "motion trails, detached effects, or extra props. Do not copy visible guide lines. "
        "Each frame must contain one complete full-body pose and preserve the same identity.\n"
        "Do not answer in text. Produce only the generated image.\n"
    )


def full_codex_imagegen_prompt(spec_text: str) -> str:
    return (
        "Use the built-in image generation tool (`image_gen`) to generate EXACTLY ONE image.\n"
        "Do not run shell commands. Do not write files. Do not browse the web.\n"
        "Do not output explanations; your only goal is to produce one generated image.\n"
        "Follow the specification below exactly.\n\n"
        "=== SPEC START ===\n"
        f"{spec_text}\n"
        "=== SPEC END ===\n"
    )


def run_codex_imagegen(
    *,
    run_dir: Path,
    prompt_file: Path,
    image_paths: list[Path],
    newest_only_after: float,
) -> Path:
    """
    Generate one image using Codex-auth image generation.

    Fallback order:
      1) Codex session auth (normal `codex exec`).
      2) Codex session auth with bypass flags (`--dangerously-bypass-approvals-and-sandbox`).

    External OpenAI Images API is *not* used here; see the main loop fallback logic.
    """

    def _run_codex_exec(extra_flags: list[str], prompt_variants: list[str]) -> Path:
        codex_executable = (
            os.environ.get("CODEX_EXECUTABLE")
            or shutil.which("codex.cmd")
            or shutil.which("codex.exe")
            or shutil.which("codex")
            or "codex"
        )
        before = latest_generated_image()
        spec_text = prompt_file.read_text(encoding="utf-8").strip()
        compact_instruction = compact_codex_imagegen_prompt(spec_text, prompt_file)
        command = [
            codex_executable,
            "exec",
            "--skip-git-repo-check",
            "--color",
            "never",
            "-C",
            str(run_dir),
            *extra_flags,
        ]
        for image_path in image_paths:
            command.extend(["--image", str(image_path)])

        last_stdout = ""
        last_stderr = ""
        for prompt_text in prompt_variants:
            result = subprocess.run(
                command,
                input=prompt_text,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )
            last_stdout = (result.stdout or "").rstrip()
            last_stderr = (result.stderr or "").rstrip()
            if result.returncode != 0:
                print("codex exec failed")
                print("command:", subprocess.list2cmdline(command))
                if last_stderr:
                    print("stderr:")
                    print(last_stderr)
                if last_stdout:
                    print("stdout:")
                    print(last_stdout)
                raise RuntimeError(f"codex exec exit code {result.returncode}")

            generated_root = Path.home() / ".codex" / "generated_images"
            candidates = [
                path
                for path in generated_root.rglob("ig_*.png")
                if path.is_file() and path.stat().st_mtime >= newest_only_after
            ]
            if before is not None:
                candidates = [path for path in candidates if path != before]
            if candidates:
                return max(candidates, key=lambda path: path.stat().st_mtime)

        raise RuntimeError(
            "codex image_gen did not produce a new ig_*.png output "
            f"after retries. stdout={last_stdout!r} stderr={last_stderr!r}"
        )

    # 1) Normal Codex-auth path first.
    try:
        spec_text = prompt_file.read_text(encoding="utf-8").strip()
        first_prompts = [compact_codex_imagegen_prompt(spec_text, prompt_file)]
        if prompt_file.stem in {"running-right", "running-left"}:
            first_prompts = [full_codex_imagegen_prompt(spec_text), *first_prompts]
        return _run_codex_exec(
            [
                "--ignore-user-config",
                "--ignore-rules",
            ],
            first_prompts,
        )
    except Exception as first_error:  # noqa: BLE001
        # 2) Retry with normal user config and the full prompt, then compact prompt.
        try:
            spec_text = prompt_file.read_text(encoding="utf-8").strip()
            full_prompt = full_codex_imagegen_prompt(spec_text)
            compact_prompt = compact_codex_imagegen_prompt(spec_text, prompt_file)
            return _run_codex_exec(
                [],
                [
                    full_prompt,
                    "IMPORTANT: You MUST call `image_gen` now. Do not answer in text.\n\n"
                    + compact_prompt,
                    compact_prompt,
                ],
            )
        except Exception as second_error:  # noqa: BLE001
            # 3) Last Codex-auth retry with bypass flags.
            try:
                return _run_codex_exec(
                    [
                        "--dangerously-bypass-approvals-and-sandbox",
                        "--ignore-user-config",
                        "--ignore-rules",
                    ],
                    [compact_codex_imagegen_prompt(prompt_file.read_text(encoding="utf-8").strip(), prompt_file)],
                )
            except Exception as third_error:  # noqa: BLE001
                raise RuntimeError(
                    f"Codex-auth image generation failed (isolated + normal + bypass). "
                    f"isolated_error={first_error!s}; normal_error={second_error!s}; "
                    f"bypass_error={third_error!s}"
                ) from third_error


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def complete_job(job: dict[str, object], output_path: Path) -> None:
    job["status"] = "complete"
    job["source_path"] = str(output_path)
    job["source_provenance"] = "secondary-fallback-codex-exec"
    job["source_sha256"] = file_sha256(output_path)
    job["output_sha256"] = file_sha256(output_path)
    job["completed_at"] = datetime.now(timezone.utc).isoformat()
    job["secondary_fallback"] = True
    for key in [
        "last_error",
        "synthetic_test_source",
        "derived_from",
        "mirror_decision",
        "repair_reason",
        "queued_at",
    ]:
        job.pop(key, None)


def write_canonical_base(
    run_dir: Path, manifest: dict[str, object], output_image: Path
) -> None:
    canonical = run_dir / CANONICAL_BASE_PATH
    canonical.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(output_image, canonical)
    reference = {
        "path": CANONICAL_BASE_PATH,
        "source_job": "base",
        "sha256": file_sha256(canonical),
    }
    manifest["canonical_identity_reference"] = reference
    request_path = run_dir / "pet_request.json"
    if request_path.exists():
        request = json.loads(request_path.read_text(encoding="utf-8"))
        request["canonical_identity_reference"] = reference
        request_path.write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")


def path_list(run_dir: Path, job: dict[str, object]) -> list[Path]:
    inputs = job.get("input_images")
    if not isinstance(inputs, list):
        raise SystemExit(f"job {job.get('id')} has invalid input_images")
    paths = []
    for item in inputs:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise SystemExit(f"job {job.get('id')} has invalid input image entry")
        path = resolve_run_path(run_dir, item["path"])
        if not path.is_file():
            raise SystemExit(f"input image for job {job.get('id')} not found: {path}")
        paths.append(path)
    return paths


def ready_pending_jobs(
    manifest: dict[str, object], selected_ids: set[str] | None = None
) -> list[dict[str, object]]:
    completed = {
        str(job.get("id"))
        for job in manifest_jobs(manifest)
        if job.get("status") == "complete" and isinstance(job.get("id"), str)
    }
    ready = []
    for job in manifest_jobs(manifest):
        job_id = job.get("id")
        if not isinstance(job_id, str):
            continue
        if selected_ids is not None and job_id not in selected_ids:
            continue
        if job.get("status") != "pending":
            continue
        deps = [dep for dep in job.get("depends_on", []) if isinstance(dep, str)]
        if all(dep in completed for dep in deps):
            ready.append(job)
    return ready


def has_incomplete_selected_jobs(
    manifest: dict[str, object], selected_ids: set[str] | None = None
) -> bool:
    for job in manifest_jobs(manifest):
        job_id = job.get("id")
        if not isinstance(job_id, str):
            continue
        if selected_ids is not None and job_id not in selected_ids:
            continue
        if job.get("status") != "complete":
            return True
    return False


def has_incomplete_jobs(manifest: dict[str, object]) -> bool:
    return has_incomplete_selected_jobs(manifest, None)


def record_job_result(run_dir: Path, job_id: str, source: Path) -> None:
    scripts_dir = Path(__file__).resolve().parent
    command = [
        sys.executable,
        str(scripts_dir / "record_imagegen_result.py"),
        "--run-dir",
        str(run_dir),
        "--job-id",
        job_id,
        "--source",
        str(source),
        "--force",
    ]
    subprocess.run(command, check=True, text=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--model", default="gpt-image-2")
    parser.add_argument("--size", default="1024x1024")
    parser.add_argument("--states", default="all")
    parser.add_argument("--job-id", action="append", default=[])
    parser.add_argument("--skip-base", action="store_true")
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")

    run_dir = Path(args.run_dir).expanduser().resolve()
    manifest_path = run_dir / "imagegen-jobs.json"
    manifest = load_manifest(run_dir)
    selected_jobs = select_jobs(
        manifest,
        states=parse_states(args.states),
        skip_base=args.skip_base,
        job_ids=args.job_id,
    )
    selected_ids = {str(job.get("id")) for job in selected_jobs if isinstance(job.get("id"), str)}
    raw_dir = run_dir / "raw"

    completed = []
    while True:
        manifest = load_manifest(run_dir)
        ready_jobs = ready_pending_jobs(manifest, selected_ids)
        if not ready_jobs:
            break
        for job in ready_jobs:
            job_id = str(job.get("id"))
            prompt_raw = job.get("prompt_file")
            output_raw = job.get("output_path")
            if not isinstance(prompt_raw, str) or not isinstance(output_raw, str):
                raise SystemExit(f"job {job_id} is missing prompt_file or output_path")
            prompt_file = resolve_run_path(run_dir, prompt_raw)
            output_image = resolve_run_path(run_dir, output_raw)
            print(f"Generating {job_id} with Codex-auth $imagegen")
            image_paths = path_list(run_dir, job)
            started_at = datetime.now(timezone.utc).timestamp()
            try:
                source_image = run_codex_imagegen(
                    run_dir=run_dir,
                    prompt_file=prompt_file,
                    image_paths=image_paths,
                    newest_only_after=started_at,
                )
                record_job_result(run_dir, job_id, source_image)
                completed.append(
                    {"job_id": job_id, "output": str(output_image), "source": str(source_image)}
                )
                continue
            except Exception as codex_error:  # noqa: BLE001
                if not api_key:
                    raise SystemExit(
                        f"Codex-auth image generation failed for {job_id}; "
                        f"OPENAI_API_KEY not set so external API fallback is unavailable. "
                        f"error={codex_error!s}"
                    ) from codex_error

                print(
                    f"Codex-auth generation failed for {job_id}; falling back to external Images API"
                )
                if image_paths:
                    response = run_image_edit(
                        model=args.model,
                        prompt_file=prompt_file,
                        image_paths=image_paths,
                        output_json=raw_dir / f"{job_id}.response.json",
                        size=args.size,
                        api_key=api_key,
                    )
                else:
                    response = run_image_generation(
                        model=args.model,
                        prompt_file=prompt_file,
                        output_json=raw_dir / f"{job_id}.response.json",
                        size=args.size,
                        api_key=api_key,
                    )
                decode_response(response, output_image)
                complete_job(job, output_image)
                if job_id == "base":
                    job["canonical_reference_path"] = CANONICAL_BASE_PATH
                    write_canonical_base(run_dir, manifest, output_image)
                manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
                completed.append({"job_id": job_id, "output": str(output_image), "external_api": True})

    manifest = load_manifest(run_dir)
    if has_incomplete_selected_jobs(manifest, selected_ids):
        raise SystemExit("some selected jobs remain incomplete after resume loop")

    if has_incomplete_jobs(manifest):
        print(
            json.dumps(
                {
                    "ok": True,
                    "completed": completed,
                    "finalized": False,
                    "reason": "run still has pending jobs outside this invocation",
                },
                indent=2,
            )
        )
        return

    finalize_command = [
        sys.executable,
        str(Path(__file__).resolve().parent / "finalize_pet_run.py"),
        "--run-dir",
        str(run_dir),
    ]
    subprocess.run(finalize_command, check=True, text=True, encoding="utf-8", errors="replace")

    final_dir = run_dir / "final"
    qa_dir = run_dir / "qa"
    validation_path = final_dir / "validation.json"
    review_path = qa_dir / "review.json"
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    review = json.loads(review_path.read_text(encoding="utf-8"))
    if not validation.get("ok"):
        raise SystemExit("final validation did not report ok=true")
    if review.get("errors") not in ([], None):
        raise SystemExit("qa review reported top-level errors")
    row_errors = []
    rows = review.get("rows")
    if isinstance(rows, list):
        for row in rows:
            if isinstance(row, dict) and row.get("errors"):
                row_errors.append({"state": row.get("state"), "errors": row.get("errors")})
    if row_errors:
        raise SystemExit(json.dumps({"row_errors": row_errors}, indent=2))

    print(
        json.dumps(
            {
                "ok": True,
                "completed": completed,
                "spritesheet_png": str(final_dir / "spritesheet.png"),
                "spritesheet_webp": str(final_dir / "spritesheet.webp"),
                "validation": str(validation_path),
                "review": str(review_path),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
