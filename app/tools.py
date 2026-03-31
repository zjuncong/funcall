from abc import ABC, abstractmethod
from config import WEATHER_API_URL,AI_MODEL
import logging
import requests
from logging import getLogger
from openai import OpenAI
from .llm import default_llm
logging.basicConfig(level=logging.INFO)
logger = getLogger("【tools】")

class BaseTool(ABC):
    """
        工具调用的基类，定义了工具的基本属性和方法，
        以及获取工具参数的JSON Schema的方法。
        需要手动实现run方法 和 _get_dict_schema方法。
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def run(self, arguments: dict) -> str:
        """
        执行工具操作
        """
    
    def get_tool_dict(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self._get_dict_schema()
            }
        }
    
    @abstractmethod
    def _get_dict_schema(self, arguments: dict) -> dict:
        """
        获取工具参数的JSON Schema
        """



class WeatherTool(BaseTool):
    def __init__(self):
        super().__init__("weather", "获取指定城市的天气信息，当需要获取某一个城市天气信息时可调用我")
    
    def run(self, city: str) -> str:
        """
        执行工具操作
        """
        response = requests.get(WEATHER_API_URL, params={"city": city})
        if response.status_code == 200:
            return self._parse_weather(response.json())
        else:
            return f"获取天气信息失败，状态码：{response.status_code}"
    
    def _parse_weather(self, weather_data: dict) -> str:
        """
        解析天气数据，返回格式化字符串
        """
        # print(weather_data)
        try:
            return f"""
            省份:{weather_data.get("province","-")}
            城市：{weather_data.get("city","-")}
            天气：{weather_data.get("weather","-")}
            温度：{weather_data.get("temperature","-")}℃
            湿度：{weather_data.get("humidity","-")}%
            风力：{weather_data.get("wind_power","-")}
            报告时间:{weather_data.get("report_time","-")}
            """
        except Exception as e :
            logger.info(f"解析天气出错=>:{e}")
            return "解析天气信息出错"
    def _get_dict_schema(self) -> dict:
        """
        获取工具参数的JSON Schema
        """
        return {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "要查询的城市的名称"
                }
            },
            "required": ["city"]
        }


class CareerPlannerTool(BaseTool): 

    system_prompt = """\
你是一名专业的职业规划顾问（Career Advisor Agent），擅长根据用户的技能、兴趣和职业目标，提供清晰、可执行的职业发展建议。

你的任务是生成一份结构化的职业规划报告，要求：

【分析原则】
1. 结合用户的技能、兴趣和目标进行综合分析，而不是孤立判断
2. 优先推荐匹配度高、可实现性强的职业方向
3. 避免空泛建议，强调可执行性
4. 如果信息不足，可做合理假设，但需保持谨慎

【输出要求】
请输出一份结构清晰的职业规划报告，包含以下内容：

1. 职业方向建议（2-4个）
   - 每个方向需说明：
     - 为什么适合（结合技能+兴趣+目标）
     - 发展前景（简要说明）

2. 核心能力差距分析
   - 用户当前技能 vs 目标职业要求
   - 存在的关键差距

3. 关键技能提升建议
   - 必备技能（必须掌握）
   - 加分技能（提升竞争力）
   - 每个技能给出简要说明

4. 行动计划（分阶段）
   - 短期（0-3个月）
   - 中期（3-12个月）
   - 长期（1年以上）

【风格要求】
- 专业但易读
- 条理清晰，使用小标题和列表
- 避免冗长废话
- 不要输出无关内容

只输出最终报告，不要解释你的思考过程。
"""
    user_prompt_template = """\
请根据以下用户信息生成职业规划报告：

【技能】
{skills}

【兴趣】
{interests}

【职业目标】
{goals}

【其他信息】
{other_info}
"""


    def __init__(self,llm:OpenAI=None):
        super().__init__("career_planner", "根据用户输入的个人信息，规划用户的职业道路。确保已经有用户的兴趣、技能和职业⽬标。缺一不可")
        if llm is None:
            llm = default_llm
        self.llm = llm
    def run(self, skill: str, interest: str, goal: str,other_info: str = None) -> str:
        """
        执行工具操作
        """
        
        prompt = self.user_prompt_template.format(
            skills=skill,
            interests=interest,
            goals=goal,
            other_info=other_info,
        )
        response = self.llm.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()
    
    def _get_dict_schema(self) -> dict:
        """
        获取工具参数的JSON Schema
        """
        return {
            "type": "object",
            "properties": {
                "skill": {
                    "type": "string",
                    "description": "用户目前已有的技能"
                },
                "interest": {
                    "type": "string",
                    "description": "用户的兴趣"
                },
                "goal": {
                    "type": "string",
                    "description": "用户的职业⽬标"
                },
                "other_info": {
                    "type": "string",
                    "description": "用户的其他信息"
                }
            },
            "required": ["skill", "interest", "goal"]
        }

if __name__ == "__main__":
    weather_tool = WeatherTool()

    print(weather_tool.run("北京"))
    print(weather_tool.get_tool_dict())
