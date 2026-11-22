# 工业级定稿写前检查

在有项目验收标准、且已获授权写入正式视频节点的任务中使用。先完成项目标准要求的真实语义审核，再执行本检查；仅讨论规则时不检查具体分镜、不写画布。记录均保存在项目工作区，保持视频提示词原模板。

## 执行顺序

1. 保存锁定原文、完整源稿、所用图片、前后组有效状态的内容版本。逐镜记录镜首、动作中、镜尾；分别定位全局连续性、镜头描述、单镜、合成中对应的原句及原文依据。实际可见人物逐人对照确定原卡，记录必要身份/衣装特征和图中位置。静态图只约束明确作用时段，正常动作变化不能被静态图永久锁住。
2. 独立审核者先读取实际资料形成事实判断，再对照编写者报告；逐镜/逐人覆盖不能用整组“保持不变”代替。必要项失败或待核时返修受影响内容，撤回相关旧结论并复查消费者。
3. 审核通过后保存 `approved.json`：`group`、`target`、完整节点 `prompt`、有序实际输入ID的 `references`、平台当前有效 `params`、`visiblePeople`。同一人物在不同图分别登记 `{person,map,card}`；群演使用确认称谓。此清单须由图审核实，工具不能从清单推断图上没有额外人物。`candidate.json`是即将实际提交的同结构快照，保持全部字段和引用顺序。
4. 保存独立 `review.json`：`author`、`reviewer`、`approvedSHA256`，以及 `inputVersions:{inputs:[...],dependencies:[...]}` 的本次已审完整版本清单；后者必须与包中实际输入和依赖清单一致，刷新包中的SHA不能沿用旧审核。`checks`包含P01–P08、P09Pre、P10Pre，逐项给 `status` 与具体 `evidence`。不适用须另给 `reason`、`confirmedBy`，确认者必须是本次独立审核者，不能由编写者自行删项；可见人物清单非空时P04不可标不适用。`shots`逐镜给 `shot,status,initial,action,final,sourceEvidence`，`fields`含 `global,description,single,composite` 各字段的具体核对位置及事实；`people`逐人给 `person,map,card,status,evidence`。核对数值/文字与图文语义的依据分别说明。
5. 保存 `admission-package.json`：`schemaVersion:1`，`approved`与`review`各为 `{path,sha256}`，`inputs`列全部实际原文/完整源稿/图片/参数依据及审核标准的 `{id,path,sha256}`，`dependencies`列实际消费的前后组状态与素材版本 `{id,path,sha256}`。独立场景没有消费者时显式给空数组并在审核证据说明依据；不能省略真实依赖。路径相对本包目录或使用实际绝对路径，SHA256由实际文件计算。不得编造已阅图、审核者身份或语义事实。
6. 运行以下只读检查，返回非0或 `eligible:false` 时停止本次写入，先处理具体差异。每次相关版本变化重跑；不能重用旧结果放行新稿。

```powershell
& 'E:/Wl rag/project/.venv-bge/Scripts/python.exe' -X utf8 -B 'C:/Users/Administrator/.codex/skills/universal-storyboard-breakdown/scripts/verify_industrial_admission.py' --package './admission-package.json' --candidate './candidate.json' --report './prewrite-result.json'
```

7. 在已有写入授权内，通过当前平台支持的写入工具提交与候选快照一致的全文、输入和参数；临提交前重新读取远端目标与素材版本，存在并行编辑或版本变化时先核差异。写后按项目P09/P10回读真实保存内容，不把本工具的写前结果冒充写回通过。全局连续性和合成段继续维护，节点复制范围见[默认30秒技能](../../chaifen-fenjing-30s/SKILL.md#视频节点提示词复制范围)。

## 能力与证据边界

- 已实现本地只读检查：必检项记录、逐镜及逐人覆盖、独立审核者与编写者记录分离、获审快照绑定、实际文件SHA、候选全文/目标/参数/引用顺序一致、依赖版本变化及显式生成开关拒绝。
- 非空事实和审核者名字不证明事实正确或真实独立；镜数、时码、语速、台词、空间、人物形象和交互仍由对应数值检查及实际独立审核提供证据。本工具不自动理解画面，不判定自然语言状态是否物理成立，也不能确认引用在远端已生效。
- 这是默认流程的写前检查工具，未接管LibTV全部MCP/CLI写入权限，也没有平台权限隔离。`eligible:true`不等于全局自动写入硬拦截已部署，不等于获得写入或生成授权，不等于成片通过。
- 本次优化不更改历史审核结果或旧报告脚本；旧脚本生成的PASS只能作为历史记录，不能导入本工具后被当成新版本的独立判断。

部署或修改检查逻辑时，用已知正确与错误样本验证。机械反例验证版本、字段与覆盖拦截；18-3松手主体、13-1初末态混写、12-2视线断裂和图卡衣装冲突须另做语义复核，机械用例通过不能冒称自动识别这些语义错误。
