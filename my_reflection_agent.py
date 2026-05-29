DEFAULT_PROMPTS = {
    "initial":"""
请根据以下需求完成任务:

任务：{task}

请提供一个完整、准确的回答。
""",

    "reflect": """
请仔细审查以下回答，并找出可能的问题或改进空间

# 原始任务:
{task}

# 当前回答:
{content}

情分析这个回答的质量，指出不足之处，并提出具体的修改建议。
如果已经回答得很好，请回答“无需改进”。
""",

    "refine":"""
请根据反馈意见改进你的回答：
# 原始任务:
{task}

# 上一轮回答:
{last_attempt}

# 反馈意见:
{feedback}

请提供一个改进后的回答
""",

}

import re
from typing import Optional, List, Tuple, Dict
from hello_agents import ReflectionAgent, HelloAgentsLLM, Config, Message, ToolRegistry

class MyReflectionAgent(ReflectionAgent):
    """
    重写的Reflection Agent - 推理与反思的智能体
    """

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        max_iterations: int = 5,
        custom_prompt: Optional[Dict[str, str]] = None
    ):
        super().__init__(name, llm, system_prompt, config)
        self.max_iterations = max_iterations

        # 设置提示词模板：用户自定义优先，否则使用默认模板
        self.prompt = custom_prompt if custom_prompt else DEFAULT_PROMPTS
        print(f"✅ {name} 初始化完成，最大迭代次数: {max_iterations}")

    def run(self, input_text: str, **kwargs) -> str:
        """运行 ReflectAgent"""
        print(f"\n🤖 {self.name} 开始处理任务: {input_text}")
        # ========== 1. 初始执行 ==========
        print("\n--- 正在进行初始尝试 ---")
        initial_prompt = self.prompt["initial"].format(task=input_text)
        messages = [{"role": "user","content": initial_prompt}]
        current = self.llm.invoke(messages, **kwargs)
        print("📝 初始回答已生成")

        for i in range(self.max_iterations):
            print(f"\n--- 第 {i+1}/{self.max_iterations} 轮迭代 ---")

            #a. 反思：让LLM评审当前回答
            print("-> 正在进行反思...")
            reflect_prompt = self.prompt["reflect"].format(
                task = input_text,
                content = current
            )
            feedback = self.llm.invoke([{"role": "user", "content": reflect_prompt}], **kwargs)
            print(f"💭 反思反馈: {feedback[:80]}...")

            #b. 检查收敛：如果反馈说“无需改进”，提前结束
            if "无需改进" in feedback :
                print("✅ 反思认为已无需改进，提前结束迭代。")
                break

            # c. 优化：根据反馈生成新版本
            print("-> 正在进行优化...")
            refine_prompt = self.prompt["refine"].format(
                task = input_text,
                last_attempt = current, #上一轮内容
                feedback = feedback #反思给出的反馈
            )
            current = self.llm.invoke([{"role":"user","content": refine_prompt}], **kwargs)
            print("优化后的回答已生成")

        # ========== 3. 保存到框架历史并返回 ==========
        print(f"\n🎉 任务完成")
        self.add_message(Message(input_text,"user"))
        self.add_message(Message(current,"assistant"))
        return current