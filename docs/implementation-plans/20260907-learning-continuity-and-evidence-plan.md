# 续课、能力证据与教学观察优化

Date: 2026-09-07
Status: implemented and locally verified; prospective teaching effects unverified

## 问题与范围

用户已确认三阶段方案并要求落下文档后执行。当前仓库有 37 份 legacy records、
0 份 structured reviews；部分路线入口仍用历史判断描述当前能力。教师使用
navigation，网站使用 session resume；HTTP 课文同时承担教材和动态问答记录。
已有连贯教学审查没有进入实际行为观察，严格模型评估仍未运行。

保留当前 mission、课程路线、术语与历史证据 gate、session schema 和严格
scorecard 契约。保留开始时的全部未提交改动，不提交、推送或发布。
不建数据库、自动采集器或新的学习调度器，不批量推断旧记录中的掌握程度。

## 1. 统一恢复与口径

- 扩展现有 navigation resolver，提供规范化的 resume、主课、当前分支与未决项。
  现有 resolve 字段兼容保留；网站生成与教师调用同一解析实现。
- 按 track 投影；缺失导航时仅使用同 track 的既有 session resume；损坏导航
  必须失败，不能退回看似正常的旧进度。网站不展示 private capture locator。
- 当前 HTTP 单元保留稳定问题框架和来源，将既有正文问答作为有明确边界的
  历史课堂材料保留；当前位置只由 navigation 决定。
- 修正路线入口对能力与状态引擎的权威表述，并保存本次讨论的续课返回点，
  不将设计讨论登记成 subject mastery。

验收：CLI 与网站的规范化位置一致；主课、嵌套分支、暂存、同 track 回退、
跨 track 隔离、损坏拒绝有测试；当前教材和入口不再承担第二份动态进度。

## 2. 核对当前课程证据

只审查事务提交、异步任务、执行者分工三个近期前置主题。优先使用现有
获准记录和当前可见对话；来源或提示条件不足时写明待检验，不补造 session、
时间、原文、独立表现或 canonical term。保留全部旧记录。

验收：每个主题给出证据范围、提示情况、可作出的结论和自然教学节点的
后续观察任务。没有证据支持时允许零能力提升。

## 3. 建立有限结论的连续教学观察

将已有合成情境整理成多轮协议，覆盖局部答疑后续课、简化表达、明确改向、
中断恢复。保存已实际发生的观察与材料版本、可取得的运行信息和限制；
未运行的合成情境保持 pending，禁止补造回答或通过率。

轻量观察只支持具体表现判断，不产生 strict aggregate，不替代原来的
不可变模型标识、digest、隔离和重复运行要求。私有原始问答不交给额外评估者。
当前执行不启用额外代理或外部模型；可核对的真实教学轨迹先作为有限观察。

验收：多轮输入、逐轮观察点、实际证据/未运行状态、结果限制可核查；静态
验证不冒充试教。首次课堂应用作为后续课程的一部分，不要求用户逐轮评分。

## 检查与停止条件

每批先运行最小相关检查。因涉及生成投影和仓库结构，最终运行
`bash scripts/check-structure.sh`，需要时先运行两套仓库 renderer。
不得削弱既有诊断；未完成的浏览器或模型运行边界逐项披露。

停止扩建设计的条件：续课出口一致、能力口径一致、核心多轮情境有协议与
真实观察入口，并如实记录当前行为证据的范围。完成后恢复课程；未来试教和
独立能力检验随自然学习节点开展，不用平台建设阻塞学习。

## 实施结果

### 第一批：已实现

- `check-teaching-navigation.py resolve` 兼容保留原字段，增加统一 resume 与暂存
  分支；`normalized-data` 调用同一 resolver 按 track 生成网站位置。现有 session
  producer 和四个旧网站数据投影保持不变。
- 网站显示主课、当前问题、返回点和暂存问题；旧注入 fixture 兼容保留。
  已有新投影即使为空，也不能回退旧进度。public payload 不含 capture provenance。
- 两个 track README 明确历史观察与 reviewed capability 的区别。教师技能参考
  改为读取 resolver，不再让课文或 README 维护第二份当前检查点。
- HTTP 单元成为稳定入口；原 1,134 行课文完整移入
  [课堂快照](../learning-observations/20260907-http-classroom-notes.md)。快照中原文的
  SHA-256 与整理前相同：`d7a8111b81e3c2021c900bf98eb6adedcaa0912b5f14b8005eb2a9af81920170`。
  它是已有课堂材料，不被称作原始逐字对话。
- 导航保存本次教学与设计暂停的返回点；因为本任务原文导出未核齐，将来源
  coverage 明确为 partial，并保留此前已核对的历史范围，未伪称全量采集。

### 第二批：已审阅，零能力提升

[前置证据审阅](../learning-observations/20260907-current-prerequisite-review.md)覆盖
事务提交、异步任务和执行者分工。已有提示/纠正、空 evidence 与未检验边界
均保留；当前证据不足以生成独立能力结论。37 legacy、0 structured 的数量
保持不变；没有更改 session 内容或虚构时间，没有批量迁移旧记录。

### 第三批：协议和真实回顾已落地，前瞻试教待发生

[有限观察协议](../evaluations/20260907-continuity-observation-protocol.md)包含四个
合成多轮情境，说明逐轮执行、跨上下文恢复、材料与运行来源、回归及结论范围。
已保存当前真实问答的 retrospective observation；未发生的行为显式标为
not-observed。没有调用模型执行合成情境，也不将软件测试当作行为试验。

新增轻量校验只检查观察结构与案例对应，拒绝 strict aggregate 和未说明的
缺项；严格六场景、fixture hash、scorecard 契约没有放宽。
下一次恢复教学再观察新实现下的返回表现；四个合成案例、新旧比较和长期
学习效果仍待实际运行，不是本轮实现完成的前提或已兑现的效果。

### 验证

- 导航/示例 11 tests 通过：主课、嵌套、暂存、回退隔离、损坏拒绝、来源过滤。
- 浏览器 renderer 8 tests 通过，新增新导航优先、返回/暂存展示、空投影不复活旧进度。
- TypeScript check、观察校验及观察负例检查通过。
- 原课文字节与新入口链接已核对；生成器已重建 site，尚未发布。
- 完整 `bash scripts/check-structure.sh` 通过，最终输出 `learning-lab structure: ok`。
  包括前端浏览器、图谱、历史、状态、记录、导航、观察、严格静态评估与生成物检查。
  随后的观察文件类型补充（区分真实回顾和未来 synthetic-run）再次通过定向
  validator 与正负例测试；没有更改前端或已有评估契约。
- 严格六场景 fixture、scorecard schema、原 evaluation runner、learning-state
  producer 与 reviewed-record producer 与本轮开始时相同；静态 fixture hash
  仍为 `a8fbf930bb7f2307d8ba048d31a7a9dfc80ca042be7e13ef942bed2435216b89`。
- `git diff --check` 通过；没有需要跳过的本轮必需软件检查。外部发布、实际
  合成模型试教、优化后跨任务续课行为和长期效果未验证。

本轮未提交、推送、发布。开始时已有的其他改动保留；`.agents` 参考更新使用
了获授权的定向文件写入，未更改全局技能或用户 memory。
