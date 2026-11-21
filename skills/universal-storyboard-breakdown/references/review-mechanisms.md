# Storyboard Review Mechanisms

Establish action/dialogue timing under Audit 0 before the first shot draft, then check it against the actual draft and after later repairs. Run the remaining audits after the first shot draft and before lighting-and-color optimization. Lock timing and run dialogue-performance reduction before applying [microexpression-and-emotion-intensity.md](microexpression-and-emotion-intensity.md). For paired bilingual source lines, lock English as the sole audible main track before timing. Any shot, rolling three-shot window, or group boundary that fails an applicable audit must be rewritten and audited again.

## Default long-text audit context

For all script jobs, load [long-text-workflow.md](long-text-workflow.md) before these audits; multi-episode work also follows [full-script-mode.md](full-script-mode.md). Load incoming scene-instance states before drafting, then run actual rendered-dialogue verification and separate action/narrative/state review after all shot, ratio, performance, and lighting repairs. Update changed states and downstream dependencies before saving a checked checkpoint. A source-integrity-only pass or checked source-classification flag is not a final storyboard pass.

- Scope rolling windows and group boundaries to real source-ordered neighboring shots. Episode or batch boundaries do not erase an available neighbor, but selected nonconsecutive episodes must not be concatenated into a false rolling window. Missing historical shots remain unverified.
- Never repair a group by moving locked speech or action across an original episode boundary. Apply the final-incomplete-group exception to group totals only; per-shot timing and complete-action requirements remain in force.
- A center-anchor/focal-role change changes how a shot is described, not the fixed world-space origin or any character's actual position. Recompute shot-relative geometry from the saved physical anchors and current camera.
- For same-job continuation, the explicitly resolved ratio and other parameters in the verified manifest satisfy the original confirmation requirement. A new job still resolves its own parameters.
- An episode passing these audits does not certify unrequested, missing, or not-yet-generated episodes. Compare the rendered source fields to the ledger and the ledger to the source before reporting coverage.

## Audit 0: Action And Dialogue Timing Match

