# Video Texture Style Options

Apply this reference after resolving the aspect ratio and before drafting the group-level `视觉风格`. Treat the selected video-texture style as a stable deliverable-level parameter. Assemble a combined positive prompt internally for consistency, but do not output a separate `合成提示词` field in the standard final deliverable.

For a continuation of the same script job, reuse the explicitly resolved style in its verified manifest unless the user changes it; follow [long-text-workflow.md](long-text-workflow.md). The current-request selection and default rules below apply to new jobs, not to a same-job message such as `继续`. Preserve the fixed style blocks exactly during resumption.

## 1. Resolve The Style

- Support two built-in labels: `写实短剧质感` and `高精度3D`.
- Normalize explicit wording such as `高精度3d`, `高精3D`, `3D乙女游戏CG`, `次世代高保真3D`, or a direct request for the prompt below to `高精度3D`.
- Use the style explicitly named in the current request. If no style is named, use `写实短剧质感` without delaying the conversion.
- If the user explicitly asks to choose or compare styles but has not selected one, ask: `请选择视频质感风格：写实短剧质感，还是高精度3D？` Stop and wait.
- Keep one style across all groups. When the user requests multiple styles, produce complete labeled variants rather than mixing styles inside one group.
- A user-supplied custom style overrides the built-in default. Preserve any exact prompt block the user explicitly locks.

## 2. Output Placement

- Record the resolved label in the global continuity block and every group's `视频质感风格` field.
- Keep `视觉风格` concise: state the label, normalized ratio/orientation, native composition, and camera grammar.
- Assemble the internal positive prompt from the normalized ratio/orientation, group-specific subject, action, environment, composition, lighting, material behavior, motion, and selected style treatment. Use it to verify consistency with the visible group fields.
- For `高精度3D`, append the exact positive block below once to every group's visible `视觉风格` field. Do not translate, paraphrase, shorten, reorder, or deduplicate it.
- End every group with `负面提示词：`. For `高精度3D`, place the exact negative block below there. Never merge it into positive content.
- The entire supplied positive block, including all its original negative phrases (`not live action, not 2D`, `no crushed blacks`, `no flickering`, etc.), is a locked exception to the general positive-prompt cleanliness rule. Do not add any other negative wording to the scene-specific positive text.

## 3. 写实短剧质感

Use this as the default when the request does not name a style:

```text
写实短剧质感，目标画幅原生构图，自然表演，中景与关系镜头为主，近景和特写只用于人物出场、身份揭示或关键情绪节点，景别递进清楚，环境声真实
```

Replace `目标画幅` with the resolved ratio and orientation. Keep the required final `负面提示词：` line empty unless the user or target platform explicitly requires content.

## 4. 高精度3D Positive Prompt Block

Preserve this block verbatim, including weights, capitalization, punctuation, paragraph order, and repeated quality concepts:

```text
(masterpiece, best quality:1.2), premium cinematic 3D otome game CG, Love and Deepspace-inspired visual quality, next-generation high-fidelity game cinematic, high-end stylized realism, mature realistic 3D modeling, refined natural proportions, realistic anatomy, polished narrative cutscene quality, not live action, not 2D,

(hyper-detailed translucent skin:1.25), physically based skin shading, subsurface scattering, delicate soft micro-pores, subtle facial peach fuzz, natural skin specular, soft translucent complexion, realistic lip texture and moisture, finely shaded eyelids, natural wet eye line, layered iris detail, clear corneal reflections, restrained facial details, smooth but non-plastic skin,

(ultra-detailed strand-based hair:1.25), distinct individual hair strands, naturally grouped hair clumps, soft fluffy hair texture, anisotropic hair highlights, realistic hair self-shadowing, detailed hairline, translucent flyaway strands, physically plausible hair movement,

high-quality PBR clothing and environment materials, clear differences in fabric, leather, metal, glass, stone and wood roughness, realistic folds, fine textile fibers, accurate reflections, subtle ambient occlusion, physically grounded contact shadows,

cinematic lighting, soft directional key light, restrained fill light, delicate rim light around the face and hair, subtle volumetric light, realistic global illumination, ray-traced reflections and shadows, balanced warm and cool lighting, controlled highlights, preserved structural detail in dark areas, no crushed blacks, elegant atmospheric depth,

natural facial micro-expressions, subtle breathing, realistic blinking, smooth eye movement, natural head and body motion, physically plausible hair and cloth secondary motion, graceful movement with realistic weight and inertia, cinematic motion blur, smooth camera movement, natural lens perspective, controlled depth of field,

(temporal consistency:1.3), strong frame-to-frame coherence, stable character identity, consistent facial geometry, stable facial features and body proportions, stable hairstyle topology, consistent clothing structure and patterns, stable environment geometry, consistent material textures, consistent lighting direction and exposure, smooth motion continuity, optical-flow consistency, no flickering, no texture swimming, no identity drift,

Unreal Engine 5 quality, Octane render quality, ray tracing, physically based rendering, high dynamic range, 4K to 8K per-frame detail, cinematic color grading, clean antialiasing, premium otome game video quality
```

## 5. 高精度3D Negative Prompt Block

Preserve this block verbatim and output it only in `负面提示词`:

```text
(worst quality, low quality:1.4), 2D, flat anime, cartoon, illustration, sketch, comic, low-poly, clay render, white model, unfinished render, live-action footage, photographic real person, plastic skin, waxy skin, porcelain skin, excessive skin pores, oily skin, over-sharpened face, blurred hair, solid hair mass, painted hair, low-resolution textures,

face flicker, identity drift, face morphing, unstable facial features, changing face shape, asymmetrical eyes, cross-eyed, distorted pupils, deformed face, bad anatomy, incorrect body proportions, extra limbs, extra fingers, fused fingers, broken joints,

hair flicker, unstable hairstyle, disappearing hair strands, texture swimming, texture crawling, changing clothing patterns, unstable fabric folds, lighting flicker, exposure pumping, color shifting, inconsistent shadows, background deformation, warped architecture, floating objects,

frame jitter, camera shake, motion stutter, ghosting, duplicated frames, interpolation artifacts, excessive motion blur, excessive depth of field, excessive bokeh, fisheye distortion, overexposed highlights, crushed blacks, oversaturated colors, excessive bloom, excessive lens flare, noise, watermark, text, logo
```

## 6. Style Audit

Fail and rewrite when any applicable condition is false:

1. The global continuity block and every group record one matching resolved style label.
2. Multi-style requests are separated into complete labeled variants.
3. `高精度3D` uses the positive block exactly once per group's visible `视觉风格` field.
4. The high-precision 3D positive block is verbatim and all its locked phrases have been preserved without deletion or additions.
5. The high-precision 3D negative block is verbatim, appears only in `负面提示词`, and is not mixed into positive visible content.
6. Every group includes the terminal `负面提示词：` line; it remains empty for `写实短剧质感` unless dedicated negative content is required.
7. Scene-specific content remains concrete and consistent with the script; the style block does not invent new plot events, props, weather, or locations.
8. The selected style, character identity, material definitions, lighting direction, exposure, and environment geometry remain consistent across adjacent groups unless the source provides a visible reason to change.
