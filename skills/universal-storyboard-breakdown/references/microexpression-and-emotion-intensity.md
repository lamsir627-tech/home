# Microexpression And Emotion Intensity

Apply this module after shot timing, dialogue-performance reduction, and causal-action planning, but before final shot-language, lighting, and combined-prompt optimization. It assigns one emotion-intensity level to every group, classifies the local emotion event in every character-visible shot, and derives microexpression complexity from `locked shot duration × emotion-event level` without changing timing.

## Table Of Contents

- [1. 时长权限边界](#1-时长权限边界)
- [2. 分镜组情绪强度三级判定](#2-分镜组情绪强度三级判定)
- [3. 镜头时长与情绪事件等级双轴矩阵](#3-镜头时长与情绪事件等级双轴矩阵)
- [4. 微表情设计顺序](#4-微表情设计顺序)
- [5. 表层情绪与真实情绪](#5-表层情绪与真实情绪)
- [6. 三段式动态表演](#6-三段式动态表演)
- [7. 微表情区域与词库](#7-微表情区域与词库)
- [8. 与表演减量和镜头语言的关系](#8-与表演减量和镜头语言的关系)
- [9. 输出位置](#9-输出位置)
- [10. 审核标准](#10-审核标准)

## 1. 时长权限边界

- Lock every shot duration in the storyboard-planning stage from plot rhythm, audible source-text length, punctuation/performance pauses, action complexity, and editing needs before applying this module.
- The microexpression module has no authority to lengthen, shorten, split, merge, or redistribute any shot. Fit the performance into the existing duration by selecting the most important `1-3` changes.
- Treat `1-3个变化` as visible state changes, not as independent time units. Several facial changes may occur together: eyes can stop while pupils widen and lips part; do not assign a separate duration to every word in the microexpression description.
- Do not pad the shot, slow the locked dialogue, add a pause, or create a reaction insert merely to accommodate expression writing.
- Exception: when the source makes the expression itself a plot event—such as a smile visibly disappearing as the decisive reveal, a character failing to suppress tears, or a reaction exposing identity—return that beat to the storyboard-planning stage for one explicit timing decision. Only the planning stage may revise duration. Once the duration is locked again, this module must obey it.
- The existing mode cap remains absolute: `15秒模式` never exceeds `3.5秒` per shot; `30秒模式` never exceeds `5.0秒` per shot. The `6秒以上` complexity bands below are compatibility guidance for external/custom workflows and never authorize this skill to exceed its resolved cap.

## 2. 分镜组情绪强度三级判定

Assign exactly one internal `情绪强度等级` to every group. Judge the complete group from source-supported triggers, stakes, visible leakage/control, confrontation, reversal, and landing—not from the number of emotional adjectives or close-ups. Do not expose this audit field in the standard final deliverable; express its useful conclusion through `情绪目标` and the visible performance design.

Keep this three-level group summary separate from the per-shot `情绪事件等级` and complexity matrix in section 3. Group intensity summarizes the group's overall stakes, peak, progression, and landing; local event level judges what actually happens inside one shot. Never copy the group level onto every shot. A `三级` group may contain several low-event ordinary-dialogue shots and one high-event betrayal reveal, while any high-event shot is still capped by its locked duration.

### 一级｜低强度

- Use for ordinary exchange, information setup, restrained observation, low-risk suspicion, or an emotional undercurrent without a decisive turn.
- Keep the face mostly stable. Use a brief eye-line stop, one small brow/lip change, restrained breath, or another single leak only where needed.
- Do not manufacture tension or assign microexpressions to every spoken clause.

### 二级｜中强度

- Use when a clear trigger causes noticeable emotional leakage, control, pressure, relationship friction, clue recognition, or a contained turn that changes how the beat is read.
- Concentrate the performance in one or two key shots. Show a readable transition such as `维持状态 → 情绪泄露 → 重新控制` when duration permits.
- Keep secondary characters restrained unless their reaction changes the plot or relationship geometry.

### 三级｜高强度

- Use for a source-supported decisive shock, betrayal, danger response, confession, breakdown, identity reveal, emotional climax, reversal, or reaction that functions as a plot event.
- Allow a stronger leak, suppression failure, or clear turn, but keep one dominant progression. Do not stack shock, rage, grief, fear, and despair as simultaneous labels.
- A high-intensity group does not automatically require more close-ups, more shots, or longer shots. Preserve the established shot plan and close-shot limits unless the source already justifies an exception.

Record one concise internal `情绪强度判定依据` using `触发事件 + 可见/可听反应 + 本组落点`. Do not quote the source boundaries, use generic claims such as `情绪很强烈`, or expose this basis in the standard final deliverable.

## 3. 镜头时长与情绪事件等级双轴矩阵

Do not derive complexity from duration alone. For every character-visible shot, complete these steps internally after duration is locked:

1. Classify the local `情绪事件等级` as `低`, `中`, or `高` from the source-supported trigger and what changes in this shot.
2. Convert locked duration into a `时长容量` ceiling.
3. Convert event level into an `事件需求` ceiling.
4. Set `最终微表情复杂度 = min（时长容量，事件需求）`. The lower side always wins: duration prevents overload; event level prevents long ordinary dialogue from becoming overacted.

### 3.1 逐镜情绪事件等级

| 情绪事件等级 | 判定依据 | 事件需求上限 |
|---|---|---|
| `低` | 普通对白、既有情绪延续、常规信息接收、低风险观察；本镜没有新的利害变化或明确转折 | `低复杂度` |
| `中` | 新线索、怀疑加深、关系压力、被迫控制、局部受伤或一次明确但可控的情绪变化 | `中复杂度` |
| `高` | 发现背叛、决定性真相、身份揭露、突发危险、重大失去、告白、崩溃、反转或表情本身构成剧情事件 | `高复杂度` |

Judge the event locally. Do not upgrade ordinary dialogue merely because it sits inside a `三级` group, uses a close-up, or lasts longer. Do not downgrade a decisive reveal merely because the final complexity must be capped by a short duration; retain the `高` event label and reduce only its visible expression design.

### 3.2 时长容量

| 已锁定镜头时长 | 时长容量上限 | 容量含义 |
|---|---|---|
| `≤2.0秒` | `极简` | 只容纳一个决定性反应单元；多个同步变化可合为同一单元 |
| `>2.0且<3.0秒` | `低` | 稳定状态加一个泄露或控制反应，不写完整转折 |
| `3.0-5.0秒` | `中` | 可保留`2-3个`关键变化，形成简短的触发—泄露—落点 |
| `6.0秒以上` | `高` | 仅在事件本身也是高等级时，才可形成清晰转折或完整情绪弧线 |

For a shot shorter than `1秒` in an external workflow, still use at most one immediately readable state change. The `6秒以上` row is compatibility guidance for external/custom workflows: `15秒模式` still caps shots at `3.5秒`, and `30秒模式` still caps them at `5.0秒`.

### 3.3 最终复杂度矩阵

| 已锁定镜头时长 | 低事件 | 中事件 | 高事件 |
|---|---|---|---|
| `≤2.0秒` | `极简` | `极简` | `极简` |
| `>2.0且<3.0秒` | `低` | `低` | `低` |
| `3.0-5.0秒` | `低` | `中` | `中` |
| `6.0秒以上` | `低` | `中` | `高` |

Final-complexity meanings:

- `极简`：one decisive reaction unit. For a high event such as betrayal in a `2秒` shot, write only `眼神骤停，瞳孔放大`. These two simultaneous eye changes count as one shock unit; do not add brow, mouth, breath, body, and recovery beats.
- `低`：stable state plus one restrained leak or control response. A long ordinary-dialogue shot stays here; duration is unused capacity, not a command to add acting.
- `中`：retain only `2-3` key changes, usually a trigger response, one readable leak, and a short landing/control. A `4秒` betrayal reveal is medium complexity: keep the most decisive changes, not the full emotional arc.
- `高`：a high event with enough locked time may show reception, genuine leakage, turn/control or breakdown, and a clear landing. High complexity means a causal arc, not more adjectives or one isolated gesture per clause.

Required calibration examples:

- `7秒普通对白 → 低复杂度`
- `7秒发现背叛 → 高复杂度`
- `4秒发现背叛 → 中复杂度，只保留最关键变化`
- `2秒发现背叛 → 极简，只写“眼神骤停+瞳孔放大”`

Do not force the maximum within any matrix cell. Dialogue, blocking, prop action, framing, occlusion, or source restraint may require fewer changes. Do not count compatible simultaneous changes mechanically: `眼神定住 + 瞳孔微张 + 嘴唇微张` may be one coordinated shock leak, not three time units.

## 4. 微表情设计顺序

Use this causal order as a selection guide, not a checklist that must fill every slot:

`情绪状态 → 触发点 → 眼神变化 → 眉眼变化 → 嘴部变化 → 呼吸/吞咽 → 身体微反应 → 情绪收束`

1. State the visible starting condition, including a mask such as composed, polite, or cold when supported.
2. Name the concrete trigger already present in the source or shot: a spoken phrase, name, wound, approaching prop, touch, clue, gaze, or visible action result.
3. Select only the facial regions that carry the clearest change in the available time.
4. Add breath, swallowing, jaw, or a small body response only when it is visible/audible and does not compete with dialogue or action.
5. End on the new readable state: control restored, suspicion fixed, anger contained, hurt exposed, or emotion breaking through.

Prefer a dynamic transition over a static label. Replace `她很紧张地看着他` with a concise supported chain such as `她原本强装镇定，听见这句话后眼神停住，眉心收紧，嘴唇微张又抿住；浅吸一口气后重新看向他，把慌乱压回去`. Shorten this chain to fit the locked duration.

## 5. 表层情绪与真实情绪

When the script supports concealment, identify both internally:

- `表层镇定 / 真实慌张`：表情维持平静，眼神变紧，视线快速判断，嘴角僵硬，呼吸变浅。
- `表层冷漠 / 真实心疼`：冷淡状态不变，视线在伤处停留一瞬，眉心极轻收紧，随后移开目光。
- `表层微笑 / 真实愤怒`：礼貌嘴角仍在，笑意不进入眼睛，目光逐渐变冷，下颌与牙关收紧。

Do not write invisible psychology directly in the final prompt. Translate the contrast into visible leakage and control. Do not invent a hidden emotion when the source, relationship, or established performance gives no evidence for it.

## 6. 三段式动态表演

Use this pattern primarily when the matrix result is `中` or `高` and the shot has a clear trigger. A `3-5秒` low-event shot does not gain a three-stage performance merely because the time is available:

1. `接收信息`：眼神停顿、视线转向、眨眼中止或呼吸短暂停住。
2. `真实情绪泄露`：瞳孔、眉心、唇线、下颌、呼吸或身体张力出现一组连贯/同时变化。
3. `控制或爆发`：移开视线、浅吸气、重新抬眼、笑意消失、怒意压住，或源文本要求的爆发落点。

Example: `听见这句话，她的眼神停顿半拍，瞳孔微张，嘴角的笑意僵住；眉心极轻收紧。她短暂垂眼浅吸气，再抬眼时只剩克制的冷淡。`

For a `≤2秒` shot, select only the decisive instant from this pattern. Even for a high event, do not compress all three stages into a frantic checklist.

## 7. 微表情区域与词库

Use the smallest supported combination, prioritizing eyes, brows, mouth, jaw, and breath.

- `眼睛`：瞳孔轻微放大、眼神骤然定住、视线短暂失焦、眼球快速扫向一侧、视线躲闪、眼神逐渐发冷、眼眶轻微泛红、眨眼频率增加、强忍不眨眼、眼睫轻颤。
- `眉眼`：眉心轻蹙、眉梢微挑、单侧眉毛轻抬、眉头瞬间收紧、眉眼慢慢松开。
- `嘴部`：嘴唇微张、唇角轻抽、下唇轻颤、抿紧嘴唇、嘴角勉强上扬、笑意逐渐消失、想开口又咽回去。
- `下颌/面部肌肉`：下颌绷紧、后槽牙暗暗咬住、面颊肌肉轻微抽动、喉结滚动、吞咽一下。
- `呼吸/身体`：呼吸变浅、短促吸气、屏住呼吸、肩颈轻微僵住、身体停住半拍、手指短暂收紧。只保留镜头景别能够看见或现场声能够听见的反应。

Emotion-specific combinations:

- `慌张/紧张`：瞳孔微张、视线游移或躲闪、眨眼变快、嘴唇轻抿、呼吸变浅、吞咽、下颌僵硬，再尝试恢复目光。
- `震惊`：眼神骤停、瞳孔放大、眉毛微抬、嘴唇微张、呼吸停顿、身体短暂僵住。Treat compatible simultaneous changes as one leak.
- `愤怒但克制`：眼神变冷、眉心压低、下颌绷紧、鼻翼轻张、唇线压直、牙关咬住。
- `委屈/隐忍`：眼眶泛红、眼睫轻颤、唇角下压、下唇轻颤、短促吸气，再把泪意或声音压住。
- `心动/害羞`：视线停留后移开、眨眼变慢、嘴角轻扬、耳尖泛红、呼吸轻乱、随后偷看回来。Do not reduce the emotion to `脸红` alone.
- `怀疑`：眼睛微眯、眉梢轻抬、视线上下审视、嘴角轻压，再把视线落回对方眼睛或关键道具。
- `嘲讽/不屑`：单侧嘴角轻扬、眉梢微挑、眼神下压、短促冷笑。Use only one dominant landing.

## 8. 与表演减量和镜头语言的关系

- Run dialogue-performance reduction first. This module may restore only a source-supported trigger-to-response transition, not decorative clause-by-clause eyebrow, lip, head, finger, or hand beats.
- Classify ordinary dialogue as a low event unless this exact shot contains a source-supported local turn. It remains low complexity even when the locked shot is long; use a stable posture plus at most one meaningful leak or control response instead of filling spare time with a full chain.
- Do not force facial detail into a wide shot, occluded face, rear view, pure prop shot, or zero-visible-character shot. Use posture, gaze direction, breath, or no microexpression when the face is unreadable.
- In a multi-character shot, design the primary chain for the focal/center-anchor character. Give another visible character only a plot-functional reaction; do not run separate full arcs on the entire cast.
- Microexpressions do not justify changing shot size, adding close-ups, breaking the 180-degree axis, or violating single-/multi-character formatting.
- Keep one dominant emotional progression. Replace unordered stacking such as `震惊、愤怒、悲伤、害怕、绝望` with a causal turn such as `先因信息怔住，震惊随后收紧为克制的愤怒，泛红眼眶只留下受伤余波` when the source supports it.

## 9. 输出位置

- Keep `情绪强度等级：一级 / 二级 / 三级` and `情绪强度判定依据：` in the internal audit only. Do not add either field to the standard final deliverable.
- Translate their useful conclusion into the required visible `情绪目标` and integrate selected microexpression changes directly into the existing per-shot `画面简介`; do not add a separate shot-level field that breaks the conditional shot-description format.
- Carry only decisive dynamic performance into the visible shot descriptions and the internal combined-prompt consistency check. Do not expose a separate `合成提示词`, or paste the group-intensity analysis, per-shot event labels, complexity labels, matrix, internal surface/true-emotion analysis, or the full lexicon into visible output.
- Record the audit in the internal `分镜自检`: group level and basis, number of key microexpression shots, every relevant shot's local event level and matrix result, timing unchanged, simultaneous changes not mechanically split, and any source-defined expression-as-plot-event exception. Omit this self-check from the standard final deliverable unless the user explicitly requests it.

## 10. 审核标准

Fail and rewrite when any applicable condition is false:

1. Every group has exactly one supported internal `情绪强度等级` and a concrete basis, neither exposed as a standalone standard-delivery field.
2. The group level follows the source trigger, stakes, visible/audible reaction, and landing rather than adjective count or shot scale.
3. Microexpression design was applied after timing lock and did not alter any shot or group duration, shot count, dialogue pace, or group boundary.
4. If expression is itself a source-defined plot event, any duration reconsideration was explicitly returned to the planning stage; the microexpression module did not change timing directly.
5. Every character-visible shot has a locally justified `低/中/高` emotion-event classification; the group level was not copied mechanically onto all shots.
6. Final complexity is the lower of locked-duration capacity and event demand, matching the matrix. Long low-event dialogue remains low; short high-event reactions are reduced rather than accelerated or extended.
7. Each shot uses no more changes than its final complexity, concurrent dialogue/action, framing, and visibility can carry.
8. Multiple simultaneous facial changes are treated as a coordinated leak, not separate artificial time units.
9. Every retained change has a concrete trigger and visible landing; static emotion labels and unordered large-emotion stacking are absent.
10. Surface/true-emotion contrast is supported and translated into visible behavior rather than invisible psychology.
11. Dialogue-performance reduction still passes: no clause-by-clause decoration, repeated gesture, or full expression arc on every speaker.
12. Facial detail matches the framing and visibility; zero-character, prop-only, rear-view, occluded, or wide shots are not forced to display unreadable facial changes.
13. Adjacent shots and groups preserve the character's inherited emotional state, control attempt, trigger, intensity, and aftermath unless the source supplies a new cause.
