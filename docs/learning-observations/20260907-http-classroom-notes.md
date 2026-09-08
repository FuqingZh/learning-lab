# HTTP/FastAPI 既有课堂材料快照

保存日期：2026-09-07。下方完整保留整理前的课文，不是原始逐字对话。
包含教学解释、问答摘要与当时的下一步；所有“当前”“下一题”“待回答”均为
历史位置，不决定现在的续课。学习者能力仍须独立的结构化审阅支持。

当前入口：[HTTP/FastAPI 单元](../../lessons/scientific-ai-platforms/http-boundary-and-fastapi.md)。
当前定位：[navigation](../../learning-state/navigation/scientific-ai-platforms.yaml)。

原课文字节 SHA-256：`d7a8111b81e3c2021c900bf98eb6adedcaa0912b5f14b8005eb2a9af81920170`。
下方分隔线之后的原文字节完整保留，原有相对链接的目录深度保持一致。

---

# 从 HTTP request 到受控业务操作

## 当前单元主线

- 主问题：浏览器发来的 bytes 和字段，如何被服务端变成一个经过身份、结构、
  domain rule 与数据库 transaction 约束的业务操作。
- 路线位置：接续 PostgreSQL 的 authoritative state 与并发规则，进入 FastAPI
  阶段；FastAPI 是现代实现实验室，HTTP/service boundary 才是可迁移主线。
- 能力目标：区分 request transport、runtime validation、authorization、
  application operation、transaction 和 response 各自能证明什么。
- 示例：提交 draft D1，创建 queued job J1 与 outbox event E1。前课已经解释
  数据库内共同提交和 worker handoff；本课解释谁有资格调用这条路径。
- 下一步：已详细区分 admission eligibility、unique claim 与 execution success，
  并说明 claim 本身是 durable side effect。当前进入 claim 后、execution 前后
  crash 的 recovery：用 durable run state、attempt/lease 与 committed artifact
  做 reconciliation，避免把 HTTP response 或目录变化误当成 execution truth。
- 延后：ASGI event/message internals、middleware 顺序、完整 dependency injection、OpenAPI
  生成细节、数据库 driver API 和 deployment topology。

## 历史位置与证据边界

1990 年 WorldWideWeb proposal 描述 browser process 向 active server process
发 request，server 定位 information 并返回 node。它建立的是 browser、server、
network request/response 的早期边界，不包含 FastAPI、JSON request body、现代
authentication 或 application service layer。来源见
[Web programming history](../../histories/web-programming-history.md)。

2004 年 W3C Web Services Architecture 将抽象 Web service 与实现它的具体
software agent 区分开，并说明 agent 可以变化而 service 保持。它适用于该文档
的 Web-services architecture，不是所有软件中 `service` 的唯一标准定义，也不
证明它直接导致 FastAPI。来源见
[program/process/service history](../../histories/program-process-and-service-history.md)。

这两个历史节点帮助分开三个问题：网络上传什么 message、哪个 running agent
处理它、对外保持什么 service contract。现代 FastAPI 是处理 HTTP/Python
边界的一种实现，不是这些抽象的来源。

## 先看完整系统，不先背 decorator

假设 browser 发送：

```text
POST /drafts/D1/submit
Authorization: <credential>
Idempotency-Key: K1

{ "expected_revision": 4 }
```

服务端要完成的不是“调用一个 Python function”这么简单，而是一条受控路径：

```text
HTTP request
  → 解析 method/path/header/body
  → runtime validation：字段能否被安全、明确地解释
  → authentication：服务器确认 caller identity
  → authorization：该 identity 能否操作 D1
  → application operation：submit_draft(...)
  → PostgreSQL transaction：条件更新 D1，创建 J1 与 E1
  → COMMIT 后构造 HTTP response
```

这里的层次不是为了多写文件，而是为了防止不同证据互相冒充：

- body 符合 Pydantic model，只证明输入满足已编码的结构与 validation rule；
- credential 被认证，只证明服务器得到一个 identity；
- authorization 通过，才证明该 identity 对 D1 有此次操作权限；
- transaction COMMIT，只证明数据库接受了共同提交的变化；
- `202 Accepted` 与 `status=queued` 只证明任务被接受，不证明计算成功；
- 上述全部通过仍不证明最终 scientific correctness。

