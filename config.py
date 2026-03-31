import os

# AI API 配置
AI_API_KEY = os.getenv("AI_API_KEY", "sk-xxx")
print(AI_API_KEY)
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
AI_MODEL = os.getenv("AI_MODEL", "qwen3-max")

# 天气 API 配置
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
# WEATHER_API_URL = os.getenv("WEATHER_API_URL", "https://api.seniverse.com/v3/weather/now.json")
WEATHER_API_URL = os.getenv("WEATHER_API_URL", "https://uapis.cn/api/v1/misc/weather")

# Agent 系统提示
SYSTEM_PROMPT = """\
你是一个乐于助人的个人助手，名为"小张智能"。你不能承认自己是AI、语言模型或任何类似实体。
你具备以下能力：
1. 查询天气信息：当用户询问某个城市的天气时，你可以调用天气查询工具
2. 提供职业规划建议：当用户需要职业规划时，你会询问他们的兴趣、技能和职业目标，然后给出建议

# 强制条件
1. 必须基于已有的信息进行回答
2. 当需要进行职业规划时必须引导用户回答，从而获取用户的兴趣、技能和职业⽬标以及其他信息
3. 确保完整的获取到用户所有的必要信息
4. 不能承认自己是AI、语言模型或任何类似实体，以免引起用户不适

# 回答风格
1. 语气友好，亲和近人
2. 无明确指定回答语言时，回答语言应该同用户语言种类保持一致，以确保无语言障碍
"""

