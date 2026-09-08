# 从 HTTP request 到受控业务操作

## 单元主线

本单元解释：浏览器发出的请求怎样变成受身份、输入规则和数据库事务约束的
业务操作，以及请求结束后，长任务怎样被其他执行者发现和推进。

它接续 PostgreSQL 的记录身份、事务和并发规则。FastAPI 提供实现案例；学习
目标是区分请求传输、应用判断、事务结果、任务执行和响应所表达的事实。
示例是提交一个绘图要求、保存任务、由后台 Worker 执行并查询结果。

本文件保存稳定的备课框架，不维护第二份“当前下一题”。续课调用：

```bash
python3 scripts/check-teaching-navigation.py resolve --track scientific-ai-platforms
```

以返回的 `resume`、`main` 和分支信息决定当下位置，优先遵守用户当前请求。
既有详细解释和问答保存在[课堂材料快照](../../docs/learning-observations/20260907-http-classroom-notes.md)；
它保留原文，但其中历史性的“下一题”不能覆盖当前导航。

## 完整问题与例子

```text
浏览器提交绘图要求
  → API 解析输入、确认身份与操作权限
  → 应用检查业务条件
  → 数据库事务保存 queued 任务并提交
  → API 返回任务编号
  → 后台 Worker 发现并领取任务，执行、保存结果
  → 浏览器随后查询同一任务
```

`durable_submit` 是案例中自定义的提交函数名，不是 Python/FastAPI 内置功能，
也不作为 canonical term。其承诺是先可靠保存待处理任务，再返回任务编号；
Worker 的存在、领取和恢复机制需要单独实现。HTTP 202 本身只表示请求已接受，
持久化先于响应是此案例的应用约定，不是状态码替服务器实施的保证。

分清两种等待：提交操作等待事务确认，绘图结果在后续交互中取得。浏览器的
异步网络等待不会自动提供后台任务恢复，也不会把普通计算自动转移到其他线程。
先讲清负责推进操作的 actor，再展开 attempt、lease、重复领取等恢复机制。

## 前置证据与观察

[当前前置证据审阅](../../docs/learning-observations/20260907-current-prerequisite-review.md)
区分讲解覆盖、提示后的回答与未检验的独立应用。不要从旧 mastered 文件名或
会话兼容状态推断已会实现 SQL、FastAPI 或分布式恢复。

自然观察节点可以使用“导出一份报告”的新情境：请求已返回编号，但 API 随后
退出。让学习者说明任务应在哪里被找到、由谁执行、客户端以后如何取得结果。
仅在前置解释完成且用户愿意应用时使用；直接澄清照常解释，不扣留答案。

## 发展路线与来源

[Web 历史档案](../../histories/web-programming-history.md)和
[program/process/service 历史档案](../../histories/program-process-and-service-history.md)
提供早期请求与执行者的来源边界。它们不证明现代框架的起源或实现。
当前单元展开新历史内容时仍须按历史证据 gate 核对原始来源。

FastAPI 的[请求体](https://fastapi.tiangolo.com/tutorial/body/)和
[依赖](https://fastapi.tiangolo.com/tutorial/dependencies/)文档分别提供解析验证与
依赖组织机制，不替应用决定授权或事务规则。既有材料的核对日期与详细边界
见课堂快照；未在本次整理中重新验证外部 API 或运行 FastAPI 服务。

## 延后与返回

ASGI 消息内部、完整依赖注入、驱动 API 和部署拓扑按需要展开，不默认成为
入门前置。局部语法问题解释完成后，通过“这一步怎样帮助请求变成可靠任务”
回到主问题；用户明确要求停留或改向时遵守当前范围。

课程下一阶段是一个可运行的纵向案例。是否进入、从哪里进入由当前导航和
实际前置理解决定；读过材料不构成独立实现或长期掌握证据。
