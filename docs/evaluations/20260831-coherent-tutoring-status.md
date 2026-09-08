# 连贯教学改造实施与验收状态

Date: 2026-08-31
Scope: approved 2026-08-30 implementation plus the authorized 2026-08-31 audit and delivery follow-up
Status: initial delivery merged; follow-up classroom evidence and whole-conversation closeout recorded; behavioral reliability remains unverified

后续更新：用户又指出历史主线在连续代码问答中丢失，并授权修改及针对性
验证。入口披露、父课备课和续课快照的本地修复见
[披露与续课修复验证](20260831-continuity-repair-validation.md)。该记录单独
区分结构检查、独立内容审阅与尚未运行的正式多轮行为验证；不覆盖或改写
下方早期交付与试讲的历史结果。

## 已落库与实施

- 保存[获准方案](../implementation-plans/20260830-coherent-tutoring-implementation-plan.md)，
  区分路线、定位、讲解；不实现首版数据库或自动导航引擎。
- 重组 tutor 入口与四份阶段参考，统一 NOTES、MISSION、track curriculum
  与历史使用指南。当前明确请求优先；取消固定小课和每轮小测。
- 增加只读导航验证/恢复及每 track 轻量快照；具体分支可以沿父链返回，
  暂存不等于解决，解决不等于掌握。导航功能不迁移旧 session 或能力记录；
  后续获准的六条 session 时间纠正是单独审计的例外，见下文。
- 准备 [React 衔接样课](../../lessons/scientific-ai-platforms/react-from-document-updates.md)
  及无依赖 HTML；初次实施时尚未讲授，后续试讲反馈见下文。
  React runtime 或浏览器绘制验证仍不在这些检查的证明范围内。
- 保留现有六场景模型评估契约，另增连贯教学内容审查，不制造模型运行结果。

本次 skill-creator 的路由要求促使入口缩短、执行规则分阶段加载；calibration
与 coding-protocol 用于限定接口和验收声明，不把静态文件质量当作教学效果。

## 对话来源：partial，不是完整落库

用户授权的来源为 `codex:thread:01a00e46-1bee-7081-a01d-111f587fdfbd`。
初次实施时，只读接口成功回读最近两轮并核对 thread ID：

- `01a052e6-4d6f-7511-98e1-3f7dbd933148`：对轻量范围的确认。
- `01a052e6-86a5-7673-9a46-eb143578203a`：本次整理与实施请求，回读时尚未结束。

接口返回 `hasMore=true`；请求排除了工具输出，并设置单条返回长度限制。
当时更早历史、当前轮最终输出和完整性均未核齐，不能把这两轮或当前决策摘要
称为完整问答。没有导出原始消息、扫描其他会话或建立后台采集器。
`.learning-private/` 已加入 Git ignore，仅提供未来授权导出的私有位置约定，
不是加密或备份。公开文件只保存必要的脱敏摘要和不授予访问权的来源标识。

随后用户授权纠正旧记录，追加核对同一 thread 中六条记录对应的原始轮次；
范围与来源见[时间审计](../audits/20260831-session-timing-audit.md)。这仍是定向、
partial 回读，不是完整历史导出，也不把初次导航快照的两轮覆盖声明改称完整。

## 样课内容自审

由本次实现代理自审，不是独立评审或用户试学结果。

| 审查点 | 当前证据与边界 |
| --- | --- |
| 起点 | 以数量变化后的显示更新为整课问题；不由系统推理能力推断 JSX 熟练度 |
| 关键先备 | 对象属性、参数/调用、String 和连接、DOM 查询/写入逐步说明；不借解构表达新机制 |
| 语言与 library | 从自定义函数过渡到可复用代码，再解释 React 提供的界面描述能力 |
| 例子完整性 | 纯 JS 与 HTML 可独立检查；React API 片段明确需要环境提供库，未伪装成完整程序 |
| 历史 | 2013 项目原文与既有 dossier 限定历史陈述；未增加 first/唯一发明人等优先权断言 |
| 现代来源 | 2026-08-31 核对 createElement、createRoot 和 textContent 官方/MDN 文档，链接保存在课文与资源页 |
| 术语分支 | JSX/component 仅定位用途，延后语法、hooks、imports；试学仍需观察这一处理是否足够 |
| 能力证据 | 没有代答新应用题，没有以 prepared、pass 或分支关闭登记掌握 |

[补充场景](20260830-coherent-tutoring-cases.md)中初次八类反例已映射到当时规则、
样课和导航测试。该映射只能证明有明确设计应对与有限结构证据，不能证明
真实模型每次遵守。自然语言返回点的教学合理性仍需人工审查。

## 可执行检查

下表保留初次实施时的检查结果；后续纠正后的新增检查另列于下节。

