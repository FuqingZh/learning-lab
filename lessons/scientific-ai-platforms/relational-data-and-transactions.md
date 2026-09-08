# 从记录身份到并发提交

## 当前单元主线

- 主问题：系统如何把一次合法的业务请求变成正确的数据库变化，并处理
  多个请求对同一份数据的竞争。
- 路线位置：接续[浏览器与服务端状态](browser-server-state.md)，沿既定
  PostgreSQL 阶段学习关系模型、keys、constraints、transaction，再进入
  concurrency 和 durability；没有改变阶段顺序，也不以产品仓库 API 为课程。
- 能力目标：解释记录身份、引用、业务成功条件与共同提交的区别；在明确的
  PostgreSQL 隔离级别下追踪两个请求的执行，而非只复述关键字。
- 起点：前几轮已讲解关系模型、SQL 基本读法、keys、删除策略、atomicity、
  BEGIN / COMMIT / ROLLBACK 和更新行数。讲解不等于独立掌握，观察见文末。
- 当前推进：数据库单元已推进到 worker recovery 边界。学习者已判断 generation
  不匹配的 UPDATE 0 应拒绝 stale attempt，并说明其不满足业务定义。下一单元
  转向 HTTP/FastAPI boundary：谁把 request 变成这些受控状态转换。
- 延后：完整 isolation-level 分类、MVCC 内部实现、deadlock、跨行并发规则、
  外部任务调度、请求去重恢复和数据库驱动 API。

## 历史与来源

