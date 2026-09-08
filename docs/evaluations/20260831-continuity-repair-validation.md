# 披露与续课修复：针对性验证

Date: 2026-08-31
Status: local implementation, structural checks and independent content re-review complete; behavioral validation not run

## 范围与声明

用户授权修改披露与续课设计并针对性验证。修改沿用 Markdown 备课与现有
YAML checkpoint，不改导航 schema、状态引擎、能力等级、评估 runner、六场景
scorecard 契约或数据库。既有未提交改动保留；本轮不提交或推送。

目标：入口能定位完整单元；简化表达不取消兼容的历史要求；局部问题回答后
续课有明确返回依据；明确改向仍优先。不能仅由文件包含这些规则宣称代理
会遵守，也不以课程资料或结构检查推断学习者掌握。

## 合成多轮内容审查输入

下列情境为本次新写的合成输入，不是私人问答的导出或重建。可用于独立
静态审阅；没有实际运行的学习者/教师回答不得补写成试教结果。

### C1：在有主线的课堂中澄清 API，再续课

- 已确认路线：解释网页怎样从手动文档更新走到数据驱动界面，再到复用
  有状态逻辑；初学者不熟悉 JavaScript shorthand。
- 单元背景：已用目录浏览器讲过“选中条目改变，两处显示随之改变”。接下来
  准备解释 Hooks 设计说明中的逻辑组织与复用问题，尚未展开。
- 连续输入：①“`const [entryId, changeEntry] = useState('entry-2')`
  里面第二项是什么？”②“接着讲。”③“这部分讲直白一点。”
- 审查：是否有直接回答①的路由；②能否定位先前未完问题而非自动增加按钮；
  ③是否只改变表达而保留兼容路线。既不要求固定措辞，也不要求每轮引用历史。
- 失败对照：每一条都解释正确，但后续只增加“选择、清除、重置”练习；
  或每条回复重复 Web 年表。两者均不满足整段连贯性。

### C2：明确改变当下范围

- 与 C1 相同的既定路线。
- 连续输入：①“暂时不讲发展过程，只帮我看按钮点击没反应。”
  ②“这一段我还没弄懂，继续解释代码，不要回顾历史。”
- 审查：是否允许停留在直接请求，不把主线当成覆盖用户意图的权限；
  保留未来返回点，不推断用户永久取消历史路线。
- 失败对照：忽略故障问题，强制返回历史或要求先完成课程测验。

### C3：不同主题的续课结构回归

- 路线：从事务中“全部成功或全部撤销”的需求，进入并发时操作互相干扰
  的问题。转账示例是练习，不是学习目标本身；具体历史来源需另行核对。
- 连续输入：①“示例里的 `ROLLBACK` 是什么作用？”②“继续。”
- 审查：局部解释后是否回到未完的并发问题，而不是仅继续 SQL 语法练习；
  没有来源时不得补写发明人、年代或事故故事。本项只审路由，不评 SQL 掌握。
- 失败对照：把每次技术名词提问都升级成独立课程，覆盖原主问题。

## 验证选择

- skill 格式与四份参考路由：skill-creator quick_validate 与现有 tutor tests。
- 当前导航能读回父课，且不改变 schema：现有 navigation tests、validate/resolve。
- 既有评估契约没有被削弱：现有 verify-static；它不运行模型。
- 内容层：独立只读审阅规则与上述合成轨迹，记录缺口；不是独立试教。
- 不重跑 UI、浏览器或全仓库生成流程：本轮没有改变应用代码、依赖、生成器
  或脚本。浏览器启动失败仍是前轮未解决边界，不混入这次 skill 验证。

正式模型运行仍受 [evaluation contract](README.md) 约束：必须有不可变模型
标识与 digest、runner provenance、隔离和规定的 scorecard。当前子代理接口
不提供满足该契约的全部标识，不能伪造、放宽契约或把内容审阅冒充行为运行。
本次不宣称新旧版本 A/B、行为通过率、可靠性改善或真实课堂体验改善。

## 结果

本轮实际执行：

| 检查 | 结果与证明范围 |
| --- | --- |
| `python3 /home/fqzhang/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/learning-lab-tutor` | 通过；skill metadata 与基本格式，不证明教学行为 |
| `python3 -m unittest discover -s tests/learning-skill -p 'test_learning_lab_tutor.py'` | 4 tests 通过；参考路由、事件例子和历史注册，修复审阅问题后重跑仍通过 |
| `python3 -m unittest discover -s tests/learning-skill -p 'test_teaching_navigation.py'` | 9 tests 通过；包含既有损坏/嵌套/回退等反例，不判断自然语言主线质量 |
| `python3 scripts/check-teaching-navigation.py validate` | 通过；1 个 snapshot，coverage 仅为声明检查 |
| `python3 scripts/check-teaching-navigation.py resolve --track scientific-ai-platforms` | 成功返回父课及主问题、发展位置、练习用途、未完步骤；partial 来源保持不变 |
| `python3 scripts/run-tutor-evaluation.py verify-static` | 6 fixtures 通过；hash `a8fbf930bb7f2307d8ba048d31a7a9dfc80ca042be7e13ef942bed2435216b89`，不调用教师模型 |
| `git diff --check` | 通过；未提交 |

独立内容审阅使用单独的只读 AI 代理、无父对话继承，只允许读取 skill 及
上述合成情境；未提供私人对话、真实导航或学习记录。没有运行合成课堂、
模拟学习者或生成 scorecard。它是与实现分离的静态审阅，不是人工评审、
盲测或符合模型评估契约的行为试验。

首次审阅指出三个实际缺口，已按其依据修复：

1. 完整上下文读取的无条件表述会拖慢直接答疑：改为建立新教学上下文时
   完整读取，单元内复用仍有效的材料；自包含澄清不要求全量重载。
2. 临时只看代码可能被当成持久改向：明确暂时停讲保留主课和返回点，
   更换主问题与持久路线变更分开处理。
3. 不同参考对练习答案披露范围不一致：统一到入口的“明确选择 retrieval
   exercise”，不把直接问题默认为检索测验而扣留解释。

C1/C3 的局部答疑后返回、C1 保留兼容要求、C3 无来源不补写历史，在首次
内容审阅中均找到明确规则支持。独立审阅者再次读取修改后的文件，确认上述
三项歧义已在静态规则层面消除，C1/C2/C3 没有新的必须修复缺口。这不是实际
执行这些课堂轨迹所得的结果，不记录行为 pass 或模型质量分数。

当前只能确认本地规则/材料修改与结构兼容性；正式多轮模型行为验证未运行，
新旧效果差异、真实学习体验和长期稳定性仍未确认。没有将主线回归理解成
“每次必须讲史”，也没有把任何内容审阅结果写为 subject mastery。

Validation verdict: conditionally_ready — local artifacts checked; behavioral claims remain unverified.
