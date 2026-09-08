# 样本浏览器：完整功能练习

目标：看懂并修改“选择样本 → 查看详情 → 清除选择”这个完整功能。
先看运行效果，再读 `app.jsx`，不要求背诵组件调用链。

本练习属于[从更新文档到理解 React](../react-from-document-updates.md)的
“当前单元主线”，不是另起一条 React API 课程。选择、高亮与详情用来说明
界面如何随数据保持一致；`useState` 是函数组件使用 state 的现代例子。
历史位置、来源与语法答疑后的返回点由父课统一维护。完成或澄清一处写法后，
先回看父课的未完问题，再决定是否需要新的操作练习。

## 运行

本工作区已安装根目录的 esbuild 与 `frontend/spike/node_modules` 中的
React / React DOM；构建复用这些依赖，不安装包、不修改 lockfile。

```bash
node lessons/scientific-ai-platforms/sample-viewer/build.mjs
node lessons/scientific-ai-platforms/sample-viewer/check.mjs
```

浏览器打开 `.build/react-sample-viewer/index.html` 即可交互，不依赖 CDN。
其他 checkout 若未安装上述依赖，构建会失败；本练习不自动安装它们。

先观察：未选择 → A 的详情 → B 的详情 → 清除后回到提示。
再完成小改动：让页面初次打开时默认选中 B，但点击清除后仍回到未选择。
允许查阅源码和文档；操作结果与解释共同作为观察，不把读过代码记为掌握。

## 备课边界

- 起点：已讲过 JSX、props、useState 和事件处理；近期口述存在共享状态与
  更新入口的混淆，不能据此推断已经能独立实现。
- 本例显式写两个按钮，暂不加入数组遍历、解构 props、请求、Effects 或数据库。
- 新语法按需解释：`if` 选择输出；`===` / `!==` 作严格相等/不等比较；
  `samples[selectedSampleId]` 按 ID 查对象里的数据；`null` 表示未选择。
- 完整示例使用局部界面 state；虚构样本不是科研结论，刷新不保留选择。
- 浏览器检查设计覆盖初始、选择 A、切换 B、重复选择、清除、再次选择与刷新。
  不证明生产适用性、科学性、学习掌握或完整可访问性。
- 后续由实际操作/修改推进到新的需求，不再逐个组件名称追问。

验证记录（2026-08-31）：构建成功。自动交互检查未完成：当前 Chrome 启动
遇到 `/tmp/Crashpad/new: Permission denied`，没有获得页面行为断言结果。
检查支持 `CHROME` 环境变量指定浏览器；本次没有修改主机权限或安装依赖。
启动失败时保留独立临时 profile 供诊断，不将环境失败记为测试通过。

交付复验（2026-09-08）：构建及全部交互断言通过，包含初始状态、A/B 切换、
重复选择、清除、重新选择、刷新与错误显示负例。默认启动仍复现旧环境问题；
当前主机的浏览器包装脚本会追加参数，干扰指定 profile。此次通过 `CHROME`
选择实际浏览器可执行文件，并给 TMPDIR、XDG_CONFIG_HOME、XDG_CACHE_HOME 设置
独立临时目录完成检查；没有修改主机包装脚本或权限。其他主机需按实际安装
指定可执行文件，不把本次结果解释为默认包装脚本已修好。

来源（React 官方文档，核对于 2026-08-31）：
[Sharing State](https://react.dev/learn/sharing-state-between-components)、
[Conditional Rendering](https://react.dev/learn/conditional-rendering)。