Apply [3C. 剧本动作与人物对话时序匹配](source-text-and-shot-rules.md#3c-剧本动作与人物对话时序匹配) to each dialogue beat and its surrounding visual descriptions. Keep the classification and evidence in existing internal records, then check the rendered visual, sound and locked-audio fields together.

Pass only when:

1. The surrounding action, its actual performer and its relation to the dialogue have been identified: action before speech, overlapping speech, or after speech; mixed beats have separate phases. Continuous posture is not invented as a fresh action, and dialogue about an event is not automatically staged as a present event.
2. The prompt states the actual completion/trigger point before speech, the real overlap interval, or the speech ending/keyword that releases the next action. Describing the action and copying the line into the same shot is insufficient when their timing relation remains unspecified.
3. Sequential time is added, overlap is counted once, and lead-ins/tails remain allocated. A delayed voice onset leaves enough time for the full locked line; declared timing includes required action results and does not double-count pauses or persistent states.
4. Shot cuts and group boundaries preserve these relations and completed states. Focal rotation neither advances the listener's reaction nor moves an irreplaceable visible action off screen; source words and speaker ownership stay intact.
5. The existing per-shot caps, natural phrase/action cuts and short-silent-shot restrictions still hold. Repair the timing plan when the selected sequence cannot fit, then re-lock it before performance refinement.

## Audit 1: Dialogue Performance Reduction

Apply to every shot whose `字幕/角色台词/旁白` field contains role dialogue.

Audit the visual `镜头描述`. Do not rewrite locked speech or remove source-required vocal delivery from `音效/现场声`.

### Preserve

- Preserve locked dialogue exactly and in order.
- Preserve source-mandated action, prop contact, blocking change, danger response, entrance, identity reveal, and decisive emotional turn.
- Preserve one visible state or action needed to make the line readable in the scene, including the source-supported speaking emotion; performance reduction must not flatten every line to neutral. Use the concrete visual/vocal approach in [分镜使用规则](source-text-and-shot-rules.md#5e-分镜使用规则).
- Preserve continuity inherited from the preceding shot.

### Reduce

- Remove decorative micro-expressions that do not change the scene state.
- Remove eyebrow, lip, head, finger, and hand beats assigned separately to each clause.
- Remove repeated pointing, pacing, fist clenching, table tapping, turning, or body leaning when the line remains clear without them.
- Remove reaction escalation added only to make ordinary dialogue look dramatic.
- Reduce ordinary dialogue to stable posture, clear eye-line, restrained breath, and at most one plot-functional action when practical.

Do not treat this reduction pass as a ban on all microexpressions. After timing is locked and this audit passes, the microexpression module may classify the shot's local emotion event and add back only the source-supported changes permitted by the `locked duration × event level` matrix. It may not fill unused time with acting, restore clause-by-clause decoration, or change timing.

### Pass Conditions

A dialogue shot passes when:

1. The locked line is unchanged.
2. Every retained performance detail is required by the source, spatial clarity, causal continuity, prop state, or a decisive emotional turn.
3. The visual does not assign a new gesture or facial change to every phrase.
4. The performance does not compete with the dialogue or reset the character's position without cause.

Record any retained strong-performance exception in `分镜自检` with a short reason such as `原文明确要求崩溃大喊` or `该动作触发下一事件`.

## Audit 2: Conditional Shot-Description Format

Count visible people and animals in the final visual description after Audit 1. Count a visible face, full body, body fragment, reflection, silhouette, or clearly visible foreground ear/hand as a visible character. Do not count an off-screen voice.

### Exactly One Visible Character

Output only:

```markdown
**镜头描述**：
- **画面简介**：中景，平视侧前方固定拍摄，焦点落在角色上半身；背景环境、唯一可见角色的位置/朝向/状态、相关道具与光线、完整动作及可见结果。
```

Omit all of the following:

- `中心锚点角色`
- `镜头与人物的位置关系`
- `镜头机位`

The `画面简介` must remain directly generatable. Before its first semicolon, state exactly one standard shot size, a basic camera angle, a fixed or simple moving-camera instruction, and the focus subject. After the semicolon, include both the background and the character, not only an isolated action or facial expression. Keep this camera phrase concise; do not add a separate camera field or overload it with lens packages and detailed rig specifications.

### Two or More Visible Characters

Output the full three-part format:

1. `镜头与人物的位置关系`, beginning with one `中心锚点角色`.
2. `镜头机位`, defined from the same anchor.
3. `画面简介`, containing background-supported action and result.

Use this route even when the second character is only a visible foreground fragment, reflection, or silhouette.

An over-the-shoulder shot/reverse-shot inherits single-character subject, blocking, speech-emotion and rotation rules, but uses this three-part format whenever two or more characters are visible. `Multi-character` here means two or more for formatting; the `多人站位关系镜头` subtype requires at least three visible characters.

### Zero Visible Characters

For a pure prop, environment, POV, or detail shot, keep the existing three-part format with `中心锚点角色：角色名（画外）。` This audit changes only shots with exactly one visible character.

### Pass Conditions

A shot passes when:

1. Visible character count matches the chosen format.
2. A single-character shot contains only `画面简介`; its opening camera phrase contains one standard shot size, a basic angle, a fixed or simple moving-camera instruction, and the focus subject, while the text after the first semicolon includes background, character, and complete action.
3. A multi-character shot has exactly one center anchor and the relationship and camera fields use the same coordinate origin.
4. Removing unnecessary dialogue performance has not silently changed the character count without a second format check.

## Audit 2A: Shot Use, Speaking Emotion And Blocking

Apply [5E. 分镜使用规则](source-text-and-shot-rules.md#5e-分镜使用规则) to the actual shot content. Record the type and any multi-character blocking task internally; do not add a visible delivery field.

A shot passes when:

1. Exactly one visible role is treated as a single-character shot; two or more as a relationship shot. Count visible foreground fragments, and count each distinct role once. A three-or-more-character cast list alone does not prove that three roles are visible in this shot.
2. Single-character and over-the-shoulder shots inherit the current world-space position, facing, eyeline and action state. The speaker gets the preferred shot when compatible with rotation and required action; the focal role in an over-the-shoulder shot is its clear speaking/reacting target, not automatically the foreground shoulder.
3. Speaking emotion remains concrete in the visible speaker's readable performance and vocal delivery, with source/continuity support and within the locked-duration matrix. An off-screen speaker carries that emotion through sound; the visible listener shows only their own supported response and does not lip-sync the speaker's line. Neutralizing meaningful emotion and adding decorative emotional escalation both fail.
4. A `多人站位关系镜头` shows at least three established roles and serves at least one task: a rotation repair that single/over-the-shoulder framing cannot preserve, a large action requiring interpersonal geometry, or a blocking change. Required two-person actions remain visible without being mislabeled as this subtype or inventing a third role.
5. A rotation repair changes the actual focal character. More visible people, a wider size, a new label or decorative crowd feedback cannot conceal an unchanged A/A/A focal sequence.
6. Large actions and blocking show source-supported starting positions, movement paths, contact/change and visible end states within the shot-duration and action-milestone rules. The center anchor stays unique; the shot does not assign a separate performance arc to every visible person.

## Audit 2B: Scene-State Handoffs Including Nonadjacent Returns

Before drafting, apply the [state-first workflow](full-script-mode.md#起草前先建立状态与必要变化再编排镜头) to establish calibrated anchors, incoming states and necessary changes. Review the first draft, then repeat this audit on affected changes and scene entries after camera, focal, framing, performance and lighting repairs. Use the instance chain and spatial-entry requirements in [full-script-mode.md section 3](full-script-mode.md#按实例维护接续链). This is a semantic review of the actual prompt text; the audio/timing scripts do not perform it.

Pass only when:

1. Each entry is classified as a direct continuation, return to a continuing instance, or new instance. For continuations, record the actual source group/shot and state version; for a new instance, record its source-supported initial state without inventing a predecessor. Review nonadjacent returns against the latest valid state of that instance, not the preceding unrelated group or the scene's original blocking.
2. The independently copied group/scene entry contains fixed anchors, relevant characters' foot/seat positions, body facing, head direction, gaze target, posture/action phase, each relevant hand's occupancy and contact/support relation, necessary distances and camera side. Include relevant off-screen counterparts. Body/head/gaze may share one description when aligned, but a head turn does not silently rotate the torso or move the feet. The first shot agrees with these facts; a global header, generic scene label or `保持一致` alone fails.
3. Compare the actually consumed source state/version with the downstream entry, character by character and prop by prop, including anatomical left/right hands and contact body parts. Every difference has a source-supported action/time transition or a recorded consistent filming decision for previously unspecified detail. Keep camera position/orientation separate and derive screen ordering, visible face side and off-screen gaze direction from it. Camera-only changes affect projection, not physical positions; a screen-side change alone does not prove a blocking error. No change evidence means no reset.
4. Shots completing changes in position, contact and props actually describe their results; unchanged facts remain valid through that scene segment's end. Derive its saved end state from the final reviewed shot sequence, without requiring every character to reappear in the last shot, and match the version consumed by every downstream entry. A draft state or an unaccepted generated-frame deviation does not qualify.
5. Multiple scenes in one group have separate states. Next-day/flashback instances use their own source-supported blocking; continuing scenes preserve their latest action results. Neither scene assets nor focal-role changes overwrite the instance state.
6. The asset description, group subject summary, scene entry, actual shot text and downstream entry agree on physical layout and state. Use visible anchor relationships from inspected references; an uncalibrated compass direction or a screen-left/screen-right swap does not establish a different physical layout. An identified image/text contradiction fails before drafting proceeds with that layout.
7. Every change of position, posture, gaze, prop ownership or contact has a before-state, supported cause, carrying shot/completion point and usable result in the internal change record. Check both the whole group and each shot: action order, reach, occupied hands, stable support before release and available time must support the written result. A correct group total or the same state sentence repeated in several fields is insufficient. Unsupported decorative blocking is reduced; required source action and valid upstream states remain intact. A necessary visible completion cannot be replaced by a group-header assertion or an invented off-screen bridge.
8. For reverse shots, continuation entries and framing/detail conflicts, apply [shot-space checks](shot-space-checks.md): the selected camera, visible torso/face side, actual background, visible-role set and required body/detail coverage must be simultaneously possible. Off-screen continuity does not summon extra visible cast; a close face crop cannot prove a thigh-level hand state. Repair the camera/framing or a source-supported action instead of silently moving people, rotating their bodies or inventing contact. A valid reverse shot may change screen sides and a required story action may change body facing.

Record each reviewed link, compared fields, differences/evidence and pass/fail/unverifiable result in the project records. Missing evidence remains unverifiable; a known contradiction fails. First-frame, binding and generated-video checks follow [global-asset-control.md section 3A](global-asset-control.md#3a-站位参考首帧与实际画面承接) only when those media stages are requested. A storyboard can pass this text audit while actual-media verification remains unperformed; report them separately.

For requested media work, keep text-state, actual-input, first-frame, video-action and cross-segment handoff results separate, with real frame times and the state version each consumer uses. Do not promote failed/unverified media states or silently retain passes after an upstream revision. Verify the actual generation input under [section 3B](global-asset-control.md#3b-实际生成输入版本); the editor's current prompt and a successful task status do not establish the historical submitted payload or visual continuity. Only affected production/acceptance is held back; independent text work can continue.

## Required Audit Order

1. Establish calibrated spatial anchors, incoming character/prop states and necessary changes under the state-first workflow. Apply Audit 0 to the source context, draft the action/dialogue timeline, then lock timing, shot count, group boundaries, dialogue pace, and continuous actions. Check the actual draft with Audits 0 and 2B before refining performance; repair state conflicts or overloaded action first.
2. Run Dialogue Performance Reduction.
3. Recount visible characters and select single-character, over-the-shoulder or qualifying multi-character blocking use under section 5E of the source/shot rules.
4. Apply Conditional Shot-Description Format and Shot Use, Speaking Emotion And Blocking.
5. Apply [microexpression-and-emotion-intensity.md](microexpression-and-emotion-intensity.md): classify every group at `一级/二级/三级`, classify each character-visible shot's local event at `低/中/高`, calculate final complexity from the locked-duration × event-level matrix, and fit only the permitted supported changes without changing timing.
6. Re-run Dialogue Performance Reduction and visible-character formatting after microexpression integration.
7. Run Dialogue-Split Variation And Sound Progression below.
8. Run Three-Shot Focal Subject Rotation below across the complete shot stream, including group boundaries; after every repair, recount visible characters and return to Audits 2 and 2A for the changed shot.
9. Run Bilingual Main Audio Track below.
10. Run Natural Shot Language below.
11. Run Group Generation Task below.
12. Run Group Emotional Target below.
13. Run Audit 7: Adjacent Shot Sizes Within And Across Groups below.
14. Run Aspect Ratio And Composition below.
15. Run framing, close-shot, prompt-cleanliness, lighting, microexpression matrix/continuity, and general continuity checks. Fail when long ordinary dialogue is upgraded merely because time is available, or when a short high event is overloaded instead of reduced to the matrix result.
16. Recheck Audit 0 against the final repaired shots, including their boundaries; run Audit 2B on the final scene-state handoffs, including nonadjacent returns, and update downstream dependencies. Record all audit results internally. Do not expose the working `分镜自检` in the standard final deliverable unless the user explicitly asks for it.

## Audit 3: Dialogue-Split Variation And Sound Progression

Apply whenever one locked audio line spans two or more shots.

### Visual pass conditions

1. Every fragment has a distinct visible beat: inherited action result, breath/eyeline beat, relationship or prop-state emphasis, spatial reveal, or final landing.
2. The cut preserves position, screen direction, posture, eyeline, and prop state instead of resetting the speaker.
3. Two shots do not reuse the same `画面简介`, relationship paragraph, and camera paragraph while changing only the source-text fragment.
4. Camera changes have a narrative purpose and are not a blind angle cycle.

### Sound pass conditions

1. Stable location ambience may continue.
2. Each shot adds the action/prop/body sound supported by its visible beat.
3. The first, middle, and final fragments use different audible delivery instructions: entry breath, continuing cadence or punctuation breath, semantic stress, and final landing.
4. Two shots in one group do not contain an identical complete `音效/现场声` field unless one indivisible sound event explicitly continues across the cut.

Fail and rewrite the shots when dialogue text is the only changing field.

## Audit 3A: Three-Shot Focal Subject Rotation

Apply a rolling window to every three consecutive shots in the complete ordered deliverable, including windows that cross a group boundary.

### Identify the focal subject

1. In a single-visible-character shot, the sole visible character and declared focus subject are the focal subject.
2. In a multi-character shot, use the character who owns the reaction/action focus and is named as the center anchor or focus lock. Background witnesses do not change the focal subject.
3. In a pure prop/detail shot, the active prop is the focal subject; do not mislabel it as an alternate-character feedback shot.
4. The audible speaker and focal visual subject may differ. An off-screen speaker does not make that speaker the visual focal subject.

### Fail condition

Fail whenever shots N, N+1, and N+2 all have the same focal character. Re-run the rolling window after every repair so that a new overlap does not create another three-shot run.

### Required repair

1. Prefer changing shot N+2 into a concrete feedback shot centered on another established character who is physically present or causally engaged in the same beat. This overrides the preference to show the current speaker. Use a single-character or over-the-shoulder feedback shot; if those cannot preserve required action and spatial relationships, use a qualifying three-or-more-character blocking shot under section 5E, with the alternate character as the actual focal subject.
2. If N+2 contains an irreplaceable source-defined reveal, contact, or action result belonging to the original subject, change N+1 instead. Change N only as a last resort.
3. Preserve the locked main-track source line and duration. The original speaker may continue audibly from off screen while the alternate character receives the visual focus.
4. Give the alternate character one source-supported readable response: eyeline change, breath, posture, hand/prop contact, recoil, hesitation, acceptance, refusal, or another plot-functional reaction. Do not invent a new event or decorative reaction escalation.
5. Preserve group totals, shot count, dialogue order, action milestones, screen direction, positions, eyelines, prop states, emotion carryover, lighting, and target ratio.
6. Recount visible characters and reapply the single-/multi-character format. If the feedback character becomes the only visible role, use the single-character format; if the original subject remains visibly present, use the three-part multi-character format with the feedback character as the unique center anchor.
7. A scene that objectively contains only one established character is the sole exemption. Record it internally as `单角色场景豁免`; never invent a character to satisfy the rotation rule.

### Pass condition

No rolling three-shot window contains the same focal character three times unless the single-character-scene exemption applies. A source-required prop/detail shot keeps its own focal identity; do not manufacture or substitute prop/empty shots to repair a failed three-character run. Such a failure still requires the alternate established character feedback described above.

## Audit 3B: Bilingual Main Audio Track

Apply when the source contains paired English and Chinese versions of the same dialogue, VO, or narration.

1. Match paired lines by role, order, and semantic content before timing.
2. Lock the English wording and punctuation as the sole audible main track. Use English delivery and pauses to calculate duration and drive lip sync.
3. Keep the paired Chinese text only in the internal source ledger as translation/subtitle reference. Do not voice it, repeat it after English, add its duration, or request generated Chinese text.
4. Render the final source-text field as `英文主声轨（锁定）— ROLE: Exact English source line`.
5. If a source beat exists in only one language rather than as a pair, preserve that available language as the locked main track; do not translate or fabricate the missing line.
6. Fail if English and Chinese are both described as audible, if duration counts both versions, if Chinese drives lip sync for a paired line, or if the English source is rewritten.

## Audit 4: Natural Shot Language

Apply to every final `画面简介`.

1. Split a raw scene heading into location, interior/exterior, time, and cast, then keep that label internal. For a single-character shot, inspect the visible-content clause after the required camera-language semicolon. Fail any rendered visible content that begins with the complete location label, including `夜里的/白天的 + 场景标签` variants.
2. Keep cast lists and continuity metadata in their dedicated fields; do not paste them into the background.
3. Replace workflow language with concrete visible facts:
   - `承接上一镜` → the actual posture/location;
   - `既定信息对象` → the visible person, prop, doorway, or direction;
   - `持物结果` → what the hands are actually holding or touching.
4. Select the current shot's visible micro-setting rather than a generic room inventory: the surface under the active prop, concealment actually used, doorway/exit defining distance, foreground obstruction, or relevant practical light. Let the action lead when it is the strongest visual evidence.
5. Use one compact multi-clause sentence or two to four short sentences. A single sentence is valid when it contains concrete visible clauses; never pad it to satisfy a sentence count.
6. Fail the shot when it reads like metadata or an audit checklist, exposes scene numbers/cast strings, uses label-led or generic fillers such as `空间边界清楚` and `主要通行方向保持畅通`, lacks concrete visible nouns or a visible state/action/change, or relies on long semicolon chains.

## Audit 5: Group Generation Task

Apply to the group-level `生成任务`.

1. Read the complete current-group source rather than only its first and last records.
2. Extract two or three decisive visible beats: action, relationship/response, and result/threat/reveal.
3. Write one short natural sentence beginning with a concrete action verb such as `呈现`, `表现`, `刻画`, `展现`, `拍摄`, or `描绘`.
4. Keep exact start/end text in internal boundary records. Do not quote it in `生成任务`, use `由……推进至……`, append ellipses, repeat role/performance labels, or write generic filler such as `生成一段写实中文短剧连续分镜`.
5. Fail when the sentence can be reused unchanged for another unrelated group or when it invents a beat absent from the current group.

## Audit 6: Group Emotional Target

Apply to the group-level `情绪目标`.

1. Read the complete current-group source plus the final visible and audible beats.
2. Select one or two concrete emotional devices already present in the group: sound, spatial distance, concealment, approach, breath, gaze, prop reveal, action contrast, clue discovery, hesitation, impact, or release.
3. Name the viewer-facing emotional effect produced by those devices, such as threat, suspense, curiosity, pressure, fear, shock, humor, relief, deduction pleasure, or counterattack expectation.
4. When the feeling changes, state the progression or landing with a natural connector such as `再`, `随后`, `逐步`, or `转而`.
5. Keep exact start/end source text in internal boundary records. Do not quote it in `情绪目标`, write `由……落到……`, append ellipses, expose role/performance labels, or use generic filler such as `通过距离、朝向、呼吸与动作节奏呈现`.
6. Fail when the sentence only repeats plot events, lacks a viewer-facing emotional effect, can be reused unchanged for another unrelated group, or invents a device absent from the current group.

## Audit 7: Adjacent Shot Sizes Within And Across Groups

Apply to every consecutive shot pair inside each group and across adjacent groups in the resolved `15秒模式` or `30秒模式`, including scene changes. Follow the actual source-ordered shot stream under source-text-and-shot-rules.md section 5B; do not join nonconsecutive selected episodes or treat unknown intervening shots as verified boundaries.

### Normalize the shot size

1. Use exactly one of these standard shot sizes in every shot: `大远景`, `远景`, `全景`, `中景`, `中近景`, `近景`, `特写`, or `大特写`.
2. For a multi-character or zero-character shot, read the size from `镜头机位`. For a single-visible-character shot, read it only from the camera-language clause before the first semicolon in `画面简介`.
3. Match longer labels before shorter labels so `大远景` is not reduced to `远景`, `中近景` is not reduced to `近景`, and `大特写` is not reduced to `特写`.
4. Normalize compound phrases by their standard label: `中景双人` and `中景反打` both become `中景`; `过肩近景` becomes `近景`.
5. Fail any shot that has no standard size or more than one standard size in the designated camera location.

### Adjacent-pair pass conditions

1. Normalize every shot, then compare each within-group pair (`1→2`, `2→3`, through the last pair) and each available adjacent group end/start pair. A within-group pair passes with different sizes or a supported exemption under source-text-and-shot-rules.md section 5B. A cross-group pair passes only with different sizes, including at scene changes; within-group exemptions do not apply. Nonadjacent size reuse is allowed: `中景→中近景→中景` passes this check.
2. For matching within-group sizes, verify at least one exemption: actual focal-character change, clearly perceptible viewpoint change, genuine over-the-shoulder shot/reverse-shot, source-grounded solitude, or a source-supported emotional climax. Small angle changes alone fail; an independently supported exemption may still qualify. For an angle exemption, inspect actual before/after camera geometry and visible results, not just angle labels. No fixed numeric angle threshold is assumed. Do not mistake an off-screen speaker change for a visual subject change, a single visible role for solitude, or an emotional adjective for a climax. Timing, source fidelity, spatial continuity, focal rotation, and close-shot ratios still need separate checks.
3. Repair a failing pair's later shot framing and size description first, then the earlier shot if needed, preserving the hook and action readability. A label-only change fails. If neither shot can change safely, return to planning intact source-speech/action units within the original episode; boundary movement alone supplies no exemption evidence, and all resulting pairs must be rechecked under their actual scope. Never invent filler shots/actions or exemption conditions to pass.
4. Preserve locked source text, credible duration, action milestones, screen direction, character position, posture, eyeline, prop state, and causal continuity. Recheck both neighbors of each changed shot, overlapping focal-subject windows, and affected group boundaries. Record any unresolved conflict as a failure.
5. Internally record each group's normalized size sequence and every pair as `通过`, `豁免通过` with category/evidence, or `失败`; angle evidence includes before/after viewpoint and visible difference. `组内无相邻镜对` applies only to a single-shot group. For cross-group checks, use `无前组` only when no preceding adjacent group exists; otherwise record actual sizes and pass/fail without within-group exemptions, or `不可核对` for an unknown boundary. A first group still needs all internal pairs checked. Keep these audit records out of the standard final deliverable.

## Audit 8: Aspect Ratio And Composition

Apply [aspect-ratio-and-composition.md](aspect-ratio-and-composition.md) after shot timing, visible-character formatting, and within-group/cross-group adjacent-shot size auditing.

### Pass conditions

1. Before timing/grouping/drafting, the ratio was resolved under aspect-ratio-and-composition.md section 1 from the current choice, the same-job verified manifest, a user answer or explicit delegation, with its basis saved.
2. Every group's `视觉风格`, ratio-specific shot geometry, and internal combined-prompt assembly use one matching normalized ratio and a concrete composition strategy, without standalone `目标画幅`, `画幅与构图`, or `合成提示词` fields.
3. Single-character shots keep the face, active hands, active props, and visible action result readable in the selected frame.
4. Multi-character shots use ratio-appropriate geometry while preserving the established center anchor, screen direction, character sides, posture, eyeline, and prop state.
5. Entrances, exits, gaze, approach, and moving props retain usable lead space in the correct direction.
6. Ratio adaptation preserves locked speech, credible duration, plot order, action milestones, normalized shot sizes, and causal continuity.
7. Every combined prompt begins with the normalized ratio and orientation and describes native composition without later-crop language.

Fail and rewrite any shot or group that treats aspect ratio as a suffix while leaving incompatible blocking or clipped action coverage. Record the ratio, orientation, composition method, and action-safe result in `分镜自检`.
