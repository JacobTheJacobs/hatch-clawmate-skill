# Animation Rows

The Codex app reads one fixed atlas: 8 columns, 22 rows, 192x208 pixels per cell.

| Row | State | Used columns | Durations |
| --- | --- | ---: | --- |
| 0 | idle | 0-5 | 280, 110, 110, 140, 140, 320 ms |
| 1 | running-right | 0-7 | 120 ms each, final 220 ms |
| 2 | running-left | 0-7 | 120 ms each, final 220 ms |
| 3 | waving | 0-3 | 140 ms each, final 280 ms |
| 4 | jumping | 0-4 | 140 ms each, final 280 ms |
| 5 | failed | 0-7 | 140 ms each, final 240 ms |
| 6 | waiting | 0-5 | 150 ms each, final 260 ms |
| 7 | running | 0-5 | 120 ms each, final 220 ms |
| 8 | review | 0-5 | 150 ms each, final 280 ms |
| 9 | coding | 0-5 | 150 ms each, final 260 ms |
| 10 | communicating | 0-5 | 150 ms each, final 260 ms |
| 11 | monitoring | 0-5 | 150 ms each, final 260 ms |
| 12 | read-file | 0-5 | 150 ms each, final 260 ms |
| 13 | syncing | 0-5 | 150 ms each, final 260 ms |
| 14 | system | 0-5 | 150 ms each, final 260 ms |
| 15 | run-tool | 0-5 | 150 ms each, final 260 ms |
| 16 | reaction | 0-5 | 150 ms each, final 260 ms |
| 17 | web-fetch | 0-5 | 150 ms each, final 260 ms |
| 18 | web-search | 0-5 | 150 ms each, final 260 ms |
| 19 | working | 0-5 | 150 ms each, final 260 ms |
| 20 | vibe | 0-5 | 150 ms each, final 260 ms |
| 21 | write-to-file | 0-5 | 150 ms each, final 260 ms |

Unused cells after each row's final used column must be fully transparent.

## Row Purposes

- `idle`: calm, low-distraction breathing/blinking loop; use as the reduced-motion first frame. Keep motion subtle and persona-preserving.
- `running-right`: locomotion to the right; 8-frame loop should read directionally.
- `running-left`: mirrored or redrawn locomotion to the left; do not simply reuse right-facing frames unless the design is symmetric.
- `waving`: greeting or attention gesture; clear start, raised gesture, return.
- `jumping`: anticipation, lift, peak, descent, settle.
- `failed`: error/sad/deflated reaction; readable but not visually noisy.
- `waiting`: patient idle variant; glance, small bounce, or prop motion.
- `running`: active working/in-progress loop, as if the pet is busy running a task. This row is not foot-running; avoid jogging, sprinting, treadmill poses, raised knees, long steps, pumping arms, or directional travel.
- `review`: focused/inspecting/thinking loop suitable for review state.
- `coding`: compact coding/work pose loop without detached code glyphs or UI.
- `communicating`: expressive communication loop; tiny accents must remain attached or overlapping.
- `monitoring`: attentive observation/status loop without dashboards or labels.
- `read-file`: focused reading loop without detached document fragments or readable text.
- `syncing`: rhythmic coordination loop with no detached arrows, rings, or icons.
- `system`: process-readiness loop without console windows or warnings.
- `run-tool`: tool-invocation loop through pose or identity-consistent accessory motion.
- `reaction`: compact feedback/emotion loop.
- `web-fetch`: retrieval-intent loop without browser panels or URLs.
- `web-search`: search-intent loop without detached question marks or UI.
- `working`: purposeful non-locomotion work loop.
- `vibe`: pet-specific personality flourish, never smoking. Use a compact attached moment; keep the pet dominant and the flourish secondary.
- `write-to-file`: compact write/save loop without detached file icons or labels.
