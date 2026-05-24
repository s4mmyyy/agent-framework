from typing import Optional, Iterator
from hello_agents import SimpleAgent, HelloAgentsLLM, Message, Config
import re


class MySimpleAgent(SimpleAgent):
    """
    重写的简单对话Agent
    展示如何基于框架基类构建自定义Agent
    """

    def __init__(
            self,
            name: str,
            llm: HelloAgentsLLM,
            system_prompt: Optional[str] = None,
            config: Optional[Config] = None,
            tool_registry: Optional['ToolRegistry'] = None,
            enable_tool_calling: bool = True
    ):
        
        super().__init__(name, llm, system_prompt,config)
        self.tool_registry = tool_registry
        self.enable_tool_calling = enable_tool_calling and tool_registry is not None
        print(f"✅ {name} 初始化完成，工具调用: {'启用' if self.enable_tool_calling else '禁用'}")
    
    def run(self, input_text: str, max_tool_interations: int =3, **kwargs) -> str:
        """
        重写的运行方法 - 实现简单对话逻辑，支持可选工具调用
        """

        print(f"🤖 {self.name} 正在处理: {input_text}")

        #构建消息列表

        messages = []

        #添加系统消息（可能包含信息工具）
        enhanced_system_prompt = self._get_enchanced_system_prompt()
        messages.append({"role": "system", "content": enhanced_system_prompt})
    

        #添加历史信息
        for msg in self._history:
            messages.append({"role": msg.role, "content":msg.scontent})
        
        #添加当前用户消息
        messages.append({"role": "user", "content":input_text})

        #如果没有启用工具调用，使用简单对话逻辑
        if not self.enable_tool_calling:
            response = self.llm.invoke(messages, **kwargs)
            self.add_message(Message(input_text, "user"))
            self.add_message(Message(response, "assistant"))
            print(f"✅ {self.name} 响应完成")
            return response

