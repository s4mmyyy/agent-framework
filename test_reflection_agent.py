# test_reflection_agent.py
from dotenv import load_dotenv
from hello_agents import HelloAgentsLLM
from my_reflection_agent import MyReflectionAgent

load_dotenv()
llm = HelloAgentsLLM()

# 默认使用提示词
general_agent = MyReflectionAgent(name="我的反思助手",llm=llm)

#使用自定义代码生成提示词（类似第四章）
code_prompts = {
    "initial": "你是Python代码专家，请编写函数{task}",
    "reflect": "请审查代码的算法效率：\n任务:{task}\n代码:{content}",
    "refine": "请根据反馈优化代码:\n任务:{task}\n反馈:{feedback}"
}

code_agent = MyReflectionAgent(
    name="我的代码生成助手",
    llm=llm,
    custom_prompt=code_prompts

)

#测试使用
result = general_agent.run("写一篇关于人工智能发展的简短文章")
print(f"最终结果{result}")