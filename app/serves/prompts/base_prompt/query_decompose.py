from app.serves.prompts.base_prompt.base_prompt import BasePrompt, PromptExample


class QueryDecompose(BasePrompt):
    def __init__(self, text, input_format=None, output_format=None):
        input_format = input_format or "问题：{text}"
        output_format = output_format or "子问题列表：\n1. {subproblem1}\n2. {subproblem2}\n3. {subproblem3}\n..."
        super().__init__(text, input_format, output_format)
        self.role = "你是一位问题分解专家，能够将复杂问题拆解成一系列简洁明了的子问题。"
        self.task = ("将给定的问题分解成一系列子问题。"
                     "每个子问题都应该是自包含的，包含解决它所需的所有信息。"
                     "确保不要分解得过多或包含任何琐碎的子问题，最后将子问题按照解决的顺序排列。")

        self.add_example(example=PromptExample(
            input_text="问题：如何在Python中实现一个简单的冒泡排序算法？",
            output_text="冒泡排序算法的工作原理是什么？\n如何在Python中实现冒泡排序的代码？"
        ))
        self.add_example(example=PromptExample(
            input_text="问题：量子计算与经典计算的主要区别是什么？量子纠缠是如何工作的？它如何应用于量子通信？",
            output_text="量子计算与经典计算的主要区别是什么？\n量子纠缠是如何工作的？\n量子纠缠如何应用于量子通信？")
        )

    def _apply_dynamic_constraints(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'complexity':
                self.add_constraint(f"子问题的复杂度应保持在{value}水平。")
            elif key == 'number_of_subproblems':
                self.add_constraint(f"分解出的子问题数量不超过{value}个。")
