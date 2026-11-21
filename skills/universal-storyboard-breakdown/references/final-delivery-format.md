# Final Delivery Format

Use this format for the final user-facing deliverable. Keep timing, emotion-level classification, microexpression matrices, prompt-cleanliness checks, and other audits as internal working records unless the user explicitly asks to see them.

## Default long-text delivery and checking

In all script modes, follow [long-text-workflow.md](long-text-workflow.md) for source indexing, batch records and actual rendered-text checking. Keep source IDs, mappings, program reports and checkpoints outside the prompt body. Each shot has exactly one source-text field. Every audible line, including a single VO or narration fragment, must use `SPEAKER: exact fragment` with the source ledger's speaker label, or the existing bilingual notation. Render multiple fragments one per line in playback order. A silent field is exactly `无`. This permits deterministic extraction without changing the visible field names.

Preserve source whitespace in audio fragments under the [audio-field whitespace contract](long-text-workflow.md#音频字段的源空白与排版): at most one ASCII space after the speaker colon is formatting; remaining leading/trailing whitespace is source text. Do not append Markdown hard-break spaces to audio lines.

Standalone batch files repeat the correct episode title and retain current group numbers so the checker can locate them. When combining batches into a final episode artifact, keep one episode title/continuity block and rerun the checker on that actual combined file. In every mode, the true last incomplete group of an episode may use the default workflow's tail-group rule; all per-shot requirements still apply.

## Full-script delivery extension

For `整本剧本模式`, follow [full-script-mode.md](full-script-mode.md) for scope and records. Apply the format below separately to each requested source episode:

- Start each episode artifact with its own plain title and seven-field continuity block. Preserve the original episode number; never place the whole book under a single episode title or a single shared blocking description.
- If several episodes are delivered in one document, repeat the complete episode format in source order. By default save separate checked episode artifacts, then return their locations and actual completed range.
- At final whole-script delivery, also deliver one separate, consolidated character/location/prop prompt document under [global-asset-control.md section 6](global-asset-control.md#6-全剧最终交付人物场景道具提示词汇总). Include complete copyable prompt text for every required final asset/version, even when references or preliminary cards were supplied earlier. Return its link alongside the whole-script prompts and include it in any delivery index/archive; a name list or links to scattered cards alone do not satisfy this requirement.
- Restart visible group numbering at `第1组` and target time at `00:00` for each episode. Continuing a partial episode retains its existing group numbers and times; only the first batch needs the episode header in a combined artifact.
- The final incomplete group of an episode may report a shorter actual duration under the full-script tail-group rule. Keep the normal group heading and full shot fields; do not move source content across episode boundaries to fill it.
- Keep the whole-script source index, coverage ledger, scene-state registry, revision history, and checkpoint outside the generatable prompt body. A short task-level completion/remaining-range note may accompany files or follow the final group; it is not part of a video prompt. Do not add working audit fields to each group.
- Express the current episode's relevant incoming state and scene instances in the existing continuity fields; express each group's concrete initial conditions and changes in its scene/shot descriptions. Do not replace them with references such as `继承第1集`.
- A shared location appearing at different times must use distinct scene-instance states, even within the same episode. The visible continuity block may list the relevant scene segments inside its existing seven fields; it must not lock every scene to one static position for the whole episode.

## Pre-storyboard asset delivery

Follow [global-asset-control.md](global-asset-control.md) before producing episode prompts. With supplied assets, deliver their usable version bindings and any missing-variant subtree; without assets, deliver a character/location/prop prompt overview tree, complete linked prompt cards and a source-event usage table. Keep these in separate files or clearly separated preceding content, not inside each video's group block. Preserve the exact seven-field episode format below.

Identify text-only designs, inspected files and actual platform bindings accurately. Trees may use project IDs to link cards, but unbound IDs or nonexistent file names cannot stand in for usable reference images. Asset-only requests end with these artifacts; an authorized storyboard request continues from the same baseline without a new default confirmation point.

In episode fields, express selected identity/costume versions in `主要人物`, location geometry/time variants in `空间母版/场景与环境状态`, and current prop state in `关键道具连续性/画面简介`. Each group's `主要主体` follows the compact people → scenes → props format below, including when references are not bound. Keep complete static designs in the separate asset cards/summary and supply needed reference context through the actual delivery channel; short names alone do not prove a binding exists. Keep hashes, paths used only for project tracking and inspection records outside generatable fields. Do not put asset-card white backgrounds, neutral poses or view-sheet layouts into story shots.

The preliminary asset package remains a working baseline. Reconcile it against the actual final storyboards and current versions before compiling the required final summary; keep that summary outside the episode and group prompt format below. Its three sections are `人物提示词`, `场景提示词`, and `道具提示词`, with explicit empty-category notes when appropriate.

When the user requests a Feishu Base asset sync, or the current project has an applicable authorized binding, also follow [Feishu Base asset delivery](lark-base-asset-delivery.md). Keep the local storyboard and standalone prompt-summary deliverables. Report the actual remote target, verified version counts by category, create/update/unchanged results, and any incomplete scope separately; claim sync completion only after reading back the records and complete prompt text. Keep integration configuration and sync reports outside the generatable prompt body.

## LibTV CLI delivery extension

When the user selects LibTV, also follow [LibTV CLI delivery](libtv-cli-delivery.md). Preserve the reviewed Markdown master and, for whole-script delivery, the standalone character/location/prop prompt summary. Derive one platform row per actual shot, with separate first-frame image, video-motion and exact-dialogue fields; preserve original groups and durations. Deliver the local handoff JSON and its comparison report. Keep platform mappings and import status outside generatable prompt text, and distinguish an offline-checked package from an actual import verified by reading back every row. Do not trigger media generation as part of an import-only request.

## Required title

Start with one plain-text title line, with no Markdown heading marker:

```text
第N集｜本集核心冲突或反转标题｜已确认画幅与方向｜15秒一组或30秒一组｜已解析视频质感风格
```

Example:

```text
第1集｜发布会指控与怀表反转｜9:16竖屏｜30秒一组｜写实短剧质感
```

Derive the short conflict/reversal title from the complete episode. Do not use a generic label such as `第一集分镜`.

## Global continuity block

Output exactly these fields, in this order:

```markdown
## 全局连续性
- **主要人物**：
- **空间母版**：
- **人物轴线**：
- **关键道具连续性**：
- **视频质感风格**：
- **视觉风格**：
- **光线与色彩基调**：
```

- `主要人物` gives only role-defining visual and performance facts needed across the episode.
- `空间母版` locks entrances/exits, depth layers, relative positions, and the stable movement routes used by the episode.
- `人物轴线` locks left/right, high/low, facing, eyeline, and crossing constraints.
- `关键道具连续性` states the holder, hand, open/closed or active state, contact point, and the exact end-state handoff needed by the next group.
- Keep internal emotion-continuity notes and general continuity checks out of this block; express only their visible consequences in the seven required fields.

## Shot use and visible-count format

Choose shots under [分镜使用规则](source-text-and-shot-rules.md#5e-分镜使用规则). One visible role is a single-character shot; two or more is a relationship shot. Over-the-shoulder shot/reverse-shot uses single-character subject, blocking and speaking-emotion design, but visible foreground shoulders/backs still require the three-part relationship format shown below. `多人站位关系镜头` requires at least three visible roles and one of the specified rotation-repair, large-action or blocking tasks. Its focal character must still pass the rolling three-shot audit. Express the selected use through existing visual and sound fields; keep classification and reasons internal.

## Group block

Use a second-level heading for every group:

```markdown
## 第1组（目标00:00-00:30；实际30.0秒）

- **生成任务**：
- **主要主体**：人物名（简单服饰描述），人物名（简单服饰描述），场景名（状态），道具名（状态）
- **场景与环境状态**：地点/时段及固定参照布局；本段相关人物相对参照的位置、朝向、视线、姿态/动作阶段、持物/接触与距离关系（含相关画外人物）；人物轴线与摄影机所在物理侧。
- **情绪目标**：
- **视频质感风格**：写实短剧质感 / 高精度3D
- **光线与色彩设计**：
- **视觉风格**：
- **分段脚本**：

  【单镜头1】X.X秒  
  **镜头描述**：
  - **镜头与人物的位置关系**：中心锚点角色：角色A。角色A的位置、朝向、视线终点；其他可见角色相对角色A的前后、左右、高低、景层和距离。
  - **镜头机位**：相对中心锚点角色的机位、标准景别、高度、角度、拍摄方向、运镜和焦点主体。
  - **画面简介**：完整可见动作、人物反馈、道具状态变化、环境反应和结果。
  **音效/现场声**：现场声、角色声音、动作声、环境声或必要静默。
  **字幕/角色台词/旁白**：角色A：锁定主声轨原文片段

  【单镜头2】X.X秒  
  **镜头描述**：
  - **画面简介**：单角色镜头按“标准景别 + 基础角度 + 简单运镜或固定机位 + 焦点主体；背景、角色位置/状态、完整动作和结果”书写。
  **音效/现场声**：现场声、角色声音、动作声、环境声或必要静默。
  **字幕/角色台词/旁白**：旁白：锁定旁白原文片段

负面提示词：
```

### 主要主体：人物、场景、道具简表

`主要主体`用一行按“人物 → 场景 → 道具”排列，各项以中文逗号分隔，名称后使用中文圆括号：

```markdown
- **主要主体**：林岚（米白衬衣、灰蓝长裤），周衡（深蓝西装），医院走廊（白天），病历夹（闭合、林岚右手持有）
```

- 人物写真实角色名，文字资产在括号内写简短服饰及必要衣装状态；两轮交付中已核对的图片绑定按下方规则填写。年龄、五官、身材、长篇外貌设定保留在独立资产资料中。
- 场景和道具使用本组实际名称，括号内简写当前状态。只列实际需要的条目，人物数量不限；无某类需求时省略该类，不为填满示例新增人物、场景或道具。
- 状态对应本组相关场景段的入态或该条目首次出现时的状态；组内变化在对应镜头展开。涉及多个阶段时简短标明对应阶段，不把后续完成态提前作为初态，也不把同一对象的互斥状态混列。
- 此简表不替代`场景与环境状态`中的完整空间初态或逐镜动作、伤势、持物与接触描述；它们须相互一致。独立人物场景道具提示词汇总仍交付完整资产提示词正文。

交付前核对本字段的条目顺序、姓名/服饰、场景/道具状态和实际组镜覆盖，清除复制旧资产卡带来的长外貌段或失效状态。

两轮模式的第二轮在 **主要主体** 后添加 **参考图片**，依次列本组起始站位图、涉及的人物资产图、场景图和关键道具图，写清文件名、用途及涉及的场景段。已核对人物按“人物名（图：资产 ID，当前状态）”简写。参考图确认的静态外观用图承载，镜头继续记录状态变化及必要空间事实。文字补缺的图按组说明。

Do not output these former working fields in the final deliverable: `情绪强度等级`, `情绪强度判定依据`, `光线质感分类`, `分类依据`, `合成提示词`, or `分镜自检`. Continue to calculate and audit them internally before finalizing the visible fields.

Expand the spatial-entry content above into actual natural-language facts under [full-script-mode.md section 3](full-script-mode.md#每组可独立使用的空间初态); do not copy its checklist labels or refer the generator to the episode header. Every standalone group, including a nonadjacent return, carries its current state. Its first shot must agree with that state. Shots completing changes in position, contact or props must describe their results; retain unchanged facts through the scene segment's end without forcing every character into its final shot. For multiple scenes in one group, put each later scene's entry state in that scene's first shot. Single-character shots keep only `画面简介`, including the fixed anchor and relevant off-screen direction after the semicolon; do not add a relationship field merely to carry continuity. Keep instance IDs, state versions, predecessor links and audit results in the project records.

If the user requests first-frame prompts, derive each static image prompt from that group's first-shot state and camera, with no later action outcome. Deliver them separately from the fixed group fields; LibTV uses its existing per-shot `imageGenerationPrompt`. Actual reference binding and generated-frame checks follow [global-asset-control.md section 3A](global-asset-control.md#3a-站位参考首帧与实际画面承接). A text-only storyboard delivery does not trigger image or video generation.

Always include the final `负面提示词：` line. For `高精度3D`, append the exact required negative block. For `写实短剧质感`, leave it empty unless the user or platform supplied a dedicated negative prompt.

## Bilingual dialogue rendering

When the source supplies paired English and Chinese lines, render the shot record as:

```text
**字幕/角色台词/旁白**：英文主声轨（锁定）— ROLE: Exact English source line
```

Keep the paired Chinese text in the internal source ledger as translation/subtitle reference. Do not repeat it as audible dialogue, do not count it a second time in shot duration, and do not request generated Chinese text. If the source contains only one language, preserve that language as the locked main track.
