# Character and Costume Workflow

Use this file when extracting characters, costume states, creature/person dependencies, or default character image prompts.

## Dependency Graph

Create a dependency graph before writing final character/costume prompts when the project has families, multiple forms, transformations, age states, injuries, or major costume changes.

Required directed dependencies:

- blood relatives;
- the same person's costume, age, injured, wet, dirty, ceremonial, disguise, or transformed states;
- twins, clones, host/form pairs, armor-bound or creature-bound forms;
- continuous damage or mutation stages.

Default dependency order:

```text
independent base identity -> family/derived identity -> costume states -> injury/age/transformation states -> shot frames
```

If a downstream asset depends on an unconfirmed upstream image or identity, output a waiting card instead of inventing the downstream prompt.

## Production List

Before writing large batches of prompts, output a production list for user confirmation:

| ID | 角色/状态 | 资产类型 | 上游依赖 | 建议批次 | 必要性 | 出图理由 | 当前决定 |
|---|---|---|---|---|---|---|---|
| CHR-01 / CST-01 | ... | 基础角色/服装/亲属衍生/变异/受伤/年龄 | 无/CHR-xx/CST-xx | 第1批 | 必须/建议/文字足够 | ... | 待确认 |

Do not over-split tiny expression changes, ordinary held objects, or dirt that can be handled in a later shot prompt.

## Current Default: Continuous Four-View Character Prompt

Output one self-contained continuous Chinese positive prompt for every necessary `CST-*` costume state. If one character has multiple important costumes, give each costume its own prompt; never compress several costumes into one prompt.

Keep two layers:

- `CHR-*`: identity lock in text, covering age range, body proportion, facial/hair constraints, temperament, class, posture, relationship function, and performance baseline.
- `CST-*`: image prompt for the actual costume design sheet, bound to one `CHR-*`.

Keep the `CHR-*` identity stable internally across all costume prompts, but do not expose identity/costume management as a field list in the default user-facing character output.

## Four-View Character Prompt Contract

For each costume state, use a short heading such as `### CST-xx｜角色名·服装状态`, followed immediately by one continuous prose prompt. The prompt must follow this content order:

1. high-precision image type and chosen visual style;
2. adult age range, identity, visible temperament, height and body proportion;
3. detailed face, eyes, brows, lashes, nose, lips, skin and makeup;
4. hair length, texture, construction, ornaments and earrings;
5. complete costume from inner layer to outer layer, waist, sleeves, lower garment, hem, shoes and carried accessories;
6. palette, embroidery/patterns and real material behavior;
7. horizontal layout: oversized head-and-upper-body close-up on the left; full-body front, strict side and back views on the right;
8. what the front, side and back views must reveal; same-person consistency across all four panels.

Do not write `绑定角色`, `使用场景`, `服装状态`, `剧本事实`, `导演提案`, `角色设定图正向提示词`, `资产类型`, `上游依赖`, or `保守补全` as user-facing character fields. Do not introduce the prompt with a field label. The prose must be directly copyable into an image generator.

Use this as the shape of the default visual prompt:

```text
高精度[视觉风格]角色四视图设定图，[成年年龄与身份、可见气质、身高体型]。[连续描述脸型、五官、瞳孔、眉眼、睫毛、鼻梁、嘴唇、肤色、妆容]。[连续描述发色、长度、发型结构、鬓发、发髻、发饰与耳饰]。

[连续描述本套服装：内衣、外袍、领口、衣襟、袖型、腰封、扣饰、挂坠、下装、裙摆/裤装、鞋履、刺绣纹样、颜色层级和真实材质]。

四视图横向排版，左侧为超大面部半身特写，右侧依次为正面、标准侧面、背面全身。正面完整展示[正面结构]，侧面展示[侧面轮廓、袖摆、腰线、发型和耳饰层次]，背面展示[发型后部、背部结构、后摆和拖尾]。四个视图为同一角色，五官比例稳定，发型、配饰、服装结构、纹样位置、左右非对称细节和颜色完全一致。[身体比例]。纯色或浅灰无缝影棚背景，真实材质质感，统一光线来源，真实阴影高光，无额外人物，无场景，无文字，无水印，无logo。
```

When the user wants a shorter output, compress descriptive detail but preserve the complete identity, the selected costume, the close-up + front + strict side + back layout, same-person consistency, material realism, clean background, and no text/watermark/extra people.

## Multiple Costume States

Every visually important costume, ceremonial state, uniform, disguise, injury/damage state, wet/dirty state, age state, or transformation that changes generation continuity gets a separate prompt. Repeat the full face, hair and body identity in every prompt instead of writing `同上` or referring the image model to another paragraph. Small temporary changes that do not alter the reusable design may remain shot-level variations.

## Acceptance Rules

Check every character prompt for:

- correct `CHR-*` binding and `CST-*` state;
- same body proportion across front/back/details;
- complete face and hair identity plus clothing silhouette and shoes/hem/sleeves;
- correct left/right asymmetric anchors;
- fabric, metal, leather, jade, wood, dirt, wetness, damage, or embroidery behavior;
- oversized close-up plus front, strict side and back full-body views in one horizontal sheet;
- no metadata field list before the prompt body;
- no readable labels unless the user explicitly requests a labeled production board.

