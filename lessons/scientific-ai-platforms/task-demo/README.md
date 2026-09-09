# 可运行任务实验

用一份演示报告观察：提交响应、持久化记录、Worker 执行和页面查询分别发生在哪里。
这是 HTTP 主课的本地脚手架；后续回到 React、FastAPI 和 PostgreSQL。

需要 Python 3.10+，且其 SQLite 为 3.35+。无需安装 Python 包。
在仓库根目录打开两个终端，分别运行：

```bash
python3 lessons/scientific-ai-platforms/task-demo/lab.py api
```

```bash
python3 lessons/scientific-ai-platforms/task-demo/lab.py worker
```

浏览器打开 <http://127.0.0.1:8765>。默认数据库位于被 Git 忽略的
`.build/task-demo/jobs.sqlite`；两个进程必须使用同一数据库路径。

## 观察顺序

1. 先只启动 API，点击提交。任务停在 `queued`；保存任务不会自动启动执行者。
2. 启动 Worker。任务变为 `running`，约 8 秒后生成演示文本，变为 `succeeded`。
3. 开始新操作并提交，随后暂停查询。页面停止更新；等待十秒再继续查询，可看到后台结果。
4. 新任务进入 `running` 后，在 Worker 终端按 Ctrl+C。重新启动 Worker，等旧租约到期后会接手，`generation` 增加。此实验重新执行整个计算，不从计算中途恢复。
5. 刷新页面，浏览器从本地存储恢复任务编号。重复提交同一操作仍返回同一任务；改变内容须先开始新操作。

页面每次查询最多等 5 秒，结束后间隔 3 秒再查；连续 3 次查询失败暂停自动查询。
成功查询重置计数，服务端任务进入终态则停止查询。这里 4xx 查询响应不自动重试，
适用于本实验的接口；不是所有系统的通用分类。提交失败保留操作编号，由按钮手动重试。
暂停查询、网络中断、点击开始新操作都不会取消已经保存的任务。

## 阅读代码

先看 `lab.py` 的 `submit`：事务提交后才回复编号。
再看 `claim` 和 `worker`：独立进程领取、续期、计算和保存结果。
最后看 `index.html` 的 `query`：只读取任务，查询错误不会改写后台任务状态。

SQLite 的写事务在本机串行化领取操作。结果是同库保存的短文本，不是真实 PDF、
AI 绘图或外部文件；因此这里没有证明外部存储与数据库的原子提交。
只使用单机时钟，未实现认证、多租户、任务取消、计算异常分类或执行次数上限。
只绑定本机回环地址，不能直接当作生产服务。实验也不证明 PostgreSQL 的并发语义。

## 验证

```bash
python3 lessons/scientific-ai-platforms/task-demo/check.py
```

验证实际 HTTP 提交与冲突、API 重启后的任务持久化、Worker 进程中断与接手、
旧代次完成被拒绝，以及两个进程竞争领取。使用临时数据库并清理测试进程。
浏览器交互另行验证；这些测试通过不构成学习者独立掌握的证据。

已安装仓库 Node 依赖及 Chrome 时，可运行浏览器检查：

```bash
node lessons/scientific-ai-platforms/task-demo/check-browser.mjs
```

它验证提交、暂停后后台完成、继续查询、刷新恢复编号，以及连续查询失败后的暂停。
若本机 Chrome 包装器或共享临时目录不可用，可用 `CHROME` 指向 Chrome 可执行文件，
并将 `TMPDIR`、`XDG_CONFIG_HOME`、`XDG_CACHE_HOME` 指向本次独立的临时目录。