| 检查 | 结果 / 证明范围 |
| --- | --- |
| skill-creator quick_validate | 通过；frontmatter 与入口基本格式 |
| test_learning_lab_tutor.py | 3 tests 通过；阶段链接、示例 v2 event 被生产 parser 接受、所需文件存在 |
| test_teaching_navigation.py | 9 tests 通过，含 19 类结构负例；嵌套返回、换课暂存、真实旧 producer 回退、损坏拒绝、重复键拒绝与原 session 字节不变 |
| 样课 Node 检查（含于上述 9 tests） | 纯 JS 得到“样本数：3”“样本数：5”；HTML script 在 document test double 上产生两次预期写入，不等于真实 DOM/像素测试 |
| navigation validate / resolve | 当前快照通过，并返回新桥接课与 partial 来源；不验证原文实际完整性 |
| run-tutor-evaluation.py verify-static | 既有 6 fixtures 通过；未运行模型评估 |
| bash scripts/check-structure.sh | 首轮其他检查均通过，仅最后 generated-drift 检查因既有 site 陈旧退出 1；未宣称整条命令首次成功 |
| render-knowledge-map-site.py + check-knowledge-map-generated.py | 生成器同步后定向复验通过：generated artifacts current；仅变更派生文件，未再重复全部前置测试 |
| git diff --check | 修复后再次通过 |

旧 skill 的逐句字符串断言已替换为路由和生产 parser 检查；教学语义的要求
迁至可审查场景，而非通过保持旧措辞来证明行为。现有状态、历史、术语、
frontend 与 scorecard 必需检查没有关闭或降级。

## 后续获准纠正与交付

用户随后授权 commit、push、merge，并明确允许先审计旧会话及纠正复习计数。
因此，下列变更是对初次实施范围的明确例外，而非继续宣称旧数据未动：

- 六条 8 月 28 日 session 已重命名，修正 `started_at` 和 `duration_minutes`。
  它们记录可核实的原始轮次 wall-time，不代表整课或有效学习时长；旧 ID、
  旧值及来源映射保存在[时间审计](../audits/20260831-session-timing-audit.md)，
  原始文件可从 Git 恢复。其证据、assisted 标记和能力记录未改写。
- 调度改为同一概念在同一 UTC 日期最多计一次 unassisted pass，不删除原始
  观察，不把日期去重视为准确 encounter 身份或长期保持证据。
- 历史 dossier 补入 React 样课的关联路径，重新生成 site；未改历史叙述、
  canonical concepts 或 reviewed learning records。
- 修复后的 15 项 learning-state 测试、4 项 tutor 测试、完整
  `bash scripts/check-structure.sh` 及提交 `1e8adb77ab5e26849bead8d59964d1174fcca335`
  的 PR CI 均通过。完整检查包括现有导航与静态评估检查，不是新模型试验。

上述提交及原有五笔本地提交已通过 PR #9 合并；前轮已核对主工作区与远端
同为 `15e5abd0535e01085870456364336eaac717efee`。本次教学微调尚未提交。
检查结果只支持相应代码、数据和结构声明，不证明教学效果。

## 首次试讲反馈与获准微调（2026-08-31）

来源：同一已获准 thread 的当前可见问答；以下是脱敏复盘，不是逐字转录。
范围仅覆盖 React 试讲、两次复杂度反馈及本次记录/微调授权；没有追加完整
平台导出或核齐所有消息 ID，来源覆盖仍为 partial。

观察：试讲先展开 HTML、DOM、对象、函数、描述与显示流程。学习者认为解释
比问题本身复杂，先用 HTML 包装概括例子，随后主动用 SQL 的 declarative
思路类比 React，并要求复盘。用户已授权记录症结、微调提示词后继续试学。
这支持一次不理想的讲解体验，不支持推断其 SQL/React 熟练度或固定学习风格。

原因判断（待后续验证）：把概览误作执行流程拆解；把工具陌生扩大为全套
基础需要重讲；用创建元素的例子承担更新管理的结论；过早堆叠边界说明。
规则较重视缺失铺垫，却未充分检查多余铺垫。不能由此断言某条提示词是唯一原因。

获准调整：在 tutor 入口、讲解参考和 NOTES 中明确主旨/用途优先、利用
有效类比、只展开当前必要细节，并要求例子体现所宣称的优势。补充两个
内容审查场景；不新增固定字数、提问频次或授课模板，不改总路线和证据规则。

后续观察：从已提出的 declarative 类比接到可复用 component 的输入/输出。
检查是否先说清用途、是否真正展示复用、是否避免无关 DOM/像素链；同时
保留阅读例子所需的 JSX 和参数说明，不从过度解释退回术语跳跃。
在自然节点分别记录体验反馈和独立应用证据；不要求每轮评分或小测。

当前结果：微调已写入，后续讲解体验、独立应用与长期保持均未确认。此处不
创建 subject-mastery session，不改变旧证据、review dates 或能力等级。
静态检查只能验证格式、引用和导航，不证明这套提示词已改善教学。

