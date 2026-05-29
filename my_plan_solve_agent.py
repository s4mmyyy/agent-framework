# 默认规划器提示词模板
DEFAULT_PLANNER_PROMPT = """
你是一个顶级的AI规划专家。你的任务是将用户提出的复杂问题分解成一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是一个独立的、可执行的子任务，并且严格按照逻辑顺序排列。
你的输出必须是一个Python列表，其中每个元素都是一个描述子任务的字符串。

问题: {question}

请严格按照以下格式输出你的计划:
```python
["步骤1", "步骤2", "步骤3", ...]
```
"""

# 默认执行器提示词模板
DEFAULT_EXECUTOR_PROMPT = """
你是一位顶级的AI执行专家。你的任务是严格按照给定的计划，一步步地解决问题。
你将收到原始问题、完整的计划、以及到目前为止已经完成的步骤和结果。
请你专注于解决"当前步骤"，并仅输出该步骤的最终答案，不要输出任何额外的解释或对话。

# 原始问题:
{question}

# 完整计划:
{plan}

# 历史步骤与结果:
{history}

# 当前步骤:
{current_step}

请仅输出针对"当前步骤"的回答:
"""

import ast
from typing import Optional, List, Dict
from hello_agents import PlanAndSolveAgent, HelloAgentsLLM, Config, Message, ToolRegistry

class MyPlanAndSolveAgent(PlanAndSolveAgent):
    """
    重写的Plan and Solve 智能体
    """
    def __init__(
            self,
            name: str,
            llm: HelloAgentsLLM,
            system_prompt: Optional[str] = None,
            config: Optional[Config] = None,
            custom_prompt: Optional[Dict[str, str]] = None
    ):
        super().__init__(name,llm,system_prompt,config)
        if custom_prompt:
            self.planner_prompt = custom_prompt.get("planner")
            self.executor_prompt = custom_prompt.get("executor")
        else:
            self.planner_prompt = DEFAULT_PLANNER_PROMPT
            self.executor_prompt = DEFAULT_EXECUTOR_PROMPT

        print(f"✅ {name} 初始化完成")

    def run(self,input_text: str, **kwargs) -> str:
        """
        运行p and s agent
        """
        history = ""
        print(f"\n🤖{self.name}开始处理问题{input_text}")

        prompt = self.planner_prompt.format(
            question = input_text
        )
        messages = [{"role":"user", "content": prompt}]
        plan_text = self.llm.invoke(messages, **kwargs)


        # 匹配所有 "步骤" 后跟数字的模式
        plan_list = plan_text.split("```python")[1].split("```")[0].strip()
        try:
        # 去除首尾空白，然后安全求值
            steps_list = ast.literal_eval(plan_list.strip())
            if not isinstance(steps_list, list):
                raise ValueError("解析结果不是列表")
        except (SyntaxError, ValueError) as e:
            print(f"解析失败: {e}")
            steps_list = []


        
        for i, step in enumerate(steps_list,1):
            print(f"\n🤖正在执行第{i}步计划")
            prompt = self.executor_prompt.format(
            question = input_text,
            plan = steps_list,
            history = history if history else "无",
            current_step = step
        )
            messages = [{"role":"user", "content": prompt}]
            response = self.llm.invoke(messages, **kwargs)
            history += f"第{i}步：{step}\n结果:\n{response}"
            final_answer = response
            print(f"✅ 步骤 {i} 已完成，结果: {final_answer}")
        
        return final_answer








