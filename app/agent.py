from openai import OpenAI
from typing import List, Dict, Any, Optional
from .llm import default_llm
from .tools import WeatherTool, CareerPlannerTool
from config import SYSTEM_PROMPT,AI_MODEL
import logging

logger = logging.getLogger("【Agent】")


class Agent:
    def __init__(self, llm: Optional[OpenAI] = None):
        if llm is None:
            llm = default_llm
        self.llm = llm
        self.messages = []
        self.tools = []
        self._register_tools()

    def _register_tools(self):
        """注册所有可用的工具"""
        weather_tool = WeatherTool()
        career_planner_tool = CareerPlannerTool(llm=self.llm)

        self.tools = [
            weather_tool.get_tool_dict(),
            career_planner_tool.get_tool_dict(),
        ]
        self.tool_instances = {
            weather_tool.name: weather_tool,
            career_planner_tool.name: career_planner_tool,
        }

    def add_message(self, role: str, content: str):
        """添加消息到对话历史"""
        self.messages.append({"role": role, "content": content})

    def clear_messages(self):
        """清空对话历史"""
        self.messages = []

    def _call_tool(self, tool_name: str, arguments: dict) -> str:
        """调用指定的工具"""
        try:
            tool = self.tool_instances.get(tool_name)
            final = False
            if not tool:
                return f"未找到工具: {tool_name}"
            res = tool.run(**arguments)
            if tool_name == "career_planner":
                final = True
            return {
                "final":final,
                "result":res
            }
            # if tool_name == "weather":
            #     return tool.run(city=arguments.get("city"))
            # elif tool_name == "career_planner":
            #     return tool.run(
            #         skill=arguments.get("skill"),
            #         interest=arguments.get("interest"),
            #         goal=arguments.get("goal"),
            #         other_info=arguments.get("other_info")
            #     )
        except Exception as e:
            logger.error(f"调用工具 {tool_name} 时出错: {e}")
            return {"final":final, "result":f"工具执行出错: {str(e)}"}

    def chat_stream(self, user_input: str):
        """流式对话"""

        self.add_message("user", user_input)

        while True:
            messages_with_system = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ] + self.messages

            try:
                response = self.llm.chat.completions.create(
                    model=AI_MODEL,
                    messages=messages_with_system,
                    tools=self.tools,
                    stream=True,
                )

                full_response = ""
                tool_calls = []

                for chunk in response:
                    if not chunk.choices:
                        continue

                    delta = chunk.choices[0].delta

                    # 普通文本
                    if delta.content:
                        full_response += delta.content
                        yield delta.content

                    # 工具调用（流式拼接）
                    if delta.tool_calls:
                        for tool_call in delta.tool_calls:
                            idx = tool_call.index

                            if len(tool_calls) <= idx:
                                tool_calls.append({
                                    "id": tool_call.id or "",
                                    "type": tool_call.type or "function",
                                    "function": {
                                        "name": tool_call.function.name or "",
                                        "arguments": tool_call.function.arguments or ""
                                    }
                                })
                            else:
                                tc = tool_calls[idx]

                                if tool_call.function.name:
                                    tc["function"]["name"] = tool_call.function.name

                                if tool_call.function.arguments:
                                    tc["function"]["arguments"] += tool_call.function.arguments

                assistant_msg = {
                    "role": "assistant",
                    "content": full_response if full_response else None
                }

                if tool_calls:
                    assistant_msg["tool_calls"] = tool_calls

                self.messages.append(assistant_msg)

                # 没调用工具直接返回
                if not tool_calls:
                    break

                yield "\n\n"  


                # 模型返回的工具 一个个调用
                final = False
                for tool_call in tool_calls:
                    tool_name = tool_call["function"]["name"]

                    try:
                        arguments = eval(tool_call["function"]["arguments"] or "{}")
                    except:
                        arguments = {}

                    logger.info(f"调用工具: {tool_name}, 参数: {arguments}")


                    # 正真的调用工具
                    # yield  "********************\n"+f"【调用工具】 {tool_name} 参数: {arguments} \n"+ "********************\n\n"
                    call_result = self._call_tool(tool_name, arguments)
                    tool_result = call_result.get("result")
                    logger.info(f"工具结果：{tool_name},结果:{tool_result}")
                    # yield "********************\n"+f"工具结果：{tool_name},结果:{tool_result}\n"+"********************\n\n"

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"], 
                        "content": tool_result
                    })
                    if call_result.get("final",False):
                        yield tool_result
                        final = True
                        break
                    
                
                if final:
                    break

            except Exception as e:
                logger.error(f"对话出错: {e}")
                yield f"抱歉，处理出错: {str(e)}"
                break