本次局部验证：skill quick_validate、4 项 tutor 测试、9 项导航测试、1 项
Markdown 渲染测试、导航 validate/resolve、generated-artifact 检查及 diff
空白检查通过。未重跑全仓库 gate，未运行模型对比或 JSX/React runtime；
本次没有改生产脚本、测试、旧 session、能力记录、canonical entries 或历史。

## 剩余验收与操作边界

下一步是观察微调后的继续试学：允许追问，在自然节点分别记录体验和
独立应用证据。首次复杂度反馈说明原有内容自审不足，不能宣称已解决问题。
不要求先开展额外模型大规模对比，也不据一次试学宣称长期保持。

自动完整采集、React runtime/浏览器绘制、模型行为可靠性、长期学习效果和
导航的网页投影均未验证或未实现。网页仍显示旧 session resume；tutor 用
新导航读回详细位置。这一差异已在入口说明。

初次实施没有执行 commit、push、merge；后续交付和旧记录纠正范围以上节为准。
初次全套检查发现既有 site 仍嵌入 8 月 27 日状态，遗漏已存在的 8 月 28 日
sessions；其后两次生成分别同步既有状态和获准纠正后的状态。
这不是把新导航接入网站，也不是本轮新产生的能力判定。

## Whole-conversation closeout（2026-09-07）

本节是后续 `$closeout` 对同一获准 thread 的完整可访问范围核对，不改写上文
“初次实施时只读取两轮”的历史事实。核对使用该 thread 的精确 local session
record，从第一条明确教学请求
`msg_01a00e46-ba3d-74c0-a443-82cd0bd18a33`（2026-08-17）逐行解析到
closeout 请求 `msg_01a07b00-81c7-7f31-89f7-0787d201af7f`（2026-09-07）。
JSONL 全文件解析通过；本节只保存脱敏主题与边界，不复制原始 transcript、
hidden reasoning、tool output 或 private host path。

重要主题与 owning documents 已核对：

- model proposal、deterministic gates、human/scientific acceptance、dataset
  handle、sandbox、authentication/authorization 和 confused deputy 由
  `learning-records/scientific-ai-platforms/0007` 至 `0015` 承担；后续课程
  不把这些能力外推为 frontend 或 backend implementation mastery。
- side effect、idempotency、retry、ACK、partial failure、queue delivery 与
  exactly-once 边界由 `0016`、对应 histories 及 relational-data lesson 承担；
  PostgreSQL/outbox/attempt/lease 的后续内容仍是 guided explanation。
- Web/program/process/service、JavaScript literal、DOM representation、
  TypeScript static/runtime boundary 与 React state/Effects 的发展路线由
  histories、track curriculum、React lesson 和 sample-viewer 承担；多次
  “术语跳跃、过细、过度解释、停止续课、丢失历史主线”反馈由 tutor skill、
  NOTES 与本 evaluation 保存，不据局部改善宣称教学法已验证。
- FastAPI route/handler/setup、Pydantic/raw body、HTTP response hiding、
  transaction ownership、claim ordering、run/attempt/manifest recovery 和
  job-level asynchrony由 HTTP lesson 承担。当前未解决点是 false acceptance：
  `uuid4()` 只产生 response identity，没有 durable handoff，route return 后
  不会自动有 actor 执行 R1。
- 关于将完整问答直接产品化存入数据库的方案，经讨论后被判为首版过度设计；
  已采用 private source locator、append-only learning events、reviewed records
  与 lightweight YAML navigation。自动采集、数据库和 navigation 网页投影仍
  deferred，不能从本次手工 closeout 推断它们已经实现。

本次仅为最后一段有精确 source-turn timing 的异步澄清新增一个 v2
empty-evidence event；它更新 resume，不提升 capability 或 review interval。
完整 conversation coverage 现在写入 navigation source declaration；结构 validator
只能检查该声明格式，完整性结论来自上述 exact session record 核对。

后续应从 false-acceptance transfer 恢复，再决定是否进入一个 runnable vertical
slice。React runtime、独立 SQL/FastAPI 实现、distributed recovery transfer、正式
多轮 tutor behavior evaluation、长期 retention 和 scientific correctness 均未由本
conversation 证明。Closeout 不授权 commit、push、merge 或 archive。

Closeout validation：`build-learning-state.py validate/normalized-data/list-review-cues`、
navigation validate/resolve 与 `git diff --check` 通过。首次完整
`scripts/check-structure.sh` 正确发现新增 session 造成 generated site stale；运行两套
repository renderer 后复跑完整 gate，通过 frontend formatting/typecheck/tests/build、
knowledge-map tests、learning-state/record/history/navigation、tutor static fixtures 和
generated-artifact current 检查，最终输出 `learning-lab structure: ok`。这些只证明
repository state 与相应 contract 一致，不证明教学行为可靠性或学习者 mastery。
