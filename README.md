# 智能助手 - HTTP API 和 Web 界面

## 代码结构

```
funcall/
├── app/
│   ├── agent.py      # Agent核心逻辑
│   ├── llm.py        # LLM配置
│   └── tools.py      # 工具定义
├── config.py         # 配置文件
├── main.py           # 命令行入口
├── index.html        # Web界面 ⭐
└── requirements.txt
```

## Web界面使用

`http://localhost:8001/index.html`



##  项目启动

> 前提条件，切换到项目根目录

1. 安装依赖

~~~bash
# python == 3.12
pip install -r requirements.txt
~~~

2. 配置环境变量

   见`config.py` 主要有AI_API_KEY

3. 启动脚本

~~~bash
python main.py
~~~

## 实现思路

对话 -> 决定是否工具调用->执行工具（将工具结果直接放入上下文继续判断后续判断是否调用工具）-> 回复结果



工具有两个

1. 天气查询工具，给定城市名称查询返回天气信息，API https://uapis.cn/api/v1/misc/weather 特点免费，无认证
2. 职业规划工具，给定兴趣，技能等生成规划内容直接返回（职业规划其实也可以直接在主Agent中直接生成规划完成，这里其实是使用工具目的时让主Agent收集信息，职业规划工具专门提示词做生成）

实现内容：

**AI：** 完成`main.py` 文件进行服务器搭建，`index.html`demo界面

**human:** `tool.py` 工具实现，`agent.py` 工具调用核心实现

## 示例

![](./img/1.jpg)
![](./img/2.jpg)
![](./img/3.jpg)
![](./img/4.jpg)
![](./img/5.jpg)
![](./img/6.jpg)
![](./img/7.jpg)



