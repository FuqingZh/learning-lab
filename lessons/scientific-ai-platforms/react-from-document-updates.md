# 从更新文档到理解 React

这次要连起来的不是一组 React 名词，而是一个问题：**数据变了以后，谁来
决定页面该显示什么，谁又负责把页面改成那个样子？**

我们的位置是：浏览器接收文档 → JavaScript 可以操作文档 → 数据持续变化时
怎样组织页面代码。TypeScript 可以帮助检查代码，但不是理解这一问题的
前置条件。这一课不用 TypeScript 标注，也不要求你已经理解 React 的写法。

## 先把已有的东西放到一起

你可以把 JavaScript 理解为我们在这里编写程序使用的语言。浏览器提供了
访问页面的对象和操作；DOM 是程序可以访问、修改的文档表示，不是原始 HTML
文本，也不是屏幕像素本身。修改这个表示之后，浏览器再负责后续显示。

假设页面需要显示一个报告的样本数量。先不碰页面，只计算一句话：

<!-- executable-example: summary -->
```js
const report = { sampleCount: 3 };

function summaryText(report) {
  const count = report.sampleCount;
  return "样本数：" + String(count);
}

const firstText = summaryText(report);
report.sampleCount = 5;
const secondText = summaryText(report);
```

这里的大括号把有名字的数据放在一起：`sampleCount` 是属性名，`3` 是它
当前保存的数值；`report.sampleCount` 就是读取这个属性。

`const report = ...` 声明名字并让它指向右边的对象。`const` 不允许之后把
这个名字重新绑定到另一个值，但不等于冻结对象，所以仍可修改它的属性。
`report.sampleCount = 5` 就是在把这个属性改为 5。

`summaryText` 是我们定义的函数。定义里的 `report` 是参数名，调用
`summaryText(report)` 时，外面的报告对象作为输入传进去。`String(count)`
把数量转成字符串，`+` 在这里连接文字，`return` 把结果交给调用者。

所以第一次得到“样本数：3”，第二次得到“样本数：5”。`firstText` 仍是第一
次计算得到的字符串，不会因为对象属性后来改变就自动变成另一句话。
截至这里，没有代码访问 DOM，也没有代码要求页面更新。

这不是把你已经答过的题重新考一次，而是让后面的例子只建立在这些明确的
操作上。若某一步陌生，可以在这里解释，不必另开一整套语法课。

## 一种已有做法：自己把计算结果写进页面

设 HTML 里有 `<p id="summary"></p>`。`p` 是一段文字的元素，`id` 给它一个
查找标记。下列两行假设上面的 `report` 和 `summaryText` 已经存在：

```js
const node = document.querySelector("#summary");
node.textContent = summaryText(report);
```

`document` 是浏览器提供的文档对象；调用 `querySelector` 找到对应元素。
`#summary` 指定按这个 id 查找；`node` 保存找到的 DOM element reference。
这里假设元素存在，不是对任意页面都能成功的保证。