Codd 的 [1970 论文](https://cs.uwaterloo.ca/~david/cs848s14/codd-relational.pdf)
§1.1–1.3 讨论应用与内部数据表示的独立性，以及通过数据值识别和引用记录。
这支持从存储位置转向逻辑数据的讲解，不证明 SQL 同时产生或独创优先权。

Gray 的 [1981 论文](https://www.cs.utexas.edu/~witchel/380L/papers/gray81vldb-transaction.pdf)
讨论 transaction 的状态变换和 atomicity；正文印刷页 14–15（PDF 页索引
15–16）讨论并发操作如何依赖未提交结果，以及用锁协调访问的方案。这里
不把文中的神话比喻当历史事实，不沿用其当年的性能估计，也不把它描述的
实现直接等同于 PostgreSQL。1970 与 1981 是两个问题视角，不声称单线因果。

相关[恢复历史档案](../../histories/volatile-memory-and-durable-state-history.md)
已读取，后续展开 durability 时再依其来源论证，不把 atomicity 等同于备份。

现代行为依据（2026-08-31 核对 PostgreSQL 18 官方文档）：

- [Concepts](https://www.postgresql.org/docs/18/tutorial-concepts.html)：table、row、column。
- [Constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)：primary key、foreign key 和删除策略。
- [Transactions](https://www.postgresql.org/docs/18/tutorial-transactions.html)：共同提交、ROLLBACK。
- [UPDATE](https://www.postgresql.org/docs/18/sql-update.html)：筛选、修改和更新零行不等于执行错误。
- [Transaction Isolation](https://www.postgresql.org/docs/18/transaction-iso.html#XACT-READ-COMMITTED)：
  Read Committed 下竞争更新会等待；对方提交后重新检查 WHERE，对方回滚后
  可以继续更新原目标记录。

以上是文档依据，不是本机双连接实验结果；本轮未连接数据库或执行这些 SQL。

## 已讲内容的连续框架

1. 保存草稿与接受分析请求是不同业务操作，但两者都可以持久化。
2. relational model 是模型，SQL 是语言，PostgreSQL 是管理数据的软件。
3. primary key 区分记录；不同 ID 不排除重复处理同一业务请求。
4. foreign key 维护引用，不替代 authorization。删除策略表达生命周期，
   不是由“存在引用”自动推导“共同删除”。删除引用者不会因该外键反向
   删除被引用的共享数据。
5. side effect 是外部状态变化，不是错误的同义词。
6. transaction 的 atomicity 组织共同提交；业务要求仍须写成条件并检查结果。
7. UPDATE 0 是合法的 SQL 结果；若业务要求恰好更新一份可提交草稿，后端
   必须在 transaction 内据此放弃本次提交，不能只检查有没有异常。

## 同一份草稿的两个请求

假设 D1 的 draft_id 是 primary key，最初 status 为 editing；采用 PostgreSQL
Read Committed，普通表，无修改行为的特殊 triggers，也没有其他流程把它
重置为 editing。请求 A、B 都必须遵循同一提交路径，身份权限前置检查另行完成。

先用反例说明：两边即使各有 BEGIN / COMMIT，若都普通读取到 editing，随后
仅按 draft_id 更新并分别创建 job，仍可能各自成功。普通读取不是预约权。

下面的条件更新与后端判断共同构成这个单行状态转换的保护：

```sql
UPDATE drafts
SET status = 'submitted'
WHERE draft_id = 'D1' AND status = 'editing';
```

每个请求在自己的同一个 transaction 内执行 UPDATE，检查实际更新行数：
不是 1 就 ROLLBACK；是 1 才创建 job；任一步失败则回滚，成功才 COMMIT。
不要拆成多次自动提交，也不要在检查前就启动外部计算。

A 先更新但尚未结束时，B 对同一行的竞争更新等待。A 提交后，B 重新检查
已更新行上的 WHERE；status 已是 submitted，因此 B 更新零行，不创建第二个
job。这里不宣称全部数据库请求串行，也不宣称所有 SELECT 都等待。

检验题（已收到回答，需修正，不记作完全通过）：如果 A 更新草稿后创建 job 失败，最终
ROLLBACK，正在等待的 B 会不会也必然失败？请解释草稿状态与 B 的条件判断。

学习者判断 B 不一定失败，但将后续描述为 D1 未写入数据库、创建新任务重新
计算。反馈澄清：D1 在 A 开始前已经存在且为 editing；回滚撤销 A 的状态
修改，B 可以对原目标继续条件更新。只有更新一行并且任务新增成功后，B 才
提交自己的 transaction。任务记录的创建不等于外部计算已经启动。备课说明
和本次修正不算学习者独立答出，也不保证 B 不会因其他原因失败。

该方案只说明上述单行、不重置状态且所有写入遵循同一路径的竞争。不自动
解决成功响应丢失后返回已有 job、跨行约束、隔离级别变更或外部执行去重。

## COMMIT 之后：durability 与 WAL

### 要解决的问题

atomicity 回答一组数据库修改是否共同生效，isolation 回答并发 transaction
怎样相互影响。durability 回答另一件事：数据库已经确认 transaction 提交，
随后数据库进程或机器发生所声明的 crash，提交结果能否恢复。

1979 年 Lampson 与 Sturgis 的未发表技术报告从 crash 可能清空 processor
state、留下不一致持久数据的问题出发，在明确的磁盘错误和灾难假设下构造
stable-storage abstraction。它不声称物理介质永不失效，也不建立全球优先权。
1983 年 Haerder 与 Reuter 的论文把 committed transaction 的结果在后续
malfunction 后仍可恢复表述为 durability。两份材料属于不同论述层次，
这里不根据年份断言直接因果或唯一谱系。来源边界见
[恢复历史档案](../../histories/volatile-memory-and-durable-state-history.md)。

### 为什么不是每次都立刻重写所有 table 文件

PostgreSQL 使用 Write-Ahead Logging（WAL）。核心顺序是：描述数据变化的
WAL record 必须先 flush 到持久存储，相关 data page 才可以随后写入 table
和 index 文件。因此，提交时不需要强制把这次修改涉及的每个 data page
全部写完；crash 后可以依据 WAL 重做尚未反映到 data file 的已记录变化。

```text
修改 draft/job 的内存页
        ↓
先记录并持久化足够的 WAL
        ↓
确认 COMMIT
        ↓
data pages 可以稍后落盘
        ↓
crash 后用 WAL 恢复 committed state
```

这是顺序关系的教学图，不是 PostgreSQL 全部内部流程。依据：
[PostgreSQL WAL](https://www.postgresql.org/docs/18/wal-intro.html)。

### durability 是有边界的承诺

默认 `synchronous_commit=on` 时，本地提交会等待 WAL flush；如果显式设为
`off`，服务端可以先报告成功，近期 transaction 在 crash 时仍可能丢失。
`fsync=off` 还可能带来无法恢复的一致性损坏风险。因此，不能脱离配置、
存储栈和 failure model，只凭看到 `COMMIT` 字样推断所有故障下绝不丢失。
依据：[PostgreSQL WAL settings](https://www.postgresql.org/docs/18/runtime-config-wal.html)。

本地 durable commit 也不自动等于备份、跨节点复制、跨区域容灾，或误删除后
可恢复。durability 更不证明数据科学正确、调用者有权写入、job 已被 worker
接管。它只覆盖具体数据库配置对具体 failure boundary 作出的保存与恢复承诺。

### 与分析任务的边界

如果 J1 已 durable 地记录为 queued，但后端只把“请执行 J1”放进 process-local
memory，随后进程 crash，那么数据库中的 J1 可以恢复，内存里的执行通知却
可能丢失。此时数据库 durability 没有失败；缺少的是数据库状态与外部执行
之间的可靠 handoff。这个问题留给后续 service/worker 单元，不在本节假装由
WAL 自动解决。

检验题（待回答）：数据库 transaction 已成功提交 J1，随后应用进程 crash；
重启后能查到 J1，但 worker 从未收到任务。这里能否说 PostgreSQL 的
durability 失败了？当前证据分别证明和不能证明什么？

学习者回答不能，并正确指出能查到 J1 支持数据库保住已提交记录，不能证明
任务运行成功；worker 未收到也不证明 J1 未持久化。需限定：仅观察某一个
worker 没收到，不能排除其他 worker、轮询恢复或另一执行路径已经处理；只有
题设保证它是唯一执行入口时，才支持“任务未执行”。该收紧尚未独立复核。

## 从 durable record 到 reliable handoff

### dual write 的 failure window

应用需要同时改变两个不同系统：在 PostgreSQL 保存 J1，再向消息系统发送
“执行 J1”。数据库 transaction 不能自动覆盖另一个消息系统。

```text
方案 A：COMMIT J1 → crash → 尚未发送消息
结果：job durable，但 worker 不知道

方案 B：先发送消息 → crash / ROLLBACK 数据库
结果：worker 可能执行一个没有 committed job 的消息
```

仅仅交换顺序不能消除两个操作之间的 failure window。Gray 1981 已区分可由
transaction undo/redo 的 protected actions 与不能简单撤销的外部 real actions，
并讨论将后者延迟到 commit；它不提供今天 outbox 产品的来源或唯一谱系。

### transactional outbox

现代常用做法是 **transactional outbox**：不要在提交路径中直接把消息当成
第二个系统的写入，而是在同一个 PostgreSQL transaction 中同时保存业务事实
和一条“以后必须发布”的 outbox record。

```text
BEGIN
  INSERT job J1
  INSERT outbox event E1: RunJob(J1)
COMMIT

relay 读取 committed E1 → 发布给消息系统 → worker 接收
```

J1 和 E1 要么共同提交，要么共同回滚。应用进程即使在 COMMIT 后 crash，E1
仍然存在；恢复后的 relay 可以继续发布。AWS Prescriptive Guidance 把这种
database write + notification 称为 dual write problem，并说明 outbox table
与业务数据在同一 transaction 更新。Debezium 文档则给出捕获 outbox table
变化的实现形式以及可用于去重的 event ID。这些是两种现代文档，不证明模式
只有一种实现或适用于所有跨系统流程。

来源：[AWS transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)、
[Debezium Outbox Event Router](https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html)。

### 为什么仍然需要 idempotency

relay 也有自己的 failure window：它可能已经发布 E1，却在记录“已发布”之前
crash。恢复后会再次发布同一个 E1。因此 outbox 通常把“可能漏发”转换成
“可以重试但可能重复”；consumer 仍需用稳定的 `event_id` 去重。同一逻辑
事件的 retry 保留 E1，不能每次生成新 event ID，否则 consumer 无法识别重复。

这不自动证明 exactly-once processing。它建立的是可恢复的发布事实，并把
重复处理变成一个显式、可检查的 consumer obligation。

检验题（待回答）：relay 已把 E1 发布给 worker，但在标记 E1 已发布之前
crash；恢复后再次发布 E1。worker 应如何处理第二次 E1？为什么不能在 relay
retry 时生成 E2？

学习者回答：检查 E1 是否已处理；已处理则不重复，否则执行；retry 生成 E2
会使 worker 无法识别同一 job 的重复。核心方向正确。补充：稳定的是同一个
logical event 的 event_id，不只是 job_id。一个 job 可以合法产生 RunRequested、
Cancelled、Completed 等不同事件，不能仅因 job 相同就把它们全部去重。

### consumer 的 check-then-act window

若 worker 只是分两步执行，仍有竞争：两个 worker 可能同时查到 E1 未处理，
随后都执行。或者一个 worker 完成外部 effect 后、记录 processed marker 前
crash，retry 又会重复 effect。

当 effect 本身只是同一个 PostgreSQL 中的修改时，可以把下面两项放进同一个
transaction：以 E1 的 unique/primary-key processed record 争取处理权，以及
真正的数据修改。只有成功插入 E1 的 consumer 执行 effect；重复 E1 因唯一性
得不到处理权。effect 失败则 marker 一起回滚。具体 SQL API 延后，当前只建立
共同提交关系。

若 effect 是启动外部计算、调用第三方 API 或控制真实设备，它不能因为本地
数据库 ROLLBACK 而自动撤销：

```text
先提交 processed(E1) → crash → 外部 effect 还没发生
先做外部 effect → crash → processed(E1) 还没提交，retry 可能重复
```

这说明 idempotency record 不是魔法 exactly-once。需要让外部操作本身接受
稳定 idempotency key，或采用可恢复 claim/lease、状态 reconciliation、结果
readback 等与具体执行系统匹配的协议。下一阶段再选择机制，不在本节把它们
混成一个万能方案。

检验题（待回答）：worker 先把 E1 标记为 processed 并 COMMIT，随后在启动
外部计算前 crash。重启后因 E1 已 processed 而跳过。这个设计实现了
exactly-once execution 吗？实际留下了什么状态？

学习者回答：没有；留下有执行标记但漏执行的状态。回答准确识别了 durable
marker 与真实外部执行之间的分歧。进一步收紧：这里的 `processed` 命名掩盖了
它实际只能证明 E1 的 marker 已写入，不能证明计算开始或成功。retry suppression
因此造成确定的 omission，而不是 exactly-once execution。该题是当前场景中的
正确判断，不外推为已掌握全部 worker recovery 机制。

### 不要用一个 processed bit 代表整个执行过程

外部计算不是瞬间发生的一次数据库修改，而是有生命周期的工作。至少要区分：

```text
queued ──claim──> running ──结果落库──> succeeded
                    └──────失败记录──> failed
```

`queued` 只表示任务可以被领取；`running` 表示某次执行尝试已经取得处理资格；
`succeeded` 才表示系统获得并持久化了所要求的完成证据。它们是不同事实，不能
都压缩成 `processed=true`。同一个 logical job J1 可以经历多个 execution
attempt，例如 A1 crash 后由 A2 重试；因此 `job_id` 保持 J1，`attempt_id`
则区分 A1、A2。

claim 应由一次有条件的数据库更新完成：只有仍为 queued 的 J1，或已经满足
恢复条件的旧 running attempt，才能被新 worker 改成 running 并写入自己的
attempt identity。这样两个 worker 竞争时，不会仅凭各自先查到 queued 就都
认为自己取得了执行权。

但 running 也不能永久占住任务。常见做法是记录一个会到期的 lease，并由仍在
运行的 worker 定期续期；worker crash 后不再续期，lease 到期，恢复流程才可
重新 claim。这里 lease 只解决“旧 owner 消失后如何再领取”，不自动证明外部
effect 没发生，也不自动实现 exactly-once。外部 executor 若支持稳定
idempotency key 或权威 status readback，系统还应据此去重或 reconciliation。

检验题（待回答）：W1 以 attempt A1 claim 了 J1，随后失去联系；lease 到期后
W2 以 A2 重新 claim。此时 W1 又恢复运行，并试图把 J1 写成 succeeded。系统
能否只检查 `job_id = J1` 就接受 W1 的结果？为什么？

学习者回答不能，因为两个 execution attempt 正在竞争，需要确认其他 attempt
状态。核心判断正确：job identity 不足以证明 A1 仍有提交资格。进一步修正是，
先查询其他 attempt 再单独写入仍有 check-then-act race；查询之后，claim 仍可能
变化。因此，资格检查必须成为最终写入本身的条件，而不只是写入前的一次观察。

### 让过期 attempt 在写入瞬间失去资格

每次 claim 除了生成新的 `attempt_id`，还可以递增一个 `claim_generation`：

```text
W1 claim J1: attempt=A1, generation=7
lease 到期
W2 claim J1: attempt=A2, generation=8
```

W1 完成后不能只写“把 J1 改成 succeeded”，而必须表达“仅当 J1 当前仍由
A1/generation 7 运行时，才接受这个结果”：

```sql
UPDATE jobs
SET status = 'succeeded'
WHERE job_id = 'J1'
  AND status = 'running'
  AND attempt_id = 'A1'
  AND claim_generation = 7;
```

W2 已经重新 claim 后，数据库中的 generation 是 8，W1 的 UPDATE 因此影响
零行。后端必须把零行解释为“这是 stale attempt，结果不再被当前 job 接受”，
不能因为 SQL 没报错就当成成功。这里再次用到了前面学过的同一原则：技术上
合法的 UPDATE 0，不一定满足业务要求。

这个条件写入保护的是 PostgreSQL 中哪一份结果成为 J1 的 authoritative state。
它不撤销 W1 已经对外部 executor 造成的 effect。如果 W1、W2 都可能启动昂贵
计算，外部 executor 还需要识别稳定 identity、拒绝过期 generation，或者允许
系统通过 authoritative status/readback 做 reconciliation。否则数据库可以拒绝
W1 的迟到结果，但重复计算已经真实发生。

检验题（待回答）：W2 已持有 generation 8；W1 携带 generation 7 完成计算并
执行上面的 UPDATE。SQL 正常执行但更新零行。后端应该把它解释为
“J1 已成功”，还是“过期 attempt 的结果被拒绝”？为什么 SQL 没有 exception
仍不能算业务成功？

学习者回答应解释为过期 attempt 被拒绝，因为不满足业务定义记录。判断正确：
该 SQL 只说明数据库能够合法完成一次条件更新的尝试；更新零行说明当前记录
不再满足 A1/generation 7 的提交资格。这里不把一次同构问题的正确回答外推为
完整 worker recovery 能力；外部 effect 去重和真实并发实验仍未检验。

本单元至此形成一条完整边界：PostgreSQL 可以保存 authoritative job state、
原子地维护数据库内 invariant，并拒绝 stale attempt；它不负责决定网络请求
来自谁、调用者是否有权提交，也不能自动撤销外部计算。这些责任由下一单元的
HTTP/service boundary 接续，见[从 HTTP request 到受控业务操作](http-boundary-and-fastapi.md)。

## 2026-08-31 问答回顾（非能力评级）

来源：当前已授权对话中可见的问答，位置见
[navigation](../../learning-state/navigation/scientific-ai-platforms.yaml)。
以下是摘要，不是逐字 transcript；没有导出或核对完整原始对话。

| 已观察的回答 | 有限结论与后续修正 |
| --- | --- |
| 区分需保存的草稿与正式提交分析 | 抓住业务区别；教师补充草稿可长期入库、提交可先排队，保存本身也是操作。 |
| 不同 job_id 不违反 primary key，并称它们是独立任务 | 前半判断正确；教师补充不同记录仍可能来自重复业务请求，尚无修正后独立检验。 |
| 删除被引用用户会留下找不到用户的任务 | 识别了引用断裂的风险；教师补充已声明的默认 foreign key 会阻止该删除，查询也未必直接报错。 |
| 不删除共享数据集，理由是有 side effect | 选择符合题设，但理由过宽；教师补充共享生命周期才是关键，尚无修正后独立检验。 |
| 对 atomicity 与 UPDATE 0 讲解表示继续 | 仅说明愿意推进；没有 transaction 或 isolation 的独立应用答案。 |
| 随后判断 A 回滚不必导致 B 失败，但称 D1 未写入并重新计算 | 判断方向正确；需要区分撤销修改与删除已有记录、任务记录与外部计算。已给修正，修正后应用尚未检验。 |
| 判断 J1 可查询说明数据库保住记录，不证明执行成功；worker 未收到不证明未持久化 | durability 与 execution 边界判断基本正确；“没收到证明未执行”仅在唯一执行路径的题设下成立，收紧后尚未复核。 |
| 对重复 E1 先查 processed，已处理则跳过；不能 retry 为 E2，否则无法识别重复 | 正确连接稳定 event identity 与 consumer idempotency；需要补充 event_id 不等于 job_id，且 check 与 effect 仍需处理并发和 crash window。 |
| 判断 marker 先提交、计算前 crash 不构成 exactly-once，并指出会“有执行标记但漏执行” | 准确识别 durable marker 与外部执行事实分歧；下一步检验其能否用 attempt identity 处理过期 owner 恢复后的竞争。 |
| 判断 lease 到期后的旧 attempt 不能只凭 job_id 提交，并提出检查其他 attempt 状态 | 正确识别 attempt 间的资格竞争；教师补充单独查询仍有 race，需在最终写入条件中验证 attempt identity/generation。修正后的独立应用仍待检验。 |
| 判断 generation 7 的 UPDATE 0 表示过期 attempt 被拒绝，因为不满足业务定义 | 正确连接条件更新结果与业务成功条件；这是同一模型内的回答，不证明外部执行去重或完整恢复设计。 |

保留未知项：独立 SQL 编写、真实双连接操作、延迟保持、并发失败恢复。
不据以上摘要建立 usable/retained 评级，也不回写早期 session 的结果。

### 记录边界

缺少可核实的完整教学起止时间/时长，所以本次不补造 v2 session。
没有为编码这些回答而新增 canonical concepts，没有修改 evidence/review-cue
计算；状态引擎原有 resume 可能较旧，当前讨论位置由 navigation 和本课组织器
提供。新增可信 session 之前，生成站点的旧 session resume 不会自动更新。
