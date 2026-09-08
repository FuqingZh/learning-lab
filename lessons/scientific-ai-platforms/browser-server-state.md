# 浏览器变成应用之后：状态由谁负责

## 当前单元主线

本桥接单元的后续已整理为[从记录身份到并发提交](relational-data-and-transactions.md)。
下列材料保留桥接过程与来源；当前续学位置以新课和 navigation 为准，
不把进入下一阶段解释为全面掌握 React。

- 主问题：浏览器承担更多交互之后，怎样区分界面状态、未提交草稿、服务端
  数据在客户端的副本，以及应独立于页面存活的业务任务。
- 路线位置：从 React 的组件运行方式过渡到数据系统和服务边界。桥接讨论
  已沿既定顺序进入 PostgreSQL 的关系模型、记录身份和 constraints，当前
  衔接多步数据库更新；不提前展开 FastAPI 或改变既定阶段顺序。
- 起点：学习者能用 class/实例数据类比逻辑复用，并在引导情境中选择把提交
  放在点击处理函数中、检查计时器清理；这些观察不证明全面掌握 React。
  学习者指出普通 return/资源清理讲解增量低。既有编程思想只说明映射和差异。
- 示例：一个明确要求“关闭页面后分析仍继续”的系统。区分当前查看的 job、
  页面显示的 job 状态副本和后端负责的任务记录/执行；这是设计例子，不是
  对任何仓库当前实现的声明。
- 下一步：从共享数据不应随单份草稿删除，收清 side effect 不等于错误，
  衔接“新增任务记录并更新草稿状态”需要共同提交的 transaction。
  页面显示与服务端确认的检查留作后续综合情境，不重复细碎提问，
  不从同意或阅读推断掌握。
- 延后：请求代码、缓存库、optimistic update 实现、并发控制与任务恢复内部细节。

## 历史材料与边界

已有[Web 历史档案](../../histories/web-programming-history.md)提供浏览器与
服务器的早期背景。本次新增课堂材料是 Jesse James Garrett 的
[2005-02-18 Ajax 文章保存副本](https://www.oceanpark.com/webmuseum/2005/garrett_on_ajax.html)。
原文比较了请求后返回整页 HTML 的交互与浏览器处理部分交互、按需异步获取
数据的模式，并用 Google Suggest/Maps 举例。其 Q&A 明确不主张 Adaptive
Path 或 Google 发明这些技术，也不主张新模式总是更好。

来源为第三方保存的原文，不冒充原站当前页面；作者的
[2025 回顾](https://jessejamesgarrett.com/2025/02/18/ajax-at-20/)另可核对文章
发表背景，但其中的概括性时代评价不据此推广为历史事实。本课不宣称唯一
技术谱系，也不把 JSON/React 当成 Ajax 当年已存在的必要组成。

## 当前说明与示例边界

- [MDN client/server overview](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/First_steps/Client-Server_overview)：请求、服务端处理与响应。
- [React state lifetime](https://react.dev/learn/preserving-and-resetting-state)：组件位置与 state 的保存/重置；不是业务任务持久化机制。
- 浏览器状态可以按需求保存到 URL 或本地存储；服务端变量也可能仅在内存。
  存在哪里、谁有权确认业务事实、需要存活多久，是不同设计问题。
- 前端保存服务端状态副本并不令副本自动最新；无法连接不能直接推出任务失败。
- 后端任务跨刷新或断连继续，是需要明确实现的应用要求，不是 HTTP 或 React
  自动提供的保证。数据库记录与实际执行/恢复也需要配套设计。

Status: lesson prepared for current continuation; sources inspected 2026-08-31;
no runnable application changed, no independent transfer assessed.

## 通向数据系统：保存内容与接受请求

课堂衔接先澄清：草稿可以持久化到后端数据库；提交也可能仅表示请求被接受、
排队而未开始计算。不能用“是否入库”或“是否立即执行”代替业务含义的区分。
保存草稿本身也是操作，只是不等于提交分析任务。

历史入口使用 Codd 的
[1970 论文及 IBM 保存的摘要](https://research.ibm.com/publications/a-relational-model-of-data-for-large-shared-data-banks)。
摘要明确讨论内部数据表示变化不应迫使用户和多数应用随之改变，并提出以
relations 为基础的模型。这里不声称首次发明、唯一谱系或 SQL 同时产生。
现代草稿/任务表只是帮助理解这个问题的教学例子，不是论文中的历史案例。

[PostgreSQL Concepts](https://www.postgresql.org/docs/current/tutorial-concepts.html)
用于说明 table、row、column 与具体数据库软件的位置；
[Querying a Table](https://www.postgresql.org/docs/current/tutorial-select.html)
用于解释 SELECT / FROM / WHERE 如何表达所需数据。代码是说明性示例，
尚未在本仓库建立数据库或执行 SQL。此处只建立关系模型、查询语言、管理软件
三个层次的联系；随后再讲记录身份与约束，不预先展开事务和并发内部机制。

## 当前延伸：从 constraints 到 transaction

身份与引用部分的说明依据
[PostgreSQL Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)。
primary key 区分记录，不自动去除同一业务请求的重复提交；foreign key
维护引用，不替代授权。删除策略取决于数据生命周期，不能把所有 side effect
都判断为错误；共享数据不等于引用者的专属组成部分。

下一段用同一数据库中的两个写入说明问题：新增 job，并把已有 draft 标记为
submitted。先比较两次分别提交留下半完成结果的风险，再解释 transaction
的 atomicity。示例假设草稿存在、标识合法，只演示两项数据库变化的共同
提交，不宣称解决更新零行、并发重提、科学正确性或外部计算调度。

历史来源是 Jim Gray 的
[1981 The Transaction Concept: Virtues and Limitations](https://www.cs.utexas.edu/~witchel/380L/papers/gray81vldb-transaction.pdf)，
文中把 transaction 讨论为状态变换，并阐述 atomicity 等性质；不声称 1981
是发明时间，也不据发表先后断言由 Codd 论文直接导致。
相关[恢复历史档案](../../histories/volatile-memory-and-durable-state-history.md)
已读取，供后续 durability/recovery 扩展定位，本轮不展开其全部历史节点。
当前行为依据
[PostgreSQL Transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html)。
BEGIN / COMMIT / ROLLBACK 先说明用途；伪代码不作为可执行 SQL 验证。
数据库回滚不自动撤回已发送邮件或已启动的外部计算。
