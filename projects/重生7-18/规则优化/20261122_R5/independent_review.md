# R5规则与本地写前检查工具独立复核

日期：2026-11-22。审核者：`/root/review_video_12`。范围仅为本次R5规则更新、默认30秒技能与新增本地检查工具；不修改工具主文件，不写画布，不生成，不声称全部分镜或成片重审。

**最终复测：本次发现的4类问题、5个反例均已修复；独立5项复测通过，工具完整23项测试通过。**结论仅针对下方版本与已列能力，不证明自然语言/图像语义必然正确或平台全局门禁已经生效。

## 初审结果：需要修复后重测

初审工具SHA256：`59ae05ef3ede88e91a1ed92911bde0908b5aa67771272be12bfc99351548086c`。

已独立运行原测试：18项全部通过。另写5项离线反例，5项均复现错误放行，退出码1，记录见 `independent_red.txt`、`test_admission_independent.py`。原有同路径换图测试只改文件、保留旧SHA，没有覆盖“清单更新而审核仍旧”的情况。

### 1. 输入及依赖版本没有绑定到独立审核（P1）

`review.approvedSHA256`只绑定含prompt、refs ID、target、params等内容的approved；输入和依赖的路径、SHA位于包外层。将图像替换后把包中该输入SHA更新为新文件SHA，approved/review不变，仍返回`eligible:true`。前组状态变更并更新dependencies SHA同样通过。这样会把旧图审/旧前情审核沿用到新内容。

最小修复：独立review保存完整`inputVersions={inputs,dependencies}`并与实际包清单严格比较，review本身仍由包SHA锁定。新输入/依赖版本必须形成新的独立审核记录；只比较文件与当前包SHA不够。不得把该修复描述为证明审核者身份真实独立。

### 2. 报告硬链接别名可以覆盖实际输入（P1）

在临时目录为`map.bin`建立`report-alias.json`硬链接。`--report`使用后者时，路径resolve不同，原保护未拦截，执行返回0并把报告写入同一底层文件。测试只在临时副本操作，没有损坏项目资产。

最小修复：在原路径保护之外，对已存在的报告目标与全部受保护输入用`samefile`比较实际文件身份，发现别名立即拒绝。保留根代理已补的“校验提前异常时也能收集受保护文件”处理。输出报告属于唯一显式写入，不应覆盖输入或证据。

### 3. 生成开关只拒绝布尔True，数值1仍通过（P2）

将已审快照与候选都设为`params.run=1`，更新approved哈希及审核快照绑定后，仍返回`eligible:true`。`item is True`没有拒绝其他非False值。

最小修复：已识别生成开关出现时只允许严格JSON布尔`false`；`true`、`1`、字符串、null等均拒绝，不依赖后续平台是否会强制类型或隐式转换。

### 4. 已有可见人物时仍可用P04“不适用”掩盖检查（P2）

approved的visiblePeople含人物，逐人图审记录也存在；将P04改成“不适用”，填“没有可见人物”并由reviewer确认，仍返回`eligible:true`。这是包内可机械比较的冲突，不需要工具理解图片或自然语言。

最小修复：visiblePeople非空时P04不得不适用。一般N/A理由是否真实仍需独立语义审核，工具不能只凭一句理由证明其适用性。

## 规则文档交叉核对

已实际读取R5标准的新段、默认30秒技能对应条款及industrial-admission用法说明。

- R5第66–69行将镜首/动作中/镜尾、全部字段、逐人图审、实际编译prompt放在提示词外；与默认技能第184、206–207行一致，没有要求改用户模板或每镜另加@图。
- R5第75、77行要求内容版本及素材/末态消费者依赖；初审工具的第1项缺陷与该要求不符，应修工具，不降低规则。
- R5第7、33行和默认技能第28行按最新指令区分读取、修改、写入、生成、成片范围；不会因已有视频自动扩大授权。
- R5第78–79行及用法说明明确这是本地写前证据/版本检查，不自动判断图文语义、不确认真实独立身份、未接管全部MCP/CLI权限、不证明平台全局门禁。该边界说明准确，应保留。
- 已独立从R4备份重新提取并比较：P01–P10的10条判据行逐字不变；默认技能输出模板区块逐字不变，默认30.0秒要求保留。不是仅引用编写者的通过标签。

## 修复复测

根代理修复工具主文件；独立审核者未修改主文件。已读取修复代码及更新的用法说明，确认实际加入输入/依赖完整清单审核绑定、报告samefile保护、生成开关严格False、可见人物非空时P04不适用拒绝。

依赖变更用例按新schema补齐“首次基线清单确实经过审核”的前置条件：先将当前inputs/dependencies拷入review.inputVersions并刷新review，再验证基线通过，随后仅变更依赖并保留旧review。修复后实际重跑独立5项全部通过，输出见 `independent_green.txt`。

按根代理授权，将这5项改为现有fixture的类方法并加入C盘 `scripts/test_verify_industrial_admission.py`；使用相邻文件的CHECKER，不复制项目绝对import路径。随后独立运行：

```powershell
& 'E:/Wl rag/project/.venv-bge/Scripts/python.exe' -X utf8 -B -m unittest test_verify_industrial_admission -v
```

工作目录为C盘技能scripts；实际23项全部通过，退出码0，记录见 `admission_full_independent_green.txt`。这些用例检查的是本地确定性边界，不把18-3、13-1、12-2等自然语言问题称为已自动识别。

最终实测版本SHA256：

- `verify_industrial_admission.py`：`076509c9bf5a7b292cff4d550c2cbf3fe7b189039f98af255302d951765bdee8`
- `test_verify_industrial_admission.py`：`6f4e3f9fd42f744f3f061fa3dbb710f3234adb46e80bff3fc7ef6e4b079cc758`
- `references/industrial-admission.md`：`e42fcadaf2c43b1cb3bd1c5a7516f9d6ce16a455747c0e161a992d62fcf54ec7`

没有发现此次修复后仍未闭环的确定性硬缺陷。剩余边界明确保留：visiblePeople清单是否完整、证据事实是否真实、N/A理由是否合适、审核者是否真正独立、远端绑定是否已生效及写入后的实际状态，需要独立语义审核与真实写后回读；本工具的通过不能替代它们。
