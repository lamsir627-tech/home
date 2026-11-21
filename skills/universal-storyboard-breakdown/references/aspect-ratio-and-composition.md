# Aspect Ratio And Composition

Apply this reference before timing, grouping, or drafting shots. Treat aspect ratio as a confirmed composition parameter, not as a suffix, a later crop instruction, or a new standalone output field.

For a continuation of the same script job under [long-text-workflow.md](long-text-workflow.md), reuse its verified, explicitly resolved ratio and skip new-job confirmation. A new source/job still follows section 1 before timing/drafting; source-only indexing may proceed without camera parameters. In all modes, ratio adaptation must preserve saved world-space positions, movement routes, endpoints and scene-instance handoffs: use camera position/distance, framing or tracking first. The movement-path suggestions below do not authorize changing locked blocking. A requested alternative staging gets a separate labeled state chain with affected handoffs rechecked before delivery.

## 1. Resolve The Target Ratio

Resolve the ratio from the current user's instructions or the verified manifest for this same job. If the user explicitly delegates the ratio or unspecified production parameters, choose a suitable ratio, state it and record `授权代选` with its basis; use `9:16竖屏` for a short drama with no other basis. Merely saying `继续` or `连续完成` is not delegation. With neither a ratio nor delegation for a new job, ask once: `请确认本次分镜需要哪种画幅：9:16竖屏、16:9横屏，还是其他比例？` Wait before timing/grouping/drafting, while independent source and asset work may proceed. Do not borrow settings from another job.

If the current request explicitly names one or more ratios, proceed without asking again. Normalize full-width punctuation such as `9：16` to `9:16`. Accept any positive `W:H` ratio. Common classes are `9:16竖屏`, `16:9横屏`, `1:1方形`, `3:4竖幅`, `4:3横幅`, and `21:9超宽横屏`.

If the user requests several ratios, create complete labeled variants. Keep dialogue, duration, plot order, action milestones, normalized shot sizes, screen direction, character state, eyeline, and prop state identical across variants; change camera position/distance, screen-space composition, foreground layering, look room and tracking while preserving world-space blocking and movement paths. A separately requested restaging is a labeled alternative with a separate checked state chain.

## 2. Universal Composition Rules

- Recompose for the target frame instead of describing a later crop.
- Treat shot size as subject coverage. A `中景` remains a `中景` across ratios even when camera distance or foreground width changes.
- Keep the speaking face, active hands, active prop, contact point, and visible action result inside the central action-safe area.
- Give gaze, approach, throwing, running, entering, and exiting actions positive lead space in their travel direction.
- Preserve established screen direction and the 180-degree axis. Changing ratio does not authorize swapping character sides.
- Use background width or height only for concrete story information, spatial depth, concealment, scale, or movement.
- Keep each group independently generatable by stating the normalized ratio and orientation in `视觉风格`, while expressing usable ratio-specific geometry inside the existing shot-description fields. Begin the internal combined-prompt assembly with the same ratio, but do not expose a separate `合成提示词` field in the standard final deliverable.

## 3. 9:16 Vertical Composition

- Organize space through foreground, middle ground, and background depth; use doors, stairs, windows, corridors, table edges, or light shafts as vertical guides only when present.
- Place a single subject near the center vertical axis with usable headroom and visible hands or active props. Use the upper and lower frame areas for supported environment and body-action information.
- Stage two people with depth staggering, diagonal opposition, upper/lower separation, shoulder-edge foreground, or controlled side-by-side spacing. Keep both faces and the active interaction readable.
- For locked lateral travel, use camera distance, angle or a concise pan/track to keep the existing path readable. Choose depth/diagonal staging only when first establishing an unspecified path or creating an explicitly requested restaging variant; preserve its resulting state chain.
- For group scenes, layer a clear main subject with a small number of foreground fragments and background reactions; avoid compressing every named character into one narrow plane.
- Use wide shots only when vertical architecture, height difference, crowd depth, or full-body action materially matters.

## 4. 16:9 Horizontal Composition

- Use left/right geography, lateral separation, over-the-shoulder relationships, and foreground-to-background depth together.
- Give eyelines and movement clear horizontal lead room. Let entrances, exits, chases, handoffs, and confrontations use the longer horizontal axis.
- Stage two people in readable left/right zones or an asymmetric two-shot while keeping the active hands or prop between them visible.
- Use the extra width for concrete environment, obstacles, witnesses, doors, vehicles, or action paths already supported by the script.
- Keep close shots purposeful; fill the width with relevant shoulder, prop, or environment context rather than empty lateral space.

## 5. Other Ratios

- `1:1`: use centered, triangular, or compact diagonal arrangements; keep negative space balanced and movement concise.
- `3:4`: follow vertical-depth principles with slightly more lateral breathing room than `9:16`.
- `4:3`: combine moderate left/right geography with strong foreground depth; favor compact relationship shots.
- `21:9`: use lateral geography and layered ensembles while keeping faces, hands, props, and contact points in the central action-safe region; reserve outer width for supported scale and movement.
- Custom ratios: classify as vertical when `H>W`, horizontal when `W>H`, and square when equal, then interpolate from the nearest rules above.

## 6. Shot-Description Integration

- In a single-visible-character `画面简介`, express ratio-specific placement after the first camera-language semicolon without adding a new camera field.
- In a multi-character shot, express ratio-specific geometry in `镜头与人物的位置关系`, then define camera distance and movement from the same center anchor in `镜头机位`.
- In pure prop/detail shots, place the active prop and its travel or reveal axis inside the target frame's action-safe area.
- Keep ratio language concise and filmable. State positions, depth, lead room, foreground share, movement route, and visible coverage rather than abstract phrases such as `适配竖屏` or `适配横屏` alone.

## 7. Aspect-Ratio Audit

Fail and rewrite when any applicable condition is false:

1. Before timing/grouping/drafting, the ratio was resolved under section 1 from the current choice, the same-job verified manifest, a user answer or explicit delegation, with its basis saved.
2. Every group uses one matching normalized ratio in `视觉风格`, ratio-specific shot geometry, and the internal combined-prompt assembly without adding standalone `目标画幅` or `画幅与构图` fields.
3. Single-character shots place the subject, hands, props, and action result legibly within the selected frame.
4. Multi-character shots use geometry suited to the ratio while preserving the established axis and character sides.
5. Entrances, exits, gaze, and moving props have lead space in the correct direction.
6. Ratio adaptation preserves locked speech, timing, plot order, action milestones, normalized shot sizes, posture, eyeline, and prop state.
7. Every internal combined-prompt assembly begins with the normalized ratio and orientation and describes native composition without later-crop language; it is not emitted as a separate field in the standard final deliverable.

Record the result in the internal self-check, including the confirmed ratio, orientation, composition method, and safety of faces, hands, active props, contact points, entrances, exits, and action results. Do not output the self-check unless the user explicitly asks for audit details.
