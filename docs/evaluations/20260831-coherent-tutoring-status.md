# 连贯教学改造实施与验收状态

Date: 2026-08-31
Scope: approved 2026-08-30 implementation plus the authorized 2026-08-31 audit and delivery follow-up
Status: implementation and corrective checks passed; PR delivery in progress; classroom trial pending

## 已落库与实施

- 保存[获准方案](../implementation-plans/20260830-coherent-tutoring-implementation-plan.md)，
  区分路线、定位、讲解；不实现首版数据库或自动导航引擎。
- 重组 tutor 入口与四份阶段参考，统一 NOTES、MISSION、track curriculum
  与历史使用指南。当前明确请求优先；取消固定小课和每轮小测。
- 增加只读导航验证/恢复及每 track 轻量快照；具体分支可以沿父链返回，
  暂存不等于解决，解决不等于掌握。导航功能不迁移旧 session 或能力记录；
  后续获准的六条 session 时间纠正是单独审计的例外，见下文。
- 准备 [React 衔接样课](../../lessons/scientific-ai-platforms/react-from-document-updates.md)
  及无依赖 HTML；尚未进行课堂讲授、React runtime 或浏览器绘制验证。
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

[补充场景](20260830-coherent-tutoring-cases.md)中的八类反例已映射到当前规则、
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

上述提交及原有五笔本地提交已推送至 PR #9；合并与主工作区同步仍待完成。
检查结果只支持相应代码、数据和结构声明，不证明教学效果。

## 剩余验收与操作边界

下一步是用户真实试学：从完整展示问题进入，允许追问，在自然节点分别
记录体验和独立应用证据。没有试学前，不宣称已解决术语跳跃或已提升学习效果。
不要求先开展额外模型大规模对比，也不据一次试学宣称长期保持。

自动完整采集、React runtime/浏览器绘制、模型行为可靠性、长期学习效果和
导航的网页投影均未验证或未实现。网页仍显示旧 session resume；tutor 用
新导航读回详细位置。这一差异已在入口说明。

初次实施没有执行 commit、push、merge；后续交付和旧记录纠正范围以上节为准。
初次全套检查发现既有 site 仍嵌入 8 月 27 日状态，遗漏已存在的 8 月 28 日
sessions；其后两次生成分别同步既有状态和获准纠正后的状态。
这不是把新导航接入网站，也不是本轮新产生的能力判定。
