# 连续教学的有限观察协议

Date: 2026-09-07
Status: usable protocol; prospective synthetic teaching runs pending

## 适用结论

本层记录特定连续问答中的实际表现，不输出 strict scorecard 或总体可靠性。
[严格评估契约](README.md)的模型 digest、隔离、重复和 aggregate 要求不变。
结构校验通过只说明观察文件自洽，不证明模型执行了案例或教师讲得好。

## 执行一次定向试验

1. 从 [cases](continuity-observation-cases.yaml) 选一个与待判断行为相符的情境。
   保存本次材料文件及哈希、日期、可取得的模型/工具/运行信息。不可取得的
   标识写 null 并列明限制，不猜测模型快照或 reasoning setting。
2. 使用新的教学上下文，提供已批准的技能、该案例 context 与必需材料。
   逐条发送 turns，等待实际回答再发送下一条；不得一次把整段输入压成单轮。
   中断恢复情境在第二条输入前另开干净上下文，保留已写入的合成工作区。
3. 按整个轨迹审阅 criteria。只记录脱敏的可观察结果和精确来源位置；缺少
   下一轮时标为 not-observed。不要让试验者补写模拟的教师回答当作运行结果。
4. 判断直接答疑、前置解释、返回、改向和证据诚实；长度和耗时只是辅助信息。
   自审、独立内容审查、真实学习者反馈、合成运行必须明确区分。
5. 定向行为修改后先重跑该情境，再选相邻情境作回归；只有实际可比较的材料
   和运行条件才能讨论版本差异。一个案例通过不代表长期稳定或学习者掌握。

当前执行不调用额外代理或外部教师模型。用户已授权检查的真实教学轨迹可以
先作为 retrospective classroom observation，不能伪装成执行了上述合成案例。
后续课程自然出现对应情境时可以继续积累真实观察，不要求学习者逐轮评分。

## 保存与校验

观察文件位于本目录 `*-classroom-observation.yaml`；案例 criteria 的结果只能是
observed、concern 或 not-observed。前两者必须附具体观察依据，不能只是“通过”。
真实课堂回顾使用 `kind: retrospective-classroom-observation`；实际合成试验使用
`kind: synthetic-run`，需要真实 run locator 和 `materials.sha256` 中每个材料文件的
完整哈希。日期、运行环境、评审者、来源与限制字段沿用本目录观察示例；哈希
记录的是执行时的材料，不应在材料后续变化后重写。没有执行的案例也要保留为
not-observed。声明校验不证明 run locator、哈希和实际运行之间的对应关系。
批次检查命令：

```bash
python3 scripts/check-teaching-observations.py
```

当前记录明确保留未发生的返回与重启恢复为 not-observed；四个合成情境均未
运行。没有可靠原文定位时标明 partial。私人完整对话不写入此目录、不发送给
额外评估者。本层不修改 learning-state/sessions 或 reviewed capability。