FastAPI 官方 request-body 文档说明 Pydantic model 可用于读取 JSON body、转换
类型并验证数据；dependency 文档把 security、authentication 和 role requirement
列为可组织的依赖需求。这些是 framework 提供的机制，不会替应用自动写出正确
authorization 或 domain rule：
[Request Body](https://fastapi.tiangolo.com/tutorial/body/)、
[Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)。

## FastAPI route 与 application operation

FastAPI route 负责把 HTTP 世界翻译成应用可理解的调用，并把结果翻译回 response。
真正的业务操作则应拥有完整 invariant 和 transaction boundary：

```text
route
  接收 HTTP/Pydantic/auth context
        ↓
submit_draft operation
  检查 authority + idempotency + current state
  执行一个 transaction
        ↓
database / outbox
```

这不是说每个项目必须采用同名的 `service.py`。关键是，无论请求来自 browser、
CLI 还是内部 agent，同一个“提交 draft”操作不能各自复制一套稍有不同的 SQL
和 invariant。FastAPI process 可以更换或水平扩容；D1 能否从 editing 变成
submitted 的规则仍应保持一致。

## 第一个边界检查

假设 request body 完全符合 Pydantic model，credential 也能认证出 user A；但
D1 属于 user B。FastAPI 已经成功 parse 和 validate request。服务端是否可以
调用自己的数据库权限提交 D1？请说明 structural validation、authentication
和 authorization 在这里分别已经证明或尚未证明什么。

学习者回答不能，因为不是同一 user；并将 structural validation 解释为输入
结构正确，将 authentication 解释为 request identity 验证通过，将 authorization
解释为权限验证通过。前两个区分正确。需要收紧两点：不同 user 并不自动代表
禁止，管理员、协作者或 delegated authority 可能被 policy 允许；题设当前只
给出了 structural validation 和 authentication，针对 A 操作 D1 的 authorization
尚未执行或证明。若没有这一步，服务端用自己的数据库权限代 A 操作 D1，就会
重现 confused-deputy boundary。该修正后尚未做新的 authority transfer 检验。

## 最小 FastAPI/Pydantic 连接

先看完整片段，再逐行解释；以下名字是教学示例，不是对 case repository 的声明：

```python
from fastapi import Depends, FastAPI
from pydantic import BaseModel, ConfigDict

app = FastAPI()

class SubmitDraftBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: int

@app.post("/drafts/{draft_id}/submit", status_code=202)
def submit_draft_route(
    draft_id: str,
    body: SubmitDraftBody,
    actor=Depends(require_user),
):
    return submit_draft(
        actor_id=actor.id,
        draft_id=draft_id,
        expected_revision=body.expected_revision,
    )
```

这里先只掌握四件事：

1. `SubmitDraftBody` 声明允许的 JSON body shape；`expected_revision` 必须能成为
   `int`。`extra="forbid"` 表示 body 额外传入 `actor_id` 等未声明字段时拒绝，
   而不是把它们悄悄带入业务调用。
2. `@app.post(...)` 把下面的 function 注册为处理该 method/path 的 route；它
   不改变 `submit_draft` 的业务规则。
3. path 中的 `{draft_id}` 进入 function parameter `draft_id`；Pydantic model
   parameter `body` 接收已解析、验证的 request body。
4. `Depends(require_user)` 表示 FastAPI 先调用服务端定义的 `require_user`，从
   credential/auth context 得到 `actor`。这里的 `require_user` 是尚未展开实现的
   server function，不是浏览器传来的字段。业务调用使用 `actor.id`，而不是
   信任 body 自称的 user ID。

这一 route 仍未展示 authorization query 或 transaction。它只把两种来源分开：

```text
caller-controlled input: draft_id, expected_revision
server-established context: actor.id
```

随后 `submit_draft(...)` 必须把二者放到一起，检查 actor 是否有权操作 D1，
再执行前课的 conditional UPDATE、job/outbox insert 与 COMMIT。仅把 actor 注入
route 不等于 authorization 已完成。

检验题（待回答）：攻击者使用 user A 的有效 credential，并在 JSON body 中
额外发送 `"actor_id": "B"`，试图让系统以 B 的身份提交 D1。上面的代码会在
哪里拒绝这个额外字段？即使删掉 `extra="forbid"`，传给 `submit_draft` 的
`actor_id` 又应该来自哪里？

学习者回答：会在 `SubmitDraftBody` validation 时拒绝；即使不拒绝，业务调用
也应使用 `actor.id`，因为它经过验证和检查。前两项正确。需要收紧最后一句：
`actor.id` 是服务端通过 authentication 建立的 identity，不因存在这个 identity
就自动具有操作 D1 的 authority；authorization 仍须结合 actor、目标资源、动作
与当前 policy 单独判断。该修正不影响“身份不能来自 caller body”的结论。

## 为什么 transaction 由 application operation 持有

route 已经解决 transport translation：从 HTTP 得到 `draft_id`、body 和 actor，
再把 operation result 变成 response。接下来真正必须共同成立的是：

```text
actor 当前有权提交 D1
D1 仍是 editing 且 revision=4
idempotency key K1 没有被不同请求占用
创建 J1
创建 outbox E1
```

如果 route 先在 transaction 外查询“有权限”，然后 `submit_draft` 只负责写入，
permission 可能在两步之间变化；如果 job 与 outbox 分别 COMMIT，又会回到前课
的 partial state。因此 transaction boundary 应与完整业务 operation 的 invariant
对齐，而不是与某一条 SQL 或 HTTP decorator 对齐。

教学伪代码如下；它表达所有权与顺序，不绑定某个 Python database API：

```python
def submit_draft(actor_id, draft_id, expected_revision, key):
    with database_transaction():
        require_current_authority(actor_id, "submit", draft_id)

        changed = mark_submitted_if_current(
            draft_id=draft_id,
            expected_revision=expected_revision,
        )
        if changed != 1:
            reject_stale_or_invalid_state()

        job = create_job_once(key=key, draft_id=draft_id)
        create_outbox_event(job_id=job.id)

    return Accepted(job_id=job.id, status="queued")
```

这里 `with database_transaction()` 表示 block 内任何必要步骤失败时，数据库修改
共同 ROLLBACK；成功离开 block 才 COMMIT。`require_current_authority` 不是
FastAPI 自动提供的函数，而是应用 policy 的占位名。真正实现还要根据 authority
存在哪些 table、是否可并发撤销来选择 conditional query、locking 或 isolation；
此处不假装一个伪函数消除了并发问题。

route 因此不决定 business success，只负责映射结果。例如：

```text
Pydantic validation 失败        → 422 类 validation response
没有 authenticated identity    → 401
identity 无权操作 D1            → 403（或按安全策略隐藏资源存在性）
revision/status 已过期          → 409 conflict
transaction 成功并创建 queued J1 → 202 Accepted
```

这些 status mapping 是教学设计示例；具体 API contract 需在 case repository 中
核对，不能仅凭通用习惯断言其现状。

检验题（待回答）：系统规定“authorization 必须在 operation COMMIT 时仍有效”。
route 先查出 A 有权提交 D1；随后 B 撤销 A 的权限；最后 `submit_draft` 只检查
revision/status 并创建 J1。这个 transaction 可以接受吗？authorization 为什么
不能仅在 route 外面提前查一次？

学习者先追问 `route` 和 B 撤销 A 的场景含义，说明原题缺少角色铺垫；随后回答
不能接受，因为要检查目标所属 identity 是否仍有权限，且提前检查后内部权限
被撤销会使旧检查无效。核心结论正确。进一步收紧：job 此时可能尚未创建，检查
对象应是 actor A 对目标 D1 执行 submit 的 current authority，而不仅是“任务的
所属 ID”；owner ID 也不是 collaborator/admin policy 的完整表达。

## route 到底是什么

在 FastAPI 这里，`route` 不是 physical network 经过哪台 router 的传输路线，
而是一条 application-level mapping：

```text
(HTTP method, path pattern) → handler function
```

例如：

```python
@app.post("/drafts/{draft_id}/submit")
def submit_draft_route(draft_id: str):
    ...
```

意思是：FastAPI server 收到 `POST /drafts/D1/submit` 时，path pattern 匹配，
于是调用 `submit_draft_route(draft_id="D1")`。decorator 建立 mapping；下面的
function 是处理此次 request 的 route handler。`endpoint` 在很多 Web 文档中也
会指对外 method/path，或连同 handler 一起指这条边界；使用时要看具体上下文。

### 补全 B 撤销 A 的时间线

原题应先声明：B 是 D1 的 owner，B 曾授权 A 作为 collaborator 执行 submit；
系统 policy 要求 authority 在 operation COMMIT 时仍有效。

```text
t1  A 发 request；route 查到 A 当前被授权
t2  B 撤销 A 的 collaborator permission
t3  submit operation 尝试创建 J1 并 COMMIT
```

若 t3 仍依赖 t1 的旧结论，就会接受已失效 authority。怎样把 permission check
与写入协调，要看 permission 的数据模型、transaction isolation 与并发修改规则；
不能只靠把同一查询从一个 function 移到另一个 function。这里要保留的原则是：
authorization evidence 必须满足系统声明的 decision time，而不是一经查过永久有效。

## Bio Plot Platform 中的一条真实 route

在 case repository commit `f31be7a2a240a958be3e7c10321fa78922333473`，
`routes_agent.py` 有：

```python
@router.post("/api/projects/{project_id}/agent")
async def run_project_agent(request: Request, project_id: str) -> Response:
    ...
```

因此，`POST /api/projects/P1/agent` 会匹配 `project_id="P1"` 并进入
`run_project_agent`。该 handler 随后取得 current user、读取 project metadata、
检查 `created_by == current_user` 且 project 未 deleted/archived，再处理 body、
claim run 和 agent stream。这是代码事实，不证明每个 FastAPI route 都应采用
相同组织方式。

尤其要注意：FastAPI 不强迫 route 必须“薄”。case 中这个 handler 承担了不少
orchestration。把 business operation 抽成独立 function 是一种帮助复用和集中
invariant 的设计选择，不是 `@router.post` 自动提供的性质。前文“route 只负责
翻译”应理解为准备采用的责任边界，而不是 framework 或现有 case 的普遍事实。

case 的 `get_current_user` 从 `X-Bio-Plot-User` header 取得并规范化 identity；
仅看这个 function 只能证明 header presence/shape 的检查。该 header 是否由可信
gateway 注入、是否能被外部 caller 伪造，必须结合 deployment boundary 判断，
不能仅凭函数名宣称完整 authentication 已成立。

检验题（待回答）：对真实 mapping
`POST /api/projects/P1/agent → run_project_agent(project_id="P1")`，哪一部分是
route mapping，哪一部分是 handler runtime execution？仅看到
`get_current_user` 校验 header 格式，能否证明 caller identity 已被可信认证？

学习者回答：decorator 是 route mapping；request 被匹配并开始运行
`run_project_agent` function body 是 handler runtime execution；header presence
和格式检查不能证明可信 authentication，还要核对外部注入和 credential。三项
边界正确。需补一个执行主体修正：`@router.post` 在 application setup 时注册
mapping，并不在每次 request 上亲自解析 POST；运行时匹配和 parameter extraction
由 server/application routing machinery 完成。

## setup time 与 request time

FastAPI program 中有两段不同时间：

```text
application setup time
  import Python modules
  创建 APIRouter
  执行 decorator，保存 method/path/function mapping
  main FastAPI app include_router(...)
  server 开始提供服务

request time
  server 收到 HTTP request
  application router 匹配 method/path
  提取 path parameter，解析/验证其他 parameter
  执行 dependencies
  调用 handler function body
  把返回值或 exception 转成 response
```

在 case commit 中，`routes_agent.py` 的 decorator 先把 mapping 放进
`agent_router`；`api/app.py` 随后调用 `app.include_router(agent_router)`，才把这组
route 纳入 main FastAPI application。function 仅仅存在于 Python module 中，
并不会自动成为可访问的 HTTP endpoint。

### ASGI 在哪里

case dependency 包含 Uvicorn。Uvicorn 是运行 Python Web application 的 server；
FastAPI application 与这类 server 之间使用 **ASGI**（Asynchronous Server
Gateway Interface）。ASGI 是 server 与 Python application 交互的标准接口，
不是 browser 使用的网络协议，也不是 FastAPI route 本身。

```text
browser
  │ HTTP over network
  ▼
Uvicorn server process
  │ ASGI interface
  ▼
FastAPI application
  │ method/path routing + validation/dependencies
  ▼
run_project_agent handler
  │ application calls
  ▼
store / agent / external execution
```

ASGI specification 将 protocol server 与 Python application 分开：server 以标准
形式 dispatch incoming connection/request information，application 通过 `scope`、
`receive`、`send` 接口交互。本课只定位这条 interface，不展开 event message
格式。[ASGI specification](https://asgi.readthedocs.io/en/latest/specs/main.html)

FastAPI 官方文档说明 `APIRouter` 可声明一组 path operations，再由 main app
`include_router`；这支持上面的 setup-time registration，不代表所有 framework
内部实现完全相同。[FastAPI Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)

检验题（待回答）：`run_project_agent` function 仍在 module 中，decorator 也已
把它注册进 `agent_router`，但 main app 删除了 `app.include_router(agent_router)`。
Uvicorn 和 FastAPI 都正常运行时，`POST /api/projects/P1/agent` 能否仅凭 function
存在而找到它？为什么？

学习者回答不能，因为 mapping 虽已在 `agent_router`，删除 `include_router` 后
没有进入 main app，HTTP POST 找不到 function。判断正确。收紧措辞：function
仍可被 Python import 或直接调用；“找不到”限定为 main app 的 HTTP routing table
没有匹配项，在没有其他相同 mapping 时会走 no-match/404，而非函数从程序消失。

## FastAPI 是否总会自动做 Pydantic body validation

不会。FastAPI 根据 handler signature 和 route declaration 决定哪些参数由
framework 提取与验证。下面两种写法不同：

```python
# framework 根据 model parameter 解析并验证 body
def submit(body: SubmitDraftBody):
    ...

# handler 获得 Request object，应用代码决定何时读取和怎样解析 body
async def run_project_agent(request: Request, project_id: str):
    ...
```

case 的 `run_project_agent` 使用第二种。按当前 code order：

```text
1. require_agent_user(request)
2. load project metadata + project_is_available(...)
3. check agent availability
4. body = await request.body()              # 得到 bytes
5. len(body) > limit                        # 过大返回 413
6. AGUIAdapter.build_run_input(body)         # 解析 protocol payload
7. sanitize_agent_run_input(...)             # 进一步 application checks
8. parsing/validation 失败返回 422
9. claim_agent_run(...) 重复则返回 409
```

因此，`@router.post` 只建立 method/path mapping，不等于“所有 JSON 会自动经过
Pydantic model”。`Request` 代表 request context；`await request.body()` 才在这个
handler 中取得 body bytes，而 `AGUIAdapter` 与 `sanitize_agent_run_input` 承担
此 endpoint 选择的解析和 validation。这里的 `async`/`await` 细节暂不展开，先
保留“读取 body 可能等待 I/O，因此 function 可在该点暂停”的直觉。

顺序本身也是 contract。按可见 handler code，一个没有有效 user identity 的
request 会先走 401 分支，而不是先进行 AG-UI payload semantic validation。网络
server 或 gateway 仍可能在进入 handler 前按自己的 transport limits 拒绝请求；
这里只陈述此 handler 内的顺序，不把它扩展为整个 deployment 的唯一顺序。

检验题（待回答）：假设没有 gateway/transport 层提前拒绝。一个 request 同时
缺少所需 user identity header，而且 body 也是非法 AG-UI payload。按当前
`run_project_agent` 的 code order，application 会先返回 identity error，还是先
解析 body 并返回 422？为什么？

学习者回答会先返回 identity error，因为 code 先验证 identity，再读取和解析
body。判断正确；限定在题设排除 upstream rejection 且当前 handler control flow
未改变的范围内。这不能外推为 FastAPI 固定先 authentication 后 body validation，
也不证明 header identity 的 trust source 已建立。

## 一个 response 可以故意合并多种内部原因

identity 检查通过后，case 读取 project metadata，并调用：

```python
def project_is_available(metadata, current_user):
    return bool(
        metadata is not None
        and metadata.created_by == current_user
        and metadata.deleted_at is None
        and metadata.archived_at is None
    )
```

下面任一情况都会得到同一个对外 response：

```text
project 不存在
project 存在但属于另一个 user
project 已 deleted
project 已 archived
        ↓
404 PROJECT_NOT_FOUND
```

所以这个 API contract 中的 404 不能被 client 解释成“数据库中一定没有这条
project record”。它只说明：在此次 authenticated identity 与当前 visibility
policy 下，application 不向 caller 提供这个 project。

这种统一 response 使 caller 不能仅从 status code/body 区分“资源不存在”和
“资源存在但无权访问”。这是当前代码可观察到的 information-hiding effect，
不证明整个 deployment 没有 timing、logging、cache 或其他 side channel，也不
自动证明 authorization policy 本身正确。

顺序现在可以完整读成：

```text
identity 不成立                         → 401
identity 成立，但 project unavailable   → 404
project available，但 agent unavailable → 503
随后才读取/检查 body                    → 413 或 422
run identity 已存在                     → 409
```

检验题（待回答）：user A 带着格式合法且来自可信来源的 identity，调用
`POST /api/projects/P1/agent`，得到 `404 PROJECT_NOT_FOUND`。仅凭这个 response，
A 能否断言 P1 在 store 中根本不存在？还可能有哪些被当前 contract 合并的原因？

学习者回答不能，并提出 identity binding 错误、deleted 和“过时”。核心“不
能从 404 推断 store absence”正确。当前 function 直接合并的原因是 nonexistent、
wrong owner、deleted、archived；identity binding 错误属于更上游 fault，若发生
会在这里表现为 wrong-owner mismatch，但不是 `project_is_available` 能诊断出的
根因。“过时”只有在指 archived 时符合当前条件；stale revision 不在这段判断中。

## validation 之后才 claim run identity

通过 identity、project、agent availability 和 body validation 后，handler 才调用：

```python
claimed = claim_agent_run(
    store,
    project_id=project_id,
    run_id=sanitized.run_id,
    current_user=current_user,
)
```

`claim_agent_run` 创建一个 pending timeline event，并使用：

```text
dedupe_key = "agent-run:" + run_id
```

在 PostgreSQL store implementation 中，`(project_id, dedupe_key)` 有 unique index；
insert 使用 `ON CONFLICT DO NOTHING`。第一个成功插入 proposed event 的 request
取得 claim；后来的相同 logical run 读回 existing event，`claimed=False`，handler
返回 `409 AGENT_RUN_ALREADY_EXISTS`。

这把前课的抽象映射到真实 case：

```text
logical operation identity: project_id + run_id
stable dedupe identity:      project_id + "agent-run:" + run_id
first accepted claimant:     插入 pending event
duplicate claimant:          unique conflict → 409
```

claim 的位置同样重要。如果在 authentication、project authority 或 payload
validation 之前就持久化 claim，一个无权或格式错误的 request 也可能抢占 R1，
使后来的合法 request 被当作 duplicate。这不是重复执行，而是 invalid claimant
污染了 operation identity。当前 handler 先完成前置 gates，再 claim；这只说明
当前可见顺序，不能由此推断 claim 后全部 agent execution 一定成功。

另外，409 证明的是同一 project/run identity 已有 accepted claim，不证明旧 run
已成功完成。是否返回旧状态、拒绝、恢复或继续 stream，是更高层 API semantics；
当前 route 选择直接返回 conflict。

检验题（待回答）：如果系统把 `claim_agent_run(project_id=P1, run_id=R1)` 移到
authentication 和 payload validation 之前，攻击者发送非法 request 却先占用了
R1。随后合法 user 用相同 R1 重试会看到什么？这时 duplicate detection 本身
虽然正常工作，为什么整体行为仍然错误？

学习者要求更详细解释，因此该题转换为 guided explanation，不再作为未提示
retrieval evidence。完整答案是：合法 request 会看到 existing claim，并在当前
route 得到 `409 AGENT_RUN_ALREADY_EXISTS`；unique/dedupe mechanism 正确阻止了
第二次 claim，但第一个 claimant 本来没有 admission eligibility，所以系统持久化
了不应存在的 reservation，并拒绝了后来合法的 operation。

### 三个不同问题不能由一个 unique index 代答

```text
admission：这个 request 是否有资格占用 R1？
uniqueness：符合资格的 requests 中，谁先取得 R1？
completion：取得 R1 的 request 后来是否真的执行成功？
```

对应到当前 handler：

| 阶段 | 回答的问题 | 失败时是否应留下 claim |
| --- | --- | --- |
| authentication | caller identity 是否成立 | 否 |
| project availability / authority | caller 是否可对 P1 发起 run | 否 |
| payload validation | bytes 是否构成允许的 AG-UI operation | 否 |
| `claim_agent_run` | 合格 request 是否先取得 P1/R1 | 是，pending |
| agent execution | 已取得 claim 的 run 是否完成 | claim 已存在，另记 terminal outcome |

unique index 只看到 `(project_id, dedupe_key)` 是否已存在。它不知道第一个 insert
来自已认证 owner 还是 attacker，也不知道 payload scientifically/structurally valid，
更不知道后面的 execution 是否成功。数据库约束正确执行，只能证明 uniqueness
contract；如果调用它之前的 admission protocol 错了，整体仍然错误。

### claim 为什么已经是 side effect

在 claim 之前：

```text
store 中没有 P1/R1
合法 request 将来仍可能取得 R1
```

claim 之后：

```text
store 中存在 PENDING event for P1/R1
后续相同 R1 的 request 会得到不同结果（当前 route 为 409）
```

因此 claim 不是只读检查，也不是临时 local variable；它改变 durable store 和
未来 request 的行为，是 side effect。即使 agent 一行都没执行，这个 side effect
也已经发生。

### 正确顺序与错误顺序对比

```text
当前顺序
identity → authority/target → body validation → claim → execution
     任一前置 gate 失败：不占 R1

错误顺序
claim → identity → authority/target → body validation → execution
  非法 request 已占 R1；后面的拒绝不能自动撤销既有 claim
```

即使错误顺序在发现 invalid request 后尝试删除 claim，也会新开 race：其他
request 可能已经看见 claim 并返回 409，或 cleanup crash 后永久残留。因此不能
把“先写、之后再删”当成与“先验证、再写”自动等价。若系统确实需要 provisional
reservation，就必须把 provisional state、expiry、ownership 和 recovery 明确建模，
不能仍把它当作 accepted claim。

当前顺序解决的是“invalid request 不应先占 identity”。它仍不解决另一个 failure
window：合法 request 通过所有 gates，成功写入 PENDING claim，随后 process 在
agent execution 开始前 crash。此时 admission 和 uniqueness 都正确，completion
仍然未知。

新检验题（待回答）：合法 P1/R1 通过所有 gates，并成功写入 PENDING claim；
server 随即在 agent execution 前 crash。client 用同一 R1 retry，当前 route 看到
existing claim 并返回 409。这个 409 能证明 execution 已开始或成功吗？系统还
缺少哪一类 recovery/reconciliation 信息？

学习者回答不能，并提出同时保存 execution 返回状态与盘上结果，再组合判断。
“409 不能证明 execution 开始或成功”正确；把 control-plane state 与 artifact
互相核对也是正确方向。但不能直接把“文件正在增长”等同于正在执行，也不能把
“没有返回且文件不变”等同于失联：queued job 可能尚未产出文件，长计算可能暂时
不写盘；反过来，增长的文件也可能来自旧 attempt、另一 attempt、buffer flush 或
一个已经失去执行权的 process。

### 不让目录现象代替 execution protocol

client 是否收到 HTTP response 是弱证据。server 可能已经持久化状态，但 response
在网络中丢失；因此 recovery 需要读取 server-side durable state，而不是依赖 client
记忆的“是否返回”。至少要把三个身份分开：

```text
run_id R1       同一个 logical operation
attempt_id A1   某一次具体 execution attempt
artifact set V1 这次 attempt 准备发布的一组结果
```

一个可恢复的最小模型通常需要以下 authoritative records：

| durable evidence | 它能回答什么 | 它不能单独证明什么 |
| --- | --- | --- |
| `status=pending/queued` | R1 已被接受、等待执行 | worker 已开始 |
| `status=running` + matching `attempt_id` + fresh heartbeat/unexpired lease | 系统目前把执行权交给哪个 attempt，且租约尚有效 | process 绝对存活、结果正确 |
| expired lease | 原 execution ownership 已失去时效，需要 recovery | 旧 process 已经停止 |
| terminal `failed` + reason | 系统记录该 attempt 失败 | 所有 retry 都应永久禁止 |
| terminal `succeeded` + verified committed artifact manifest | 按 operation contract，执行和结果发布已完成 | scientific correctness |

这里的 heartbeat/lease 不是为了把 distributed execution 变复杂，而是回答一个目录
回答不了的问题：**现在谁仍被允许代表 R1 提交结果？** 如果 A1 lease 过期后 A2
接管，A1 即使后来恢复并继续写文件，也不应覆盖 A2 的结果；系统还需用 generation
或 fencing check 拒绝 stale attempt 的 commit。

### result artifact 也需要 commit boundary

“盘上出现一个文件”通常不应直接成为 `succeeded`。更可靠的发布顺序是：

```text
A1 写入 provisional/temp output
  → 检查 required files、size/checksum 等 encoded contract
  → 原子地发布 artifact manifest 或 promote 整组结果
  → durable state 变为 succeeded，并引用该 committed manifest
```

因此可以收紧学习者提出的四种判断：

| 观察 | 能下的结论 |
| --- | --- |
| durable `succeeded`，但 contract 要求的 committed artifact 缺失 | invariant violation；进入 error/reconciliation，不能报成功 |
| durable `succeeded`，且对应 attempt 的 committed artifact 验证通过 | operation 按已编码 contract 成功；仍不证明 scientific correctness |
| 没有 client response，目录中文件增长 | 只有 provisional activity evidence；不能据此断言当前合法 attempt 正在健康运行 |
| 没有 client response，目录无结果或结果不变 | execution outcome unknown；还要查 queue、attempt、heartbeat/lease 与 executor readback，不能直接定为失联 |

### 把四种“状态”还原成物理过程

严格说，上表不是四个 mutually exclusive system states，而是 observer 在某一时刻
看到的四种 evidence combinations。以生成 `plot.png` 的 R1 为例，物理系统中同时
存在四个位置：browser 保存自己是否收到 HTTP response；FastAPI process 接收和
转发请求；PostgreSQL 保存 durable run/attempt state；worker process 在 filesystem
写 artifact。它们不会在同一个 CPU instruction 中同时改变，任意两步间都可能
crash 或断网。

#### 组合一：client 收到或数据库记录 success，但 required artifact 不存在

一种错误实现可能按以下顺序运行：

```text
worker 完成内存中的绘图计算
→ UPDATE runs SET status = 'succeeded'
→ process crash
→ 本应写入或发布的 plot.png 没有完成
```

如果 HTTP response 已在 `UPDATE` 后发出，browser 甚至会看到“成功”，但下载时
得到 404。这里不是简单的 filesystem error，而是两个事实互相矛盾：control record
声称 operation 的输出已经完成，data record 却不满足 success contract。

代码方向不是在读取页面时临时伪造一个空图，而是让 success transition 依赖已经
验证并 committed 的 artifact：

```python
manifest = artifact_store.commit(attempt_id, provisional_files)

store.mark_succeeded(
    run_id=run_id,
    attempt_id=attempt_id,
    manifest_id=manifest.id,
)
```

`mark_succeeded` 还应检查 attempt 是否仍拥有有效 execution authority，以及 manifest
是否属于这个 attempt。若旧数据已经出现 `succeeded + missing artifact`，读取端应把
它报告为 invariant violation 并交给 reconciliation/repair，而不是继续向用户声称成功。

设计思路是：**terminal success 必须引用可以验证的 committed result**。它不能只
表示“worker 的主要计算函数曾经 return”。

#### 组合二：durable success 与 committed artifact 都存在

理想物理顺序是：

```text
worker A1 计算
→ 写 provisional/plot.png
→ 验证文件完整性
→ 发布 manifest M1，M1 指向确定的 artifact/checksum
→ 数据库把 R1/A1 标为 succeeded，并引用 M1
→ API 查询到该状态并返回给 browser
```

最后一步 response 即使丢失也不破坏事实。browser retry 后可以按 `run_id=R1` 查询到
同一 durable result。代码读取的是数据库和 manifest，而不是创建 R2：

```python
run = store.get_run("R1")
if run.status == "succeeded":
    manifest = artifact_store.get_manifest(run.manifest_id)
    verify_manifest(manifest)
    return RunResult(status="succeeded", artifacts=manifest.files)
```

这里的“成功”仍然有边界：它证明程序按照 encoded operational contract 生成并发布
了结果，不证明选择的统计方法正确，也不证明图具有 scientific correctness。

#### 组合三：client 没有 response，但 artifact 正在增长

可能的正常过程是：

```text
FastAPI 接受 R1，数据库记为 queued
→ worker A1 取得 lease，记为 running
→ browser 与 API 的连接中断
→ A1 持续写 provisional/plot.png
```

但相同的目录现象也可能来自异常过程：

```text
A1 的 lease 过期
→ controller 已允许 A2 接管 R1
→ A1 没有及时停止，仍继续写旧文件
```

所以 `file_size_now > file_size_before` 只能成为 diagnostic observation，不能驱动
run state machine。代码应先查询 durable attempt ownership：

```python
attempt = store.get_current_attempt("R1")

if attempt.status == "running" and attempt.lease_until > now:
    return RunResult(status="running")

if attempt.lease_until <= now:
    schedule_reconciliation(run_id="R1", attempt_id=attempt.id)
    return RunResult(status="recovering")
```

真实实现还要使用 database/server time 并在 commit artifact 时再次检查 attempt
generation，避免 A1 在 lease 过期前检查通过、过期后仍完成 stale commit。

设计思路是：**activity 与 authority 是两件事**。一个 process 仍在消耗 CPU 或写
bytes，不代表它仍有权决定 R1 的最终状态。

#### 组合四：client 没有 response，artifact 不存在或暂时不变

这一观察对应的现实过程最多，不能直接归为“失联”：

```text
情况 A：R1 仍 queued，尚无 worker 领取
情况 B：A1 正在读取大数据，还没进入写图阶段
情况 C：A1 正在计算，算法很久才产生第一个文件
情况 D：A1 被资源阻塞，但 heartbeat 仍正常
情况 E：A1 process 已 crash，heartbeat 停止且 lease 最终过期
情况 F：A1 已完成，但 artifact 写到了错误位置或 publication 失败
```

这些情况在 filesystem snapshot 中可能完全相同。代码必须先按明确顺序读取：

```text
1. run 是 queued、running 还是 terminal？
2. current attempt 是谁？
3. heartbeat 是否更新，lease 是否仍有效？
4. executor/queue 是否仍认识这个 attempt？
5. 是否存在 provisional 或 committed manifest？
```

只有 failure detector 所采用的条件满足，例如 lease 已过期并且 authoritative executor
readback 也找不到有效 attempt，系统才可以进入 recovery。即便如此，更准确的结论
也是“系统不再承认 A1 拥有 execution lease”，不等于从哲学上证明旧 process 已死亡。

设计思路是：**unknown 必须作为可表达的状态保留下来**。系统不知道时，不应为了
给 UI 一个简洁答案而猜成 `running`、`failed` 或 `succeeded`。

#### 代码上不要写成一个四分支函数

四种观察混合了不同来源，因此更稳妥的 code structure 是让不同 component 各自
拥有一个职责：

```text
API route
  接受/查询 R1；不凭 HTTP connection 判断 execution

run store
  保存 run state、attempt identity、lease、terminal outcome

worker/controller
  领取 lease、heartbeat、执行、触发 recovery

artifact store
  保存 provisional files，并原子发布 committed manifest

reconciler
  对照 run、attempt、executor 与 artifact，处理矛盾或过期状态
```

状态 transition 也应由 conditional update 保护。例如只有仍持有 A1 generation 的
worker 才能把 R1 从 `running` 改为 `succeeded`。这样 `if file.exists()` 是 artifact
validation 的一部分，而不是整个 distributed operation 的真相来源。

### 从物理过程到三个 stored objects

Database 不是自动感知物理世界的仪表盘。它只保存各 process 成功提交给它的 records；
worker 已 crash，旧的 `running` 字样也不会自动消失。因此不要让一行 `runs.status`
同时冒充 logical operation、process activity 和 artifact truth。一个最小模型可分成：

```text
run R1
  用户要求完成的 logical operation
  保存 overall state 和最终采用的 result

attempt A1/A2
  某个 worker 对 R1 的一次具体 execution
  保存 execution ownership、heartbeat、lease 和 outcome

artifact manifest M1
  某个 attempt 正式发布的一组 result identities/checksums
```

它们的关系不是“一行数据不断改名”，而是：

```text
R1 ── has attempts ──> A1, A2, ...
R1 ── current attempt ──> A2
R1 ── committed result ──> M2
M2 ── produced by ──> A2
```

`run` 的 `queued` 表示工作已 durable admission，但没有 execution ownership；
`running` 表示 Database 当前记录一个 attempt 被授权执行，不是实时 process probe；
`succeeded` 应引用 committed manifest；`failed` 表示按当前 retry policy 已形成 terminal
outcome。一次 attempt 失败不必自动令整个 run failed：controller 可能为 R1 创建 A2。

正常 transition 可以还原为：

```text
R1 queued, no attempt
→ worker W1 conditional claim
→ R1 running, current=A1; A1 lease valid
→ A1 heartbeat renews lease while computing
→ A1 publishes M1
→ conditional commit verifies R1/current=A1/generation/lease
→ R1 succeeded, committed_manifest=M1
```

如果 A1 crash，Database 仍可能显示 `running`；只有 heartbeat 停止、时间越过 lease，
controller 才把它当作 stale ownership 并进入 recovery。A2 接管后，A1 的旧 process
即使恢复，也必须因 attempt/generation 不匹配而无法提交 R1。

另一个重要 failure window 是：A1 已发布 M1，却在把 R1 改为 `succeeded` 前 crash。
此时 `R1=running` 与 `M1=committed` 并存。M1 不是自动胜者；reconciler 需要核对它
是否由 R1 当前被授权的 A1 生成、是否满足 result contract，以及期间是否已有 A2
接管。核对通过才可完成 transition；否则把 M1 保留为可审计但不被采用的 artifact，
而不是盲目让 A2 重算或盲目标记 success。

回到原 failure window：如果只有 `PENDING claim`，没有 execution attempt record，
系统应能表达“已接受但尚未开始”，而不是只用 409 把 caller 挡回去。retry 可以读取
并返回同一个 R1 的 current state；recovery controller 则判断是否创建/恢复一个
attempt。duplicate request、duplicate attempt 与 duplicate artifact publication 是
三个不同问题，不能由一个 unique claim 一次性解决。

新检验题（待回答）：数据库里 R1 是 `running`，A1 的 lease 已过期；结果目录里
一个 PNG 仍在增长，但没有 committed artifact manifest。系统能否因此把 R1 标为
`succeeded`？如果不能，这三条证据分别说明什么，recovery 接下来最先要确认什么？

该题在 guided explanation 中已回答：不能。`running` 是可能 stale 的 stored claim；
expired lease 表示 A1 的 execution authority 已过期，但不证明 process 已停止；PNG
增长只表明 activity，且没有 manifest 就没有 committed result。recovery 先确认当前
execution ownership/executor state，并 fence stale A1，再决定恢复还是创建新 attempt。

下一检验题（待回答）：A1 已发布 committed manifest M1，但在把 R1 从 `running`
改为 `succeeded` 前 crash；随后 A1 lease 过期。reconciler 发现 M1 完整存在。它能否
仅凭 M1 存在就把 R1 标为 `succeeded`，或直接创建 A2 重算？在两者之前必须核对哪些
identity、authority 与 result-contract 关系？

学习者先追问三类条件。当前说明把它们固定为：identity 检查 `A1→R1`、`M1→A1/R1`
以及 project/user/dataset/revision/generation provenance；execution authority 检查 A1
是否为合法 current attempt，以及 M1 的接受是否经过当时有效的 lease/generation
fencing；result contract 检查 manifest committed、required artifacts、checksum/schema、
accessibility 和 input binding。三组通过仍只支持 operational success。

### M1 存在与 M1 被 authoritative acceptance 是两回事

单看 storage 中的 M1 及其 timestamp，不能证明它在 A1 lease 有效时被系统接受：
worker clock 可能偏差，上传跨过 expiry boundary，A2 也可能已在并发接管。需要一个
由 execution authority owner 在 commit boundary 写入的 durable acceptance record，
或让 manifest admission 和 run terminal transition 处于同一 database transaction。

一种较简单的实现顺序是：

```text
A1 上传 immutable provisional objects
→ A1 请求 complete_attempt(R1, A1, generation=1, file descriptors)
→ server 开启 database transaction 并锁定/conditional read R1
→ 检查 current_attempt=A1、generation=1、lease valid
→ 验证 objects 和 result contract
→ 在同一 transaction 插入 accepted manifest M1
   并把 R1 改为 succeeded、引用 M1
→ COMMIT
```

这样 Database transaction 的结果只有两类：manifest acceptance 与 `succeeded` 一起
可见，或二者都不可见。若 worker 上传后、transaction 前 crash，只留下 unaccepted
objects，可以清理或复用，但不能冒充成功；若 COMMIT 后 HTTP response 丢失，retry
读取 R1/M1 即可返回已有 success，不创建 A2。

若现有 architecture 让 manifest acceptance 与 run update 位于两个不能共同 transaction
的 durable systems，就必须保留中间状态和 reconciliation evidence，不能用 object
mtime 猜测。reconciler 的决策次序是：

```text
1. lock/read current R1，防止检查期间 A2 又接管
2. 核对 A1/R1/generation 与是否已有 A2
3. 找 M1 的 authoritative acceptance，而非仅找文件
4. 验证 result contract 与 immutable content identity
5. 证据闭合：finalize R1 succeeded
6. authority 冲突：不采用 M1，fence A1，跟随当前 attempt
7. evidence 不足：保持 unknown/recovering，不猜 success
8. 已确认没有有效 accepted result 和 active attempt：才安排 A2
```

因此“补记成功”和“重新执行”都不是默认动作。前者可能采用 stale/错误结果；后者
可能造成昂贵 duplicate computation，甚至让 A2 与仍活动的 A1 并发发布。recovery
先恢复事实和 authority，再选择 transition。

新检验题（待回答）：A1 已上传 provisional files，随后调用 `complete_attempt`；server
在同一 PostgreSQL transaction 中验证 A1 authority、插入 M1 并把 R1 改为 succeeded，
COMMIT 也已完成，但返回给 A1 的 HTTP response 丢失。A1 用同一 completion identity
retry。系统应创建 M2/再次执行，还是读取并返回已有 R1/M1？这个 retry 能证明什么，
又仍不能证明什么？

学习者回答先核对 `R1→A1→C1→M1`，检查 M1 与 R1 状态，确认后复用并返回 success。
方向正确：retry 不创建新的 completion、manifest 或 attempt。还需核对相同 C1 的
request/content hash 未改变，并把返回语义收紧为“返回 R1/C1 已持久化的原 terminal
outcome”；A1 是否也存为 succeeded 取决于 data model，不能只靠 response 临时推导。
已接受 manifest 的完整 validation 不必在每个 client retry 都从头执行，但当前读取
仍可按 availability/integrity policy 检查 artifact 是否可提供。该结果证明 operational
completion 被 durable commit，并不证明 scientific correctness。

### 回到 HTTP boundary：submit、status 与 completion 是三种 operation

长任务不需要把一个 browser connection 从开始计算一直保持到结束。更清晰的 HTTP
surface 把三个不同 actor、authority 和 side effect 分开：

```text
Browser → POST /runs
  请求接受 logical run R1
  返回 202 + R1 identity/status location

Browser → GET /runs/R1
  读取 durable current state
  不创建 attempt，不重做计算

Worker/controller → complete_attempt(R1, A1, C1, ...)
  内部提交一次 execution 的结果
  必须验证 attempt authority 和 completion idempotency
```

submit response 丢失时，client 用相同 operation identity 重试或查询 R1；status query
是 read，不因重复调用产生新的 execution；completion retry 用相同 C1 返回已提交的
terminal outcome。三者共享同一个 R1，但不是同一个 operation，也不应共享同一组
authorization：能查看自己的 R1，不代表 browser 可以冒充 worker 完成 A1。

这也解释 `202 Accepted` 的边界。它表示 server 已接受 request 进入异步处理，并不
表示 A1 已开始、M1 已存在或 R1 已成功。response 可提供一个后续查询位置，例如
`Location: /runs/R1`；之后 UI 显示 queued/running/succeeded/failed，应来自 durable
status read，而不是原 POST connection 是否仍存在。

当前 case route 对 duplicate run identity 返回 409，这是其当前 public semantics；
另一种 API contract 可以对相同且内容一致的 submit retry 返回既有 R1。两者都需要
明确 contract，不能仅由 unique index 决定 client-visible behavior。

下一检验题（待回答）：Browser 成功提交 R1 后只得到 `202 Accepted` 和
`Location: /runs/R1`，随后立刻 `GET /runs/R1` 得到 `status=queued`。这两个 response
分别证明了什么？如果 Browser 连续调用 GET 十次，是否应该创建十个 attempt，为什么？

学习者回答：202 证明 identity/authority gates 通过且 Run identity 创建成功；GET
十次不应创建十个 attempts，因为 attempt 是同一 run 的 execution try，健康执行时
不需因查询而重复创建。核心正确。边界需收紧：HTTP 202 的通用语义只是 accepted，
只有在本 endpoint contract 明确规定 authentication/authorization 和 durable insert
先于 response 时，才可据它推断这些 gates/commit；随后的 GET queued 是独立 readback。
另外，多 attempts 应保持相同 logical operation/input contract，但物理环境、时间和
non-deterministic computation 可能令 execution/output 不同，不能说执行内容必然相同。

### Asynchrony：用 stable identity 跨过不连续的时间

这里的核心矛盾不是“计算慢”，而是 browser HTTP connection 的 lifetime 与后台 work
的 lifetime 不同。若 browser 必须保持同一个 call 等到最终图生成，caller 的控制流
停在 `result = compute()`，connection/request context 承载整个未完成操作；任一 proxy
timeout、断网或页面关闭都会让 client 不知道后台事实。

异步 job protocol 把一段长时间耦合拆成多个短 interaction：

```text
interaction 1: submit → durable R1 → 202
无 HTTP connection 的期间: worker 执行 A1，Database 保存进度
interaction 2..n: GET R1 → current durable state
final interaction: GET R1 → succeeded + M1
```

消失的是持续等待的 connection/call stack；替代它的是 `run_id=R1` 和 durable state。
因此这里 asynchrony 的本质是：caller 发起 operation 后，可以在 operation 最终完成
前继续；双方以后借稳定 identity 重新关联，而不是靠原调用仍挂着。

这不等于 parallelism。一个 single worker 可以依次处理许多 asynchronously submitted
runs；反过来，一个 synchronous request 内部也能用多核 parallel computation，但
caller 仍等待最终 response。它也不等于“快”：async job 可能很慢，价值是解除 lifetime
coupling，并明确表达 queued/running/terminal/unknown 与 retry/recovery。

还要区分两个层次：Python `async def`/`await` 主要解决一个 process 内等待 I/O 时如何
让 execution context 暂停、event loop 转去推进其他 work；`202 + R1 + worker` 解决的
是跨 request/process/crash 的 durable workflow。一个 `async def` handler 可以一直
await 30 分钟才 response，仍是 client-level synchronous completion；普通 `def` route
也可以 durable insert R1 后立刻返回 202，形成 asynchronous job protocol。语法不会
自动提供 durable identity、queue、idempotency 或 recovery。

采用 asynchronous job protocol 后，原先由 call stack 暂时保存的“做到哪里”，必须
外化为可恢复 records：R1 identity、state transition、attempt/lease、result manifest、
status read/notification 和 retry contract。这是额外设计成本，也是 process crash 后
还能恢复的来源。

下一检验题（待回答）：下面两段分别在哪一个层次 asynchronous？

```python
# A
async def route():
    result = await run_analysis_for_30_minutes()
    return result

# B
def route():
    run_id = durable_submit()
    return Accepted(run_id)
```

Browser 在 A 中是否必须等待最终 result？B 即使没有写 `async def`，为什么仍可形成
asynchronous job protocol？

学习者回答 A 在 route 层面异步而 route 仍等待 run，B 在 durable 层面异步，并正确
判断 Browser 在 A 中仍等待最终 result；但随后的“只返回 id、交给 Accepted 后续做”
描述的是 B，且 `Accepted` 不是执行 actor。更准确地说，A 在 Python coroutine/event-loop
scheduling 层使用 async/await，route 的 response dependency 仍等待 analysis；`await`
也不证明 analysis 内部串行或并行。B 的 `durable_submit` 必须先建立一个可由其他
process 独立发现和推进的 R1，`Accepted(run_id)` 只构造 response representation。

### Route return 后是谁继续工作

route return 后，它的 local call stack 和 variables 会结束；response object 被 framework
序列化并通过 server 发给 client，不会自行领取或执行任务。后台继续需要在 return
之前建立 durable handoff，常见形态包括：

```text
database queue: transaction 插入 R1=queued；worker poll/claim queued rows
outbox: transaction 插入 R1 与 E1；dispatcher 把 E1 发送到 broker
message broker: consumer 收到 durable message 后创建/领取 attempt
```

若 `durable_submit()` 只生成 random id 并 return，没有保存 queued work、发送 durable
message 或建立其他 handoff，则 response 虽是 202，route 结束后没有任何 actor 知道要做
R1。这是 false acceptance。相反，只要 R1 已 durable admission，原 API process 在
return 后退出或重启，worker 仍可通过 Database/queue 找到它。

最小 database-queue 时间线是：

```text
API transaction: INSERT R1 queued → COMMIT
API: return 202 + R1
Worker loop: SELECT/claim queued R1 → create A1 → execute
Browser later: GET R1
```

这里 `202` 与 execution 之间的桥不是 Python return value，而是 committed R1。若采用
outbox，则 R1 和 E1 应共同 commit；dispatcher/worker 的 duplicate delivery 再由 stable
event/run identity 与 conditional claim 处理。它延续了前课的原则：handoff side effect
要 durable，response 不是 work queue。

下一检验题（待回答）：下面的 route 返回了 202 和 R1，但 `durable_submit` 只运行
`return uuid4()`，既不写 Database，也不发送 message。HTTP response 能正常到达
Browser。它是否形成了真正的 asynchronous job？route return 后还有谁知道 R1 需要
执行？应把最小 durable handoff 放在哪里？

学习者随后用 `a→a1` 与前台继续处理 `b/c` 描述 asynchrony。模型接近 job-level
asynchrony，但需修正两处：API 必须先把 R1 durable commit，再返回 accepted identity，
不能先返回再尝试提交；Database 保存 work/state，通常由独立 Worker 执行。最终 a1
不是原 request 延迟恢复，而由前台通过新的 GET、notification 或 stream event，凭同一
R1 identity 取得。可压缩为：synchronous completion 的原 response 承载 final result；
asynchronous job 的原 response 承载 durable receipt R1，final result 在后续 interaction
中取得。前台能同时处理 b/c 是这种 lifetime decoupling 的效果，不是定义本身。

## 来源与验证边界

历史档案及其上述 primary sources 已在 2026-09-01 复核。FastAPI 官方文档同日
复核。当前只建立 framework-independent pipeline 和 responsibility boundary；
未创建可运行 FastAPI application，也未对 Bio Plot Platform 当前 route 作事实
声明。一次课堂回答不自动形成 FastAPI coding mastery。