第二行右边先计算文字，再通过 `textContent` 把它写进文档。这个赋值与前面
仅仅生成字符串不同，它改变了程序之外的文档状态。写入的是文本，不把它
当作 HTML 标签解析。[textContent 的行为](https://developer.mozilla.org/en-US/docs/Web/API/Node/textContent)

页面很小时，这种做法完全可以使用。但之后每次数据变化，程序都需要安排
相应更新。问题不在于 JavaScript 不会计算，而在于我们需要组织**数据与
页面之间持续存在的关系**。代码可以自己封装这些操作，并不是只有 React
才能解决；也不能仅凭使用 React 就断言更快或更正确。

本课的[独立 HTML 示例](react-from-document-updates.html)不需要安装依赖，
可在浏览器打开。它先写入数量 3，再写入数量 5，最终显示“样本数：5”。
浏览器不保证把两个紧接着的写入分别画出两帧；观察最终结果即可。

## React 出现时，项目方怎样说明这个问题

2013 年 6 月 5 日，Pete Hunt 在 React 项目文章中介绍了用可复用的界面
组成部分呈现变化的数据，并说明先产生界面描述、再据变化更新 DOM 的做法。
这证明的是当时项目方公开说明的方案，不证明 React 首创了这种思想，也
不能直接当成所有现代 API 的说明。
[历史原文](https://legacy.reactjs.org/blog/2013/06/05/why-react.html)
与[已建历史档案](../../histories/web-programming-history.md)分别提供来源与边界。

## 先区分“语言”和“提供现成能力的代码”

前面的 `summaryText` 是我们自己写的 JavaScript 函数。其他人也可以把一组
可复用能力写好，供我们的程序使用；这样的代码集合称为 library。
它不因此变成另一门语言。React 是用于构建用户界面的 JavaScript library。

要使用 library，需要先把它提供的代码接入程序。模块加载和项目安装是
后面的具体操作。本课先说明调用的含义；不把省略接入过程的代码冒充可以
直接粘贴运行的完整程序。

React 的一个关键区别是：我们可以产生“这一块界面应该是什么样”的描述，
再交给负责浏览器文档更新的 React DOM。**描述不是实际 DOM，生成描述本身
也不是已经修改了屏幕。**

## 把刚才的数量放进界面描述

下面是 API 对照片段，假设 `React` 已由环境提供，`report` 与 `summaryText`
沿用上面的定义。它不作为本课免安装 HTML 的一部分执行：

```js
const description = React.createElement("p", null, summaryText(report));
```

`React` 在这里是提供相关函数的对象。点号取出它的 `createElement` 函数；
圆括号仍然是普通 JavaScript 函数调用。三个参数在这个例子里分别表示：

- `"p"`：要描述一段文字元素；
- `null`：这里不另外提供属性；`null` 是 JavaScript 的一个值，不是变量名；
- `summaryText(report)`：这一段应包含的文字。

调用得到 React element，也就是供 React 使用的描述对象，而不是 DOM
element。不要自己改它的内部字段来控制页面。
[当前 createElement 文档](https://react.dev/reference/react/createElement)

假设页面里另有 `<div id="root"></div>` 作为展示区域，且 `ReactDOMClient`
已由环境提供，接入它的示意是：

```js
const container = document.querySelector("#root");
const root = ReactDOMClient.createRoot(container);
root.render(description);
```

先找到 DOM 展示区域，`createRoot` 为这一块区域建立由 React DOM 管理的
入口，`root.render` 把描述交给它显示。它并不表示浏览器里的全部页面都
必须交给 React 管理。[当前 createRoot 文档](https://react.dev/reference/react-dom/client/createRoot)

如果我们后来只写 `report.sampleCount = 8`，这个普通对象的赋值本身不会
自动通知 React。在这个手动演示里，需要重新生成描述并再次交给入口。
应用通常怎样触发更新，会在后续交互单元中讲。本课不提前要求你理解那套
机制，也不把“使用 React”说成“任意变量变化都会自动更新页面”。

## 那么 JSX 和 component 放在哪里

当界面描述需要多次复用时，React 可以调用我们编写的函数来产生描述；
这种组织界面代码的单位称为 component。知道它承担什么角色即可，本课
暂不引入参数解构、hooks 或 component 调用规则。

JSX 则是一种用于表达界面的语法形式，经工具处理后供程序使用。它不是
React 本身。本课用了普通函数调用来展示同一类描述能力，所以理解 React
是什么，不需要先解开 JSX 的全部语法。

这一段的作用是安放你会遇到的名称，不是宣布你已经学会写 component。
后续用有背景的完整例子学习它们，不在这里继续展开一条术语链。

## 回到原问题

我们没有消除文档更新，而是改变了职责分工：先计算想显示的内容，再产生
界面描述，由 React DOM 管理对应区域的文档更新。JavaScript 仍负责执行
程序，浏览器仍负责显示。没有使用 React 时，自己的代码也能组织更新。

这个模型并不能证明报告的数据或科学结论正确。它解释的是界面的组织
方式；科学数据的可信性仍需要另外的证据。

真正进入 Bio Plot Platform 时，可以带着这个问题检查一个页面：哪部分
数据决定展示内容，哪里产生描述，哪里连接外部操作。本课没有重新核对
该仓库的当前实现，因此不把某个组件或路径作为事实展示。

## 自然节点的应用（可在试学时使用）

换成显示“文件名”的页面：先一起把数量示例改成文件名示例，明确输入与
输出；之后再由你解释，当文件名变化时，哪些操作只是计算，哪些操作才
请求改变页面，以及更换展示 library 会不会把程序换成另一门语言。

这个任务用于观察解释和迁移，不考 API 拼写。如果尚未准备好，可以继续
澄清或暂停；不因为未作答就登记失败，也不因为读完本课就登记掌握。

## Teacher preparation and acceptance

本段供 tutor 备课，不需在课堂逐项朗读。

- Outcome：区分语言、library、界面描述与实际文档更新，能在新展示案例
  中解释职责；不是“已经掌握 React 开发”。
- Starting evidence：当前对话曾涉及函数、对象和 DOM，但未在本次实施中
  独立复测；不能由 `program` 的 session 标签推断语法流利。开头提供桥梁。
- Dependencies：对象属性、函数参数、调用、字符串连接、DOM 查找和写入均
  在首次关键使用处说明；library、null、createElement、createRoot 同样铺垫。
- Deferred：安装与模块加载、JSX 写法、参数解构、hooks、事件和更新触发。
  API 片段明确不是独立可运行程序。只有纯 JS 与 HTML 示例参加本地执行检查。
- History：读取现有档案与 2013 原文；不新增历史优先权或动机推断，不把
  2013 的实现描述泛化成现代内部实现保证。
- Checks：结构测试、示例输出与未变更旧事件可以机械检查；讲解是否适合
  学习者需要实际试学。React runtime/浏览器绘制尚不由 Node 示例测试证明。
- Next：先让学习者选择澄清或独立应用，再进入一个有明确输入的 component
  例子；不得直接恢复旧的 typed-props 起点。
- Status：prepared, not taught or mastered. Content review is separate from
  real learner evidence.
