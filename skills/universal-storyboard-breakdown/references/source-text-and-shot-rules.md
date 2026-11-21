# Source Text And Shot Rules

These rules are mandatory for `universal-storyboard-breakdown`. Apply them before producing any preview, shot table, or final video-generation prompt.

For all script work, first apply [long-text-workflow.md](long-text-workflow.md): preserve/index the source, review classifications, and check the actual rendered dialogue using the supplied scripts. Keep source subtitle markers and non-audible translations only in the working ledger, outside final shot fields. Its batch, final-tail-group and same-job continuation rules govern those interfaces. For multi-episode routing also apply [full-script-mode.md](full-script-mode.md). Per-shot speech/action rules below still apply, and required action coverage needs separate content review.

## Table Of Contents

- [1. 源文本保留规则](#1-源文本保留规则)
- [2. 字幕处理规则](#2-字幕处理规则)
- [3. 时长与节奏](#3-时长与节奏)
- [3A. 分段脚本格式](#3a-分段脚本格式)
- [3B. 对话表演减量与单角色格式审核](#3b-对话表演减量与单角色格式审核)
- [3C. 剧本动作与人物对话时序匹配](#3c-剧本动作与人物对话时序匹配)
- [4. 开场钩子](#4-开场钩子)
- [5. 景别与视角](#5-景别与视角)
- [5A. 人物—动物高低差关系镜头](#5a-人物动物高低差关系镜头)
- [5B. 组内与跨组相邻镜头景别切换](#5b-组内与跨组相邻镜头景别切换)
- [5C. 画幅与构图](#5c-画幅与构图)
- [5D. 连续三镜主体轮换](#5d-连续三镜主体轮换)
- [5E. 分镜使用规则](#5e-分镜使用规则)
- [6. 群像与人群反应](#6-群像与人群反应)
- [7. 声音与台词表演](#7-声音与台词表演)
- [7A. 双语剧本英文主声轨](#7a-双语剧本英文主声轨)
- [8. 提示词清洁规则](#8-提示词清洁规则)
- [9. 视觉参考资产规则](#9-视觉参考资产规则)
- [10. 提示词污染与视觉代偿审核](#10-提示词污染与视觉代偿审核)
- [11. 交付前的质量检查清单](#11-交付前的质量检查清单)

## 1. 源文本保留规则

- Treat source `VO`, `旁白`, and role dialogue as locked text.
- Do not rewrite, summarize, polish, modernize, add, delete, replace, or reorder any source dialogue, VO, or narration.
- Preserve original punctuation exactly in locked audio fragments.
- A line may be split across multiple shots, but the original words and order must remain unchanged.
- Do not invent hook narration such as `女帝登基` unless that exact text exists in the source script.
- Use the resolved mode's per-shot cap when splitting a long line: `3.5秒` in `15秒模式`, or `5.0秒` in `30秒模式`. Split only at a natural phrase boundary supported by an action milestone, emotional turn, spatial reveal, or camera-intention change. Prefer two consecutive shots when the complete delivery fits within twice the applicable cap (`7.0秒` or `10.0秒`); if two shots are still insufficient, continue splitting at additional natural boundaries or move the group boundary. Do not exceed the applicable cap, shorten source text, or rush delivery.
- Each group may contain only the source dialogue/VO/narration that belongs to that plot range. Do not pull later lines forward to strengthen the hook.
- When English and Chinese are paired versions of the same source line, lock English as the sole audible main track. Preserve the Chinese pairing in the internal source ledger as translation/subtitle reference, but do not speak, time, or lip-sync it. Do not rewrite the English line.

## 2. 字幕处理规则

- Source `【字幕：...】` markers are post-production editing elements.
- Do not write subtitle markers or subtitle text into shot fields, per-shot video prompts, combined video prompts, narration, dialogue, or screen text.
- Use subtitle text only as reference for character identity or plot state.
- Express the actual image through composition, action, blocking, props, and scene relationships.
- Do not ask the video model to generate readable Chinese subtitles. Subtitles should be added during post-production.
- Source subtitles are still part of the script record, but must not be treated as VO, narration, spoken dialogue, or generated on-screen text.

## 3. 时长与节奏

- In every mode, time and group each original episode separately. Group numbers and target time restart per episode, while a resumed partial episode keeps its checkpoint. Never move source text across an episode boundary to meet a group target or repair shot variation. Only the last incomplete episode group may use the shorter real total defined in `long-text-workflow.md`; its shots still obey the selected cap and short-shot rules. These qualifications also apply to the timing checklist below.
- Resolve the group-duration mode from the current request before timing. Use `15秒模式` by default: target `15.0秒`, total `14.5-15.5秒`, and cap each shot at `3.5秒`. Use `30秒模式` only when the current request explicitly asks for `30秒一组`, `30s一组`, or an unambiguous equivalent: target `30.0秒`, total `29.5-30.5秒`, and cap each shot at `5.0秒`. A user- or platform-supplied exact duration or tolerance may override the group-total tolerance but not the selected per-shot cap.
- Determine shot count only after timing the locked source speech and identifying complete action chains. Do not target a fixed number of shots.
- Estimate Chinese speech at `3.5-8字/秒`: about `3.5-6.2字/秒` for slow or suppressed delivery, `4.2-7.0字/秒` for normal delivery, and `5.0-8.0字/秒` for urgent delivery. These ranges apply to both 15-second and 30-second modes; choose a content-matched rate within the range, with the upper endpoint as a cap rather than a required speed. Count spoken Chinese characters and spoken numbers/letters; exclude role labels and non-spoken punctuation from the character count.
- For a bilingual pair, ignore the Chinese-rate branch and time the English main track from audible words plus punctuation/performance pauses. Use a content-matched English delivery around `1.8-2.2词/秒` for slow or suppressed speech, `2.2-2.8词/秒` for normal delivery, and `2.8-3.3词/秒` for urgent delivery. Count contractions and hyphenated spoken units as naturally uttered words; exclude role labels and non-spoken production notes.
- Add audible pause time after calculating character delivery: comma or short breath about `0.15-0.3秒`; period, question mark, or exclamation landing about `0.25-0.5秒`; ellipsis, choking, or deliberate hesitation about `0.4-0.8秒`. Use the performance note to choose within the range.
- Before timing, apply [3C. 剧本动作与人物对话时序匹配](#3c-剧本动作与人物对话时序匹配) to the dialogue and surrounding visual descriptions. Set duration from the resulting speech/action timeline: add sequential phases, count an overlapping interval once, and use the longer duration only when one activity's interval is fully contained in the other. Retain non-overlapping lead-ins, tails and source-required pauses.
- Lock shot duration, shot count, and group boundaries before applying [microexpression-and-emotion-intensity.md](microexpression-and-emotion-intensity.md). The microexpression module must fit its design into that lock and has no authority to lengthen, shorten, split, merge, or redistribute shots. Only when the source makes the expression itself a plot event may the beat return to the storyboard-planning stage for a new explicit timing decision.
- Cap every shot at the resolved per-shot maximum: `3.5秒` in `15秒模式`, `5.0秒` in `30秒模式`. Do not distribute durations evenly; assign each shot only the time required by its locked speech and visible action unit.
- Keep a continuous action chain in one shot when initiation, contact/change, and visible result fit within the resolved cap. Do not cut between reaching and touching, turning and seeing, lifting and placing, running and stopping, or another indivisible action pair.
- When a continuous action chain exceeds the resolved cap, split only after a completed internal action milestone with a visible result. Continue the next shot from that exact result without resetting screen direction, character position, posture, eyeline, or prop state.
- Split a shot only at a real speaker change, completed action milestone, emotional turn, spatial reveal, or camera-intention change. A long line may cross shots only at a natural phrase boundary that coincides with such a visible change.
- Define a short shot as any shot under `2.5秒`. Allow it only when the shot contains locked source dialogue/VO/narration whose natural audible delivery, including its pause, is under `2.5秒`.
- Do not create a short shot with `无` in the source-text field. Merge a silent reaction, insert, action landing, or transition into the preceding or following shot while preserving the continuous action.
- Do not pad a short spoken line to an arbitrary standard duration, and do not rush a longer line to manufacture a short shot. The duration must remain credible for the stated delivery.
- Make the sum of all shots equal the reported actual group duration. Keep that sum within the resolved range (`14.5-15.5秒` or `29.5-30.5秒`) unless the user or target platform supplies a different tolerance; move whole lines and continuous actions across group boundaries instead of cutting them arbitrarily.
- Long narration or dialogue may be performed across two consecutive shots when its natural delivery exceeds the resolved cap but fits within twice that cap (`7.0秒` in `15秒模式`; `10.0秒` in `30秒模式`). If two shots still cannot hold the natural delivery, use additional shots. In `30秒模式`, any line whose natural delivery exceeds `5.0秒` must be split at a natural semantic node; never accelerate or rewrite it. Preserve the original text, order, punctuation, credible pace, and action-state continuity completely.

## 3A. 分段脚本格式

Use one of the following block formats for every shot inside `分段脚本`. Select the shot's use under [5E. 分镜使用规则](#5e-分镜使用规则), then count visible characters before choosing the format. Over-the-shoulder shot/reverse-shot inherits single-character design rules, but visible foreground shoulders/backs still count toward the format. Do not use a Markdown table for shots.

Multi-character shot, or pure prop/detail shot with a画外 anchor:

```markdown
【单镜头1】X.X秒
**镜头描述**：
- **镜头与人物的位置关系**：中心锚点角色：角色A。角色A位于画面中的位置、朝向与视线终点；角色B位于角色A的左/右、前/后、上/下或高/低位置，并说明前景/中景/背景与距离关系。
- **镜头机位**：镜头位于中心锚点角色A的正面/侧面/背面/肩外侧，从大远景/远景/全景/中景/中近景/近景/特写/大特写中选择一个标准景别，机位高度，俯仰/侧向角度，拍摄方向，运镜方式，焦点主体。
- **画面简介**：从动作发起到接触、变化和可见结果的连续过程；必要的表情、道具互动、环境反应、光线落点和画面转折。
**音效/现场声**：只写现场声、人声、动作声、环境声、必要静默。禁止背景音乐/BGM。
**字幕/角色台词/旁白**：说话者标记：锁定主声轨原文片段
```

Single-visible-character shot, including one visible person or one visible animal:

```markdown
【单镜头1】X.X秒
**镜头描述**：
- **画面简介**：中景，平视侧前方固定拍摄，焦点落在角色上半身；可生成的背景环境，唯一可见角色在背景中的位置、朝向与状态，从动作发起到接触、变化和可见结果的完整过程，以及必要的道具互动、环境反应和光线落点。
**音效/现场声**：只写现场声、人声、动作声、环境声、必要静默。禁止背景音乐/BGM。
**字幕/角色台词/旁白**：说话者标记：锁定主声轨原文片段
```

- If exactly one character or animal is visible, `镜头描述` must contain only `画面简介`. Omit `中心锚点角色`, `镜头与人物的位置关系`, and `镜头机位`. Treat off-screen voices as non-visible; a shot can still use the single-character format when only one character is on screen.
- A single-character `画面简介` must begin with exactly one standard shot size, a basic camera angle, a fixed or simple moving-camera instruction, and the focus subject. End that concise camera-language clause with a semicolon, then state the filmable background, the sole visible character's position/orientation/state, relevant props and light, and the complete action result. Do not add a separate camera field or overload the opening with detailed lens or rig specifications.
- Parse the raw scene heading before writing `画面简介`, but keep the full location label internal. Do not start the paragraph with that label or with `夜里的/白天的 + 场景标签`. Choose only the current shot's visible micro-setting—surface, active prop, concealment, doorway/exit, obstruction, or practical light—and do not paste the scene number or cast list into the paragraph.
- Translate continuity locks into visible facts. Write the actual posture, eyeline target, prop state, or location instead of `承接上一镜`, `既定信息对象`, `持物结果`, `落位`, `支撑点`, or similar workflow language.
- Prefer one compact multi-clause sentence or two to four short sentences with periods and commas. Do not pad a concrete one-sentence description. Reject checklist-like semicolon chains and generic fillers such as `空间边界清楚` or `主要通行方向保持畅通`.
- If two or more characters or animals are visible, use all three labeled subfields in this exact order: `镜头与人物的位置关系` → `镜头机位` → `画面简介`.
- In a multi-character shot, `镜头与人物的位置关系` must begin with `中心锚点角色：角色名。` Select exactly one visible person or animal who carries the main action, speech, reaction, or narrative focus. State that anchor's screen position, facing direction, and eye-line endpoint first, then locate every other visible character relative to it. Do not change coordinate origins within the shot.
- For a pure prop/detail shot with no visible character, keep the three-part format, write `中心锚点角色：角色名（画外）。`, and locate the prop along that role's facing axis.
- In a multi-character or pure prop/detail shot, `镜头机位` must state the camera position relative to the same center anchor, then give exactly one standard shot size, height, angle, direction, movement, and focus subject.
- `画面简介` must state the concise visible process from action initiation through contact/change and result. In multi-character shots, do not restate camera geometry. In single-character shots, integrate the concise camera-language clause, background, and character state into this one field without adding a separate camera field.
- `音效/现场声` may include only live/production sound, human voice, action sound, environmental sound, or necessary silence. Do not write background music or BGM.
- `字幕/角色台词/旁白` records the audible source text. Every audible line, even a single VO or narration line, uses `SPEAKER: exact fragment`, matching the reviewed ledger; multiple fragments appear on separate lines in playback order. Preserve dialogue, VO and narration exactly. A silent field is exactly `无`.
- If the source includes `【字幕：...】`, retain it only in the internal source ledger as post-production subtitle reference. It must not enter the rendered source-text field, `镜头描述`, per-shot visual prompts, the internal combined-prompt assembly, or generated on-screen text instructions.
- If the shot has no source text, write `无`.
- After every group, complete the following mode-aware self-check internally. Do not output it in the standard final deliverable unless the user explicitly asks to see audit details:

```markdown
**内部自检（不对外交付）**：分组模式与目标时长；实际总时长；已确认画幅比例与方向；画幅构图审核；核心人物/手部/活动道具/接触点/出入画安全；镜头数量；逐镜语言估时；双语剧本英文主声轨审核（不适用则写不适用）；单镜头均不超过当前模式上限（15秒模式=3.5秒；30秒模式=5.0秒）；长台词自然拆镜；短镜头均有短台词依据；连贯动作按完整里程碑衔接；对话表演减量审核通过；连续三镜主体滚动窗口审核；反馈镜头修复位置与新主体；单角色场景主体轮换豁免（无则写无）；情绪强度等级与判定依据；关键微表情镜头数量；逐镜情绪事件等级；逐镜时长×情绪事件等级矩阵结果；微表情未改动镜头时长/镜头数/组边界；多个同时变化未机械拆时；表情作为剧情事件的规划层例外（无则写无）；逐镜可见角色数量已核对；单角色镜头仅含画面简介、开头含标准景别/基础角度/运镜或固定机位/焦点且分号后包含背景、角色与完整动作；多角色镜头中心锚点唯一、人物相对位置与机位同锚点、三段式模板合规；组内景别：标准景别序列及每一对相邻镜头的通过/豁免通过/失败结果，豁免写类别与实际依据，角度豁免写可见机位差异，单镜组写组内无相邻镜对；跨组景别衔接：确无相邻前组写无前组，有前组写上一组末镜=标准景别、本组首镜=标准景别及通过/失败，未知边界写不可核对，不使用组内豁免；前2秒钩子；景别统计；近景/特写占比；大脸特写次数及依据；连续近景检查；人物出场/情绪比例例外依据（与组内景别豁免分别核对）；视角；原文保留；语速；空镜；光线情绪匹配；光线环境匹配；光线连续性；已完成光色优化；无BGM；无静态外观污染。除非用户明确要求，最终交付不得输出这一整段。
```

- Fill the self-check with concise results, not an empty template. State how many shots used the single-character format and how many used the multi-character three-part format; confirm the dialogue-performance audit, name any source-mandated strong-performance exception, and record the normalized size sequence, every within-group adjacent-pair result and exemption evidence, and adjacent-group boundary sizes under section 5B. `无前组` does not exempt the first group's internal pairs from checking. Audit focal-subject rotation, close-shot ratios, and within-group size exemptions separately; none waives the cross-group size requirement.

## 3B. 对话表演减量与单角色格式审核

Apply both audits after drafting the shots and before lighting optimization. Follow [review-mechanisms.md](review-mechanisms.md) for the full pass/fail procedure.

- For every shot carrying dialogue, preserve the locked line and plot-essential action, then remove performance that exists only to decorate each clause: repeated eyebrow changes, lip emphasis, multiple hand beats, pacing without relocation purpose, repeated pointing, and redundant reaction escalation.
- Prefer one restrained visible state or one necessary action per dialogue shot. Preserve the speaker's source-supported emotional intent through a readable cue and concrete vocal delivery under section 5E; reduction must not make every line emotionally neutral. Keep stronger acting only when explicitly required by the source, when it completes a causal action, or when it marks a decisive emotional turn. Record the exception in `分镜自检`.
- Do not remove source-mandated action, speaker identity, necessary eye-line, prop contact, blocking change, danger response, or emotional climax merely to reduce acting.
- Count visible people and animals after the performance reduction. Exactly one visible character uses only `画面简介`, with concise camera language before the first semicolon; two or more visible characters use the three-part anchored format. Re-run the count if a rewrite removes or adds a visible reaction character.
- Fail the format audit if a single-visible-character shot still contains `中心锚点角色`, `镜头与人物的位置关系`, or `镜头机位`; if the opening of its `画面简介` lacks exactly one standard shot size, a basic angle, a fixed or simple movement instruction, or a focus subject; or if the text after the first semicolon lacks background or character description.
- Fail the format audit if a multi-character shot lacks a unique center anchor, relationship geometry, camera setup, or the final `画面简介`.

## 3C. 剧本动作与人物对话时序匹配

在估时、选镜和细化说话情绪之前，对每段人物对话执行本规则；15秒和30秒模式均适用。先理解对话前后的画面内容，再生成与该段动作时序匹配的提示词。

### 先读上下文，再判断动作与台词的关系

- 读取该段台词、角色标签及括号说明、前后关联的画面描述和听者反应。至少检查台词前、后各一个相关画面段；因果尚未闭合时扩展到同一节拍或连续场景。片段位于已提供源文边界时使用实际可用上下文，不能补造缺失动作。
- 区分说话者、动作执行者、动作对象和信息接收者。动作可以由听者或其他在场人物完成，不能因为靠近某人的台词就归给该说话者；人物说出的回忆、计划、威胁或命令，也不自动成为此刻已经发生的画面动作，自述或指控不自动视为事实。
- 按原文明示的“做完后、说完才、边……边……、话音未落、听到某词”等时间/触发线索，结合动作结果、人物认知和可执行性判断。段落在台词前后的位置是参考，不能单凭排版认定串行或并发。
- “站在门口、仍握着杯子、双肩一直紧绷”等持续状态写入当前画面；仅在原文发生进入、握住、松开等变化时计为新动作，不重复执行或额外加时。单纯对白没有关联动作时按普通对白处理，不为分类编动作。
- 时序不明确时，依据已知因果和实际动作条件作最小拍摄推定并记下依据，不能为了塞进时长而默认边做边说。真实矛盾影响关键因果、动作归属或发声能力时，按现有未决项流程只澄清该缺口；独立段落继续。

### 三种情况的编排与提示词

| 判断结果 | 画面与声音如何匹配 | 时间计算 |
|---|---|---|
| **先做再说** | 先呈现动作发起、接触/变化和可见结果；在对应完成点或触发点后才开始该句。画面写“把钥匙放稳后抬眼开口”这样的具体顺序；声音注明动作完成后人声进入。人物尚未看清、拿到或完成前提动作时，不提前说出原文确定依赖该结果的台词。 | 前置动作时间 + 台词自然发声及停顿时间。 |
| **边做边说** | 明确哪一段动作与哪一段台词重叠，以及各自起止和动作落点。画面写“一边卷起绷带一边开口，话音结束时仍在收拢最后一圈”这样的并行过程；动作声与人声按实际重叠关系出现。动作、呼吸、嘴部状态须容许该发声，不能同时安排互相妨碍的口型与动作。 | 按两条时间区间的实际覆盖计算；同起或一条完全覆盖另一条时取较长者，部分重叠只扣除真正重叠的时间。 |
| **说完再做** | 说话阶段保持原来的位置、持物和接触状态；对应台词片段结束后才执行后置动作/反应。画面写“整句说完才推门进入”，声音注明语尾落定后门响和脚步进入；听者反应以真正接收信息的时点为起点。 | 台词自然发声及停顿时间 + 后置动作时间。 |

“话音未落就动手”属于有具体起点的重叠，不能写成整句结束后才动手。若听到句中关键词就开始反应，而后续台词仍在继续，按关键词前后的片段分别判定，反应与后续发声的重叠仍须保留。同一段中有“开盒后说第一句—递出物品时说第二句—说完收手”等混合关系时，按动作里程碑和原台词片段分别判定，不给整段强套一个类别。台词中夹入非口述动作时，保留源文和追溯切片，将动作放到它实际发生的位置，不把括号说明念出来。

### 落实到实际镜头与内部核对

- 在已有工作记录中，为每段对话保留：台词源单元/片段、前后关联动作源单元、动作执行者、时序类别与依据、动作和发声起止/触发点、实际集组镜。混合段记录各阶段；无关联动作记为普通对白。此记录不改变 `source-ledger.json` 或 `storyboard-map.json` 的既有 schema。
- 成品沿用原字段：`画面简介`写具体先后或重叠过程，`音效/现场声`写人声进入/结束与动作声的关系，`字幕/角色台词/旁白`只放锁定原台词。分类标签、源ID和分析表留内部；不要把“先做再说”等标签当作完整提示词或混入台词。需要明确延迟发声时可在画面/声音说明中写镜内时间段，时间说明不作为口述内容。
- 先排时序，再锁镜头时长、镜数和组界；不能让有台词的镜头默认从第0秒开始说，也不能在非零起点后仍把整镜时长全部算作可用发声时间。已计入发声估时的停顿不重复计时，持续状态不另加动作时长。
- 总需求超过当前单镜上限时，保留已判断的时序并遵守第3节的完整动作规则；连续动作仅在已完成的内部里程碑处切分，长台词跨镜同时须在自然语义边界并伴随允许的可见变化，不能仅到达断句点就切断伸手到接触等不可分动作。后镜继承真实完成状态。先后关系不能被改成并发以省时，也不能删动作、改台词或强行加速。静默不足2.5秒的动作段应与邻接镜整合，保留其在台词前后的原位置；自然短台词仍可独立成短镜。
- 主体轮换或过肩反打只改变观看对象，不改变动作与发声的时间关系。切到听者时原声归属不变，听者不能提前反应、代为说话；必须可见的接触/动作结果仍须在合适镜头中清楚呈现。跨镜或跨组检查前置动作没有重做、后置动作没有抢跑、重叠阶段没有被重复计算。
- 复核实际成品中的画面、声音和锁定台词是否共同实现这条时间线。文字覆盖及秒数加总通过，只能证明对应程序检查通过，不能证明动作与对白的语义/时序匹配正确。

## 4. 开场钩子

- The first `2秒` are critical. Do not open with a slow wide/establishing shot.
- Open with the strongest readable action, step, prop reveal, movement, POV, relationship tension, spatial reveal, or justified facial reaction. Do not default to a face close-up or large-face extreme close-up merely because the shot is first.
- The first `5秒` should build pressure, curiosity, identity tension, or conflict through action, blocking, shot-scale progression, and visible stakes rather than repeated face close-ups.
- A character's first appearance, identity reveal, or immediate emotional turn may use a close-up or extreme close-up as the hook. Follow it with a spatial or relationship anchor unless deliberate concealment is required by the source scene.

## 5. 景别与视角

- Assign every shot exactly one standard shot size: `大远景`, `远景`, `全景`, `中景`, `中近景`, `近景`, `特写`, or `大特写`. Put it in `镜头机位` for multi-character or zero-character shots and before the first semicolon in `画面简介` for single-visible-character shots.
- Within each group, adjacent shots use different normalized standard sizes by default; matching sizes require a documented exemption under section 5B. Small angle changes alone do not qualify. Across group boundaries, normalized end/start sizes must differ without those exemptions. Audit focal-subject rotation and close-shot ratios separately.
- Use at most one far shot, wide shot, or establishing shot per group unless the user requests slow cinematic pacing.
- Do not use the far/wide/establishing shot as the first shot unless explicitly required.
- In ordinary dialogue, deduction, and action groups, use medium shots, medium two-shots, three-quarter/full action framing, relationship shots, over-the-shoulder framing, POVs, and spatially informative inserts as the main grammar.
- Treat near shots, face close-ups, and large-face extreme close-ups as emphasis. Together they should occupy no more than half the shots in an ordinary group. Use at most one large-face extreme close-up, defined as a face filling roughly `60%` or more of the frame.
- Do not place more than two near/close face shots consecutively in an ordinary group. Break the sequence with a medium shot, two-shot, relationship shot, over-the-shoulder, action framing, POV, or spatial insert.
- Use a face close-up only for a visible purpose: character entrance, identity reveal, decisive reaction, emotional buildup/turn/climax, or an important dialogue landing. Do not give every spoken line its own face close-up.
- Character entrances, identity reveals, or sustained emotional peaks may exceed the ordinary close-shot ratio. Vary shot scale and angle, include a spatial/relationship anchor when practical, and record the exception in `分镜自检`.
- When introducing a character, a detail or facial close-up may precede the reveal, but include a medium, three-quarter, full-body, or relationship shot that establishes posture and space unless concealment is intentional.
- Prefer low angle, high angle, side angle, over-the-shoulder, foreground obstruction, POV, and moderate handheld tension.
- Vary angles for a visible narrative purpose. Only a clearly perceptible change of viewpoint can qualify for the within-group angle exemption; a slight shift, tilt, or different angle label alone cannot.

## 5A. 人物—动物高低差关系镜头

Generic `过肩近景` or `前景A背影压住画面` wording often makes video models assume two equal-height humans. When a person interacts with a dog, cat, bird, rodent, ferret, or another much lower/higher subject, use height-aware framing.

The templates below apply only after a near/close relationship shot is narratively justified. They do not require every human-animal exchange to use close framing and do not override the group-level close-shot limits.

- Use this priority: `视线匹配反打` > `高低位肩外侧反打 / 耳侧前景反打` > `双主体关系镜头`.
- Put the intended clear subject first in the prompt. State its full face/eyes, frame position, approximate frame share, eye-line endpoint, and focus lock before describing the foreground subject.
- State the camera side and height, then state `向下俯拍` or `向上仰拍`. Do not rely on `过肩` alone to imply geometry.
- Keep the foreground fragment small and specific: a human shoulder edge plus a little side-face contour, or an animal ear tip/head-top contour. Target about `10%-15%` of the frame.
- Keep the clear target's full face and eyes visible, usually at `40%-60%` of the frame. Name animal-specific facial features when useful, such as eyes and muzzle, or eyes, beak, and complete head.
- Do not use `前景背影压住画面`, `人物背部占据前景`, or `动物背影` in a positive human-animal prompt. These phrases increase the chance of a back-dominant image.
- If camera height, tilt direction, foreground fragment, or target face cannot be stated cleanly, split the beat into two single-subject eye-line match shots.

Human foreground, animal target template:

```text
镜头与人物的位置关系：中心锚点角色：B。B位于画面中下部约占45%，面向左前上方；A位于B的左前上方，A右肩外缘和少量侧脸落在左前景约占12%，B的视线向上连接A画外脸部。
镜头机位：镜头位于中心锚点角色B的正前方偏右，同时贴近A右肩外侧；高低位肩外侧俯拍近景，机位高于B眼睛且略低于A肩线，向下拍摄，焦点锁定B。
画面简介：B抬起完整头部看向A，正脸、双眼和口鼻保持清晰，A前景轮廓虚化。
```

Animal foreground, human target template (this pair varies size; a genuine within-group shot/reverse-shot may also retain size under section 5B):

```text
镜头与人物的位置关系：中心锚点角色：A。A位于画面中上部，头部及胸部以上入画，面向右下方；B位于A的右前下方，B耳尖和头顶落在右下前景约占10%，A的视线向下连接B。
镜头机位：镜头位于中心锚点角色A的正前方偏左，同时位于B右耳外侧后方，以较宽取景容纳A头部及胸部以上；低位耳侧前景反打中近景，机位低于A眼睛并与B眼睛齐平，向上微仰拍摄，焦点锁定A。
画面简介：A低头回应B，正脸、双眼及肩胸轮廓清晰，B前景耳尖和头顶轮廓虚化。
```

Eye-line match fallback:

```text
镜头A：
画面简介：近景，平视正前方固定拍摄，焦点锁定B面部；B单独位于画面中部，抬头看向画外上方A所在方向，保持完整面部和明确眼神方向。

镜头B：
画面简介：中近景，略低机位正前方微仰固定拍摄，焦点锁定A；A单独位于画面中部，头部及胸部以上入画，低头看向画外下方B，以相反视线方向完成高低位空间匹配。
```

## 5B. 组内与跨组相邻镜头景别切换

- For full-script work, adjacency follows the actual source-ordered shot stream, including available neighboring episodes and batches. Selected nonconsecutive episodes are not adjacent. Unknown intervening shots are an unverified boundary, not permission to invent them; spatial handoffs are separately checked by continuous scene instance.
- In both `15秒模式` and `30秒模式`, compare every consecutive pair inside each group (`1→2`, `2→3`, through `倒数第二镜→末镜`) and every adjacent group boundary (`上一组末镜→下一组首镜`). Within a group, different normalized sizes are the default and matching sizes require a supported exemption below. Across groups, end/start sizes must differ, including scene changes; the within-group exemptions do not apply.
- Read the shot size from `镜头机位` for a multi-character or zero-character shot and from the camera-language clause before the first semicolon in `画面简介` for a single-visible-character shot.
- Match longer labels before shorter labels so `大远景`, `中近景`, and `大特写` are not reduced to their shorter substrings. Normalize compound phrases by their standard label: `中景双人` and `中景反打` both equal `中景`; `过肩近景` equals `近景`.
- **组内同景别豁免（满足任一项并记录依据）：**换人物——实际视觉焦点由一个既有角色转向另一个，只有说话者变化而画面仍跟随原角色不算；换角度——机位方位或高度产生清晰可见的视点差异；过肩正反打——真实切换对应人物、视线方向与前景肩部关系；独处——剧情中该人物确实独处，仅单人入画、对手仍在画外不算独处；情绪高潮——原文支持的高潮反应或情绪峰值需要同景别承接，写明对应事件与表演依据。
- **小角度不豁免：**同主体、同景别，仅略微侧移、轻微俯仰、微小摇移或把“正面”改写为“微侧面”，不能单凭换角度豁免。应说明机位前后差异及其可见结果，如正面转明显侧面、俯视转明显仰视，并保持原轴线与空间连续性；文字不足以证明明显变化时，不认定角度豁免。未指定数值时不擅设固定角度阈值。若另有真实换人物、正反打、独处或高潮依据，可按该项独立判断，不能把小角度本身记成豁免依据。
- These exemptions permit matching sizes within a group; they do not waive source fidelity, shot timing, action/dialogue order, spatial continuity, focal-subject rotation, close-shot ratios, or the need for a purposeful cut. A new shot label, a scene change, an entrance, or a reveal alone is not an additional exemption.
- This is an adjacency rule, not a limit of one occurrence per size per group. `中景→中近景→中景` passes this size check. `A中景→B中景` may pass by a verified character-change exemption; `A中景正面→A中景微侧面` fails when no other exemption applies. `近景→过肩近景` remains the same normalized size and requires evidence of a qualifying change, not merely the word `过肩`.
- If matching sizes fail the applicable rule, first reframe the later shot to a different standard size while preserving its hook and readable action; if unsafe, reframe the earlier shot. Change actual subject coverage and the description together, not merely the size label. Recheck both neighbors of each changed shot, overlapping focal-subject windows, and affected group boundaries.
- If neither shot can change safely, return to storyboard planning and reorganize intact source-speech/action units within the same original episode. Moving a group boundary alone is not exemption evidence or a repair; recheck each actual pair under its resulting within-group or cross-group scope. Do not invent filler shots, actions, solitude, or emotional peaks to force compliance; report an unresolved conflict if no compliant arrangement preserves the source and timing.
- Preserve locked source text, credible duration, action milestones, screen direction, character position, posture, eyeline, prop state, and causal continuity during any repair.
- In the internal self-check, record the normalized size sequence and each within-group pair as `通过` (different sizes), `豁免通过` (matching sizes with category and concrete evidence), or `失败`. For an angle exemption, include the before/after viewpoint and visible difference; do not write only `换角度`. Example: `1→2：中景→中景，豁免通过（换人物，焦点A→B）`. A single-shot group records `组内无相邻镜对` and still checks available cross-group boundaries. Record `跨组景别衔接：无前组` only when no preceding adjacent group exists; otherwise record actual end/start sizes and pass/fail. Unknown boundaries stay `不可核对`; cross-group matching sizes always fail.

## 5C. 画幅与构图

- Resolve the ratio under [aspect-ratio-and-composition.md](aspect-ratio-and-composition.md): use the current choice, the same-job verified manifest, or an explicit delegation to choose; only a new job with none of these needs a ratio question. Independent preprocessing can continue while waiting.
- When the current request explicitly names one or more ratios, normalize and use them without asking again.
- Preserve locked speech, timing, plot order, action milestones, normalized shot sizes, screen direction, posture, eyeline, and prop state when adapting between `9:16`, `16:9`, or another ratio.
- Recompose camera position/distance, screen-space placement, foreground share, look room and tracking for the selected frame while preserving world-space blocking and movement paths. Do not describe a later crop as aspect-ratio adaptation.
- Put the normalized ratio and orientation in `视觉风格` and at the start of the internal combined-prompt assembly; express ratio-specific placement and movement in the existing shot-description fields. Do not add standalone `目标画幅`, `画幅与构图`, or `合成提示词` output fields.
- Keep faces, hands, active props, contact points, entrances, exits, and action results readable inside the selected frame.

## 5D. 连续三镜主体轮换

- Apply a rolling three-shot audit to the complete ordered shot stream, including windows that cross a group boundary.
- Define `镜头主体` as the focal visual character: the sole visible character in a single-character shot, or the center-anchor/focus character in a multi-character shot. The audible speaker may remain off screen and is not automatically the visual subject.
- If three consecutive shots share the same focal character, force one shot to become another established character's feedback shot. This takes priority over giving the speaker a single-character shot. The feedback may use a single-character shot, over-the-shoulder shot/reverse-shot, or a qualifying three-or-more-character blocking shot under section 5E, but its actual focal character must change. Prefer changing the third shot; change the middle shot when the third contains an irreplaceable reveal, prop contact, or action result.
- Keep the original locked main-track line and duration. Let the original speaker continue off screen while the feedback character visibly receives, resists, doubts, recoils from, accepts, or otherwise responds to the beat.
- Preserve group totals, shot count, source order, action continuity, screen direction, positions, eyelines, prop states, emotional carryover, lighting, and target ratio. Recount visible characters and reapply the conditional shot format after the rewrite.
- Re-run overlapping windows after every repair. Do not satisfy the rule with a prop insert, empty environment, or decorative crowd cut; the repaired focal subject must be another plot-relevant established character.
- If the scene objectively contains only one established character, record the sole `单角色场景豁免` internally and do not invent a new character.

## 5E. 分镜使用规则

以下规则同时适用于15秒和30秒模式。先根据可见角色与本镜任务选用镜头，再执行主体轮换、站位连续性、时长和字段审核。

### 可见人数与镜头类型

| 实际可见角色 | 类型与用法 |
|---|---|
| 恰好1名 | **单人镜头**，按该人物的实际站位组织画面 |
| 2名及以上 | **关系镜头**；人物过肩正反打用于主要人物的对话与反馈，多人站位关系镜头用于下述三类任务 |
| 至少3名 | 达到**多人站位关系镜头**的人数门槛；恰好2名不属于这一子类，3名同框也不自动意味着应使用该子类 |

按不同角色计数：可见脸、身体、前景肩背、手、倒影或轮廓均计入其角色，同一角色不因身体与倒影同时出现而重复计数；画外声音不计入。人物与动物沿用同一可见人数规则。0名可见角色保留原有道具/细节镜头规则，不归为单人或关系镜头。

### 单人镜头：站位、说话者与情绪

- 根据人物在空间母版中的真实位置、朝向、视线终点、姿态与动作路径调整机位和画面内容。把门口、桌边、距离与画外交流对象方向写成可见事实；不能为套用单人模板把人物移回居中或重置动作。
- 人物说话时，优先给予对应人物的单人镜头，让说话与该人物的可读表现对应；主体轮换规则优先于这一偏好。需要轮换时可以切向已在场人物的反馈，原说话者继续原台词，按其实际可见情况交代声画关系。
- 说话者在画外时，由声音承载其说话情绪；画面只写可见反馈人物的表情和动作，不让听者代替说话者动嘴，也不把画外说话者不可见的面部表现写入画面。
- 提示词要强化说话时的情绪可读性：在 `画面简介` 中保留符合源文与前态的关键眼神、唇线、下颌、呼吸或姿态表现，在 `音效/现场声` 中写具体声线、气息、重音和语尾。只选当前面部可见度与锁定时长容纳的表现，不必逐项写满。例如压怒可写“视线定在对方方向，下颌绷紧”，声音写“压低声线，句尾咬字稍重”；锁定台词原文不变。
- 情绪强化表示更具体、可见、可听，不自动提高情绪等级或增加动作数量。继续遵守对话表演减量、微表情时长矩阵与近景/特写配额；单人镜头不等于面部特写。

### 人物过肩正反打：沿用单人镜头设计

- 每一侧都围绕一个主要人物，沿用上述站位、说话者优先、情绪表达和主体轮换规则。清晰的说话/反馈人物是视觉焦点；前景肩背负责交代对位关系，不因占据前景就成为主体。
- 机位与正反方向服从既有站位、轴线、视线、高低差和动作承接。正打、反打各自作为一个镜头进入连续三镜窗口，不能把整对视为一个镜头。
- “沿用单人规则”指设计与表演，不改变人数和字段：只见目标人物时用单人 `画面简介`；同时可见另一人的肩背等身体片段时，属于关系镜头，使用三段式，并以主要说话/反馈人物为唯一中心锚点。

### 多人站位关系镜头：至少3名可见角色

在已有剧情人物达到人数门槛，且符合以下任一任务时使用：

1. **主体轮换修复**：单人或过肩方案无法在保留必要动作与空间承接的同时完成主体轮换，用多人关系保留动作参与者，并让另一名已建立角色的反馈成为真实焦点。仍需通过三镜窗口；`A/A/A`不能仅靠第三镜加入B、C或拉远变成合格。
2. **人物大幅度动作**：人物的冲出、扑挡、跨越、后退等原文动作需要同时看清其与其他人物的距离、阻挡、接触或结果，用多人关系画面呈现完整动作里程碑。
3. **人物站位调度**：人物进退、换位、绕行或其他已有走位改变相互关系时，用多人关系画面交代起始位置、移动路径、关键交汇/接触和结束位置，供后续镜头承接。

三类任务是任选其一，不必同时发生。始终只选一个中心锚点和主要视觉焦点；写清其他人物相对位置与动作关系，不给所有人平行添加表演。普通静态对白优先用单人或过肩正反打，不因场内有三人就把他们全放进画面。恰好两人的必要接触与走位仍须完整呈现，可保留必要的双人关系画面，不称为“多人站位关系镜头”，也不为凑人数新增角色。大幅度动作与站位调度都须来自源文或必要动作承接，不能为了使用此镜头而编造动作；15秒/30秒单镜上限与完整动作规则不变。

## 6. 群像与人群反应

- Group scenes must not show only the protagonist and the speaker/announcer.
- Insert officials or crowd reactions when needed: lowered eyes, swallowing, tightened fingers, shoulders sinking, exchanged glances, hesitation before kneeling, visible fear, or awe.
- Reaction shots must be concrete and visible, not abstract.
- If duration allows, reaction shots may carry continuing source VO.
- In crowd scenes, do not force every named character into the same frame unless necessary. Prefer one main face/action, foreground back/shoulder obstruction, background silhouettes, local hand/foot/prop inserts, single-person reaction cuts, or off-screen sound/direction.
- Flag shots that mention four or more named characters and use `围住`, `包围`, `全部`, `所有人`, or `同时` without one clear main visual focus.

## 7. 声音与台词表演

- Sound notes may describe how a line is spoken, but the actual spoken words must exactly preserve the source text.
- Use punctuation to control performance rhythm:
  - `，`: pause, breath, urgency.
  - `……`: hesitation, choking, emotional pause, broken speech.
  - `~`: lighter, brighter, more playful tone.
- Prefer concrete voice delivery over abstract emotion labels.
- Avoid labels like `悲伤地说` or `愤怒地说`.
- Prefer audible, performable descriptions such as:
  - `声音有点发颤，语速慢下来`
  - `声音压着怒气，咬字变重，一字一句`
  - `声音很轻，尾音发虚`
  - `呼吸很轻，断断续续`
  - `声音压低，语速很慢，最后几个字带着一点冷笑`
- Add scene/person state when useful, such as `昏暗的房间`, `雨里等待很久`, `红着眼眶`, `躲在门后，害怕被发现`, `强忍着眼泪`.
- Only write visible/audible state. Avoid invisible psychological descriptions.
- Do not add background music or BGM descriptions.

## 7A. 双语剧本英文主声轨

- Detect paired English/Chinese versions by role, sequence, and semantic match before timing.
- Use English as the sole audible main track for every paired line. Derive shot duration, pauses, emphasis, and lip sync from the exact English wording.
- Keep Chinese in the internal source ledger only as translation or post-production subtitle reference. Do not speak English and Chinese consecutively or simultaneously, do not count both versions, and do not request generated Chinese text.
- Render the final record exactly as `英文主声轨（锁定）— ROLE: Exact English source line`.
- When a beat exists in only one source language rather than as a pair, preserve that available line as the locked main track. Do not translate, backfill, or fabricate the absent language.

## 8. 提示词清洁规则

- Avoid abstract or human-only descriptions that do not translate into visuals:
  - `她不是……而是……` comparisons.
  - Invisible psychology such as `内心嫉妒成狂`.
  - Positive prompts that say `不出现某某角色` unless there is a dedicated negative prompt field.
  - Broad emotion labels without visual/action support.
- Prefer concrete visible/audible details:
  - posture, gaze direction, hand movement, breathing, hesitation, stepping back, falling, turning.
  - camera angle, lens, push/pull/pan/tracking/handheld/over-the-shoulder/POV.
  - spatial relationship and blocking.
  - prop contact and action result.
  - lighting changes; smoke, dust, blood, or similar elements only when visible and narratively necessary.

## 9. 视觉参考资产规则

- Before storyboard drafting, follow [global-asset-control.md](global-asset-control.md): match supplied character/location/prop assets or first deliver their prompt overview tree. Preserve supplied matches and prepare only missing variants; record reference inspection, intended use and actual availability.
- Suppress repeated static appearance only for the currently selected, inspected and usable asset version. Character identity does not lock one costume for the entire story; costume, wetness, wounds, hairstyle changes and prop states follow source events and narrative time.
- With working reference bindings, name the actual corresponding asset and add the current required changes. Without a binding channel or image, write the necessary registered static design into the text; a file name, internal ID or `@资产名` alone is not proof of a valid reference.
- For video generation, select the fewest relevant compatible references per group/scene segment and record actual submissions. If `@资产名` is explicitly supplied, resolve those references; report missing or incompatible versions instead of silently submitting different images or unrelated assets.
- Scene variants inherit one location geometry. Create only required day/night/weather/damage versions; a new scene instance resets blocking from its evidence, not the layout, and does not automatically create another asset image.
- New character identity/costume asset design prompts use a neutral pose and pure white background by default. This applies to asset design cards, not user-provided images or story shots. Scene assets emphasize architecture; ordinary clutter stays in the scene/shot unless it needs separate continuity control.

## 10. 提示词污染与视觉代偿审核

Treat these as core review rules for storyboard prompts and Seedance-ready prompts.

### A. 提示词污染 / 关键词联想陷阱

- AI video/image models may associate certain keywords with stereotyped visual packages. Even negative wording can activate the unwanted object.
- Unless the shot truly needs them, do not put pollution keywords into the positive main prompt.
- Common pollution patterns:
  - Negative wording: `不要/禁止/不能/不出现/避免 + visual object`.
  - Identity words: `护士`, `医生`, `警察`, `士兵`, `杀手`, `黑帮`, `教父`, `清洁工`, `女仆`, `修女`, `公主`, `女王`, `CEO`, etc.
  - Prop words: `手机屏幕`, `游戏`, `屏幕`, `UI`, `文字`, `地图`, `摄像机`, `箭头`, `血`, `伤口`, `绳索`, `武器`, `垃圾桶`, `徽章`, etc.
  - Director/internal words: `本组目标`, `关键衔接规则`, `为下一组`, `留反打`, `提升抽卡率`, `避免重复`, `空间关系参考图仅用于...`.
  - Literary metaphors: `像`, `如同`, `仿佛`, `命运`, `气息`, `吞噬`, `破碎感`, `猎物感`, `水母`, `蝴蝶`.
- Rewrite with concrete visible behavior, body state, camera angle, object orientation, and sound.
- Prefer positive target descriptions. Put necessary exclusions in a negative-prompt field if the platform provides one, not in the main prompt.
- Examples:
  - Instead of `男生打游戏`, write `男生在地铁座位上双手横向拿着手机，手机背面朝向镜头，屏幕朝向人物`.
  - Instead of `男生修图`, write `男生坐在桌前看向显示器背面，右手放在鼠标上`.
  - Instead of `八块腹肌`, write `肩宽腰窄，腹部线条紧实`.

### B. 视觉代偿 / 抽象关系陷阱

- Models often compensate for abstract relationships by adding body parts or contradictory viewpoints.
- High-risk words: `背对`, `望向`, `注视`, `凝视`, `看见`, `意识到`, `感觉到`, `对视`, `对峙`, `四目相对`, `视线交锋`, `互相看着`, `面对面`.
- These words are not absolutely forbidden, but must be paired with camera/orientation anchors.
- For two-person or multi-person orientation, use one lightweight anchor:
  - `过肩反打（限高度接近的主体），前景A肩部外缘和少量侧脸虚化，B正脸回应`.
  - `侧面对峙，A在左面向右，B在右面向左`.
  - `单人反应切，A看向画外B`.
  - `A的POV，B正面逼近`.
- If a shot contains `对视/对峙/四目相对/视线交锋/互相看/面对面/凝视对方` without an orientation anchor such as `过肩/侧面/POV/画外/前景肩缘/左面向右/右面向左`, flag it as `双人朝向风险：缺少朝向锚点`.
- If a human-animal shot contains bare `过肩近景`, `前景背影压住画面`, or lacks camera height, tilt direction, foreground fragment/share, target face/share, eye-line endpoint, or focus subject, flag it as `人兽高低差构图风险：主体可能被背面或前景遮挡`.
- Do not force every shot to contain complex blocking. One short anchor is enough.

## 11. 交付前的质量检查清单

For every script job, first apply the default long-text workflow's scope-aware source and rendered-dialogue checks plus separate action/state review, including the tail-group exception. Read ratio, duration, style, and language choices from the locked manifest on same-job continuation; a new job uses the entrypoint parameter policy, including explicit delegation when supplied. Do not create an extra confirmation checkpoint just because an episode or batch has finished.

Before drafting, also complete the asset route and usage table. At final review, verify correct costume/time/prop versions, actual reference availability, unchanged location geometry across lighting variants and source-supported state transitions. Keep the asset tree and binding audit separate from the shot fields.

Before delivery or a user-requested preview, check the applicable items. Record actual results compactly; do not copy the full checklist into the deliverable or create an approval pause:

- Was the ratio resolved before timing/grouping/drafting from the current choice, same-job verified manifest, user answer, or explicit delegation, with its basis saved?
- Do `视觉风格`, ratio-specific shot geometry, and every combined prompt use the same normalized ratio and orientation without standalone `目标画幅` or `画幅与构图` fields?
- Is each shot natively recomposed for that ratio rather than described as a later crop?
- Are faces, hands, active props, contact points, entrances, exits, eyelines, movement lead space, and visible action results readable in the target frame?
- If several ratios were requested, are complete variants clearly labeled while locked speech, timing, plot order, action milestones, normalized shot sizes, screen direction, posture, eyeline, and prop state remain identical?
- Does the reported actual group duration match the resolved mode: `14.5-15.5秒` in `15秒模式`, or `29.5-30.5秒` in `30秒模式`, unless the user or platform specified another group-total tolerance?
- Does the first `2秒` use the strongest readable action, prop, movement, POV, relationship tension, spatial reveal, or justified facial reaction instead of defaulting to a slow wide shot or large-face close-up?
- Do the first `5秒` establish pressure, curiosity, or identity tension?
- Does every shot duration cover the natural audible delivery plus the complete visible action?
- Is every shot at or below the resolved cap (`3.5秒` in `15秒模式`; `5.0秒` in `30秒模式`), with unequal durations allowed according to language and action needs?
- If a long line exceeds the resolved cap, is it split at natural semantic and visible-change boundaries—preferably into two shots when it fits within twice the cap (`7.0秒` or `10.0秒`), and into more shots when it does not—without rushing or rewriting the source?
- Does every shot under `2.5秒` contain locked short dialogue/VO/narration with a matching language-duration estimate?
- Are there no sub-2.5-second shots whose source-text field is `无`?
- Are continuous action chains kept in one shot when they fit within the resolved cap, and otherwise cut only after completed visible milestones with screen direction, pose, eyeline, and prop state preserved?
- Does the sum of all shot durations equal the reported actual group duration?
- Is there at most one far/wide/establishing shot?
- Does every shot state exactly one standard shot size in its designated camera location?
- Have all within-group adjacent pairs been normalized and checked for different sizes or a supported section 5B exemption? Does every matching pair record its exemption category and actual evidence, rejecting small angle changes alone? Do actual framing and coverage match the size labels?
- Does shot selection follow section 5E: one visible role is single-character, two or more is relational, and a multi-character blocking shot has at least three visible roles plus a rotation-repair, large-action, or blocking task? Are foreground fragments counted and zero-character shots kept separate?
- Do speaker-centered single and over-the-shoulder shots respect established positions, prefer the actual speaker where rotation permits, and make the source-supported speaking emotion concrete without exaggerating performance or exceeding timing/close-shot limits?
- Does every rolling three-shot window, including across group boundaries, avoid three occurrences of the same focal character under the exact pass condition in review-mechanisms.md? If a run was repaired, is the alternate focal subject another established plot-relevant character rather than a prop/empty cut, with the original speaker allowed to continue off screen and all timing/spatial/prop continuity preserved?
- If a three-shot run occurs in an objectively single-character scene, is the sole exemption recorded internally without inventing a new character?
- In an ordinary group, do near shots, face close-ups, and large-face extreme close-ups occupy no more than half the shot count?
- Is there at most one large-face extreme close-up in an ordinary group, and does every face close-up have a visible narrative or emotional purpose?
- Are there no runs of more than two consecutive near/close face shots in an ordinary group?
- If a character entrance, identity reveal, or emotional peak exceeds the ordinary close-shot ratio, is the exception justified and balanced by scale/angle variation plus a spatial or relationship anchor when practical?
- Does it use low angle/high angle/side/over-the-shoulder/POV rather than repeated eye-level medium shots?
- Do crowd scenes include official/crowd reactions when needed?
- Are silent reactions, inserts, action landings, and transitions merged into adjacent shots instead of being used as standalone short shots?
- Are source VO/dialogue/narration fully preserved with exact original punctuation, while subtitle markers are excluded?
- For paired bilingual lines, is English the sole audible main track used for timing and lip sync, with the exact final notation `英文主声轨（锁定）— ROLE: ...`, while Chinese remains internal translation/subtitle reference and is neither voiced nor counted again?
- Does Chinese dialogue/narration fit `3.5-8字/秒` and the selected delivery range (`3.5-6.2字/秒` slow/suppressed, `4.2-7.0字/秒` normal, `5.0-8.0字/秒` urgent)?
- When English is the main track, does its delivery fit the content-matched English word-rate branch and include punctuation/performance pauses instead of using the Chinese character-rate branch?
- Do sound notes describe concrete voice delivery and visible/audible state rather than abstract emotion?
- Has every dialogue shot passed the performance-reduction audit, with decorative micro-expression, repeated gesturing, and clause-by-clause acting removed?
- If a dialogue shot retains strong acting, is it explicitly required by the source, a causal action, or a decisive emotional turn, and is the exception recorded in `分镜自检`?
- Does every group contain exactly one supported `情绪强度等级` (`一级/二级/三级`) plus a concrete trigger/reaction/landing basis?
- Was microexpression design applied only after shot timing, shot count, group boundaries, dialogue pace, and action milestones were locked, with all of those values unchanged afterward?
- If an expression itself is a source-defined plot event, was timing reconsidered explicitly by the storyboard-planning stage rather than changed by the microexpression module?
- Was each readable-face shot assigned a local `低/中/高` emotion-event level, then given a final complexity equal to the lower of duration capacity and event demand: `≤2秒=极简`, `>2且<3秒=低`, `3-5秒=中`, `6秒以上=高` for capacity, with low/medium/high event ceilings? Does long ordinary dialogue remain low and does a short decisive event retain only the matrix-permitted key change(s)?
- Are simultaneous eye, brow, mouth, jaw, breath, or body changes treated as coordinated performance rather than mechanically split into separate time units?
- Does each selected microexpression use a concrete trigger and visible landing, preserve one dominant progression, distinguish any supported surface/true-emotion contrast through visible behavior, and avoid unordered emotion stacking?
- Are facial details omitted or reduced when the face is unreadable, and are multi-character reactions concentrated on the focal/center-anchor character rather than giving every character a full arc?
- If source VO is available and duration allows, does the opening shot use an audio hook?
- Is there no background music/BGM description?
- Does the prompt suppress repeated static appearance only for the inspected, effectively bound current reference version, while retaining necessary baseline text when binding is unavailable and expressing required costume/state changes in either case?
- Does the final prompt avoid pollution keywords: negative visual wording, identity stereotypes, prop traps, internal director notes, and literary metaphors?
- Does `情绪目标` name a concrete current-group audiovisual or performance device, the viewer-facing emotional effect, and any progression or landing, without quoting the source start/end boundaries or using `由……落到……`?
- Is each group classified as `光线与色彩1`, `光线与色彩2`, `光线与色彩3`, or `自定义光线与色彩` using visible environment and emotion evidence?
- Does the lighting-and-color design fit the established location, practical sources, materials, and emotional turn without mechanically copying an ill-fitting reference?
- Do adjacent groups in the same uninterrupted scene preserve light direction, color temperature, contrast, and atmosphere unless a visible transition justifies change?
- Is the optimization integrated into the final prompt without inventing weather, props, materials, smoke, mist, water, debris, or costume details?
- Do abstract relationships such as `对视/对峙/面对面` have lightweight orientation anchors?
- Do human-animal height-gap shots use eye-line match or height-aware shoulder-edge/ear-side framing, with camera height, tilt, foreground share, target face, eye-line endpoint, and focus subject stated? Is `前景背影压住画面` absent from the positive prompt?
- Does every multi-person shot have one clear main visual focus instead of forcing all named characters into the frame?
- Does `分段脚本` use `【单镜头N】` blocks instead of a table, with `镜头描述`, `音效/现场声`, and `字幕/角色台词/旁白` fields?
- Has visible character count been checked after the final dialogue-performance rewrite for every shot?
- Does every single-visible-character shot contain only `画面简介`, with one standard shot size, basic angle, fixed or simple movement, and focus before the first semicolon; background, sole character position/state, props/light, and complete action after it; and no `中心锚点角色`, relationship field, or separate camera field?
- Does every multi-character shot contain `镜头与人物的位置关系`, `镜头机位`, and `画面简介` in that exact order, with one center anchor and no coordinate drift? For a prop-only frame, is the connected role marked as `（画外）`?
- Does every `画面简介` avoid starting with the full or paraphrased scene label, name a concrete current-shot visible detail, and contain a visible state/action/change instead of a generic spatial filler?
- Do the previous group's final normalized shot size and the current group's opening normalized shot size differ, including across a scene change, with any repair preserving source text and spatial/action continuity?
- After size repairs, have both neighbors, affected group boundaries, and overlapping focal-subject windows been rechecked? Does the internal self-check contain each group's size sequence, every adjacent-pair result, and supported within-group exemption evidence, without treating `无前组`, boundary movement, or an unverified exception as a pass?
- Does the internal self-check include target ratio, aspect-ratio composition result, action-safe coverage, timing, action continuity, dialogue-performance audit result, bilingual English-main-track result, three-shot focal-subject windows and repairs/exemption, emotion-intensity level and basis, key microexpression-shot count, per-shot emotion-event levels and duration × event-level matrix results, confirmation that microexpressions did not change timing, any expression-as-plot-event planning exception, single-character/multi-character format counts, source-mandated performance exceptions, adjacent-group boundary sizes, opening hook, shot-size statistics, close-shot audit, source preservation, speech rate, lighting continuity, no BGM, and no static-appearance pollution—and is this self-check omitted from the standard final deliverable unless explicitly requested?
- Does the final deliverable match [final-delivery-format.md](final-delivery-format.md): plain episode title line, seven global-continuity fields, `##` group headings, only the required visible group fields and shot blocks, and a final `负面提示词：` line?
- If a preview file is produced, is it saved under `_待确认预览/` rather than the project root, and returned as a clickable Markdown link using the absolute filesystem path supported by the host?
- Respect explicit user-requested checkpoints and unresolved required parameters; completed batches/assets/episodes do not create additional approval checkpoints.
