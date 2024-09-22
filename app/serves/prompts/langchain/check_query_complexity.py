from app.serves.prompts.langchain.base_prompt import BasePrompt, PromptExample


class CheckQueryComplexity(BasePrompt):
    def __init__(self, user_question, input_format=None, output_format=None):
        super().__init__(user_question, input_format, output_format)
        self.role = "你是一个问题复杂性评估员，负责判断用户提出的问题是否为复杂问题。"
        self.task = ("通过分析问题的长度、结构、是否包含多个子问题以及问题需要的知识广度和深度，来判断问题是否复杂。"
                     "复杂问题通常包含多个子问题、需要跨领域知识或涉及复杂推理。"
                     "根据复杂度，给出二进制分数，1表示问题复杂，0表示问题简单。")

        # 添加一个问题复杂的例子
        self.add_example(PromptExample(
            input_text="用户问题: 量子计算与经典计算的主要区别是什么？量子纠缠是如何工作的？它如何应用于量子通信？",
            output_text="1"
        ))

        # 添加一个问题简单的例子
        self.add_example(PromptExample(
            input_text="用户问题: 量子计算是什么？",
            output_text="0"
        ))
