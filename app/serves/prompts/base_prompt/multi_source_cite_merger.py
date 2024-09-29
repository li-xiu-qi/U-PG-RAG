from app.serves.prompts.base_prompt.base_prompt import BasePrompt, PromptExample


class MultiSourceCiteMerger(BasePrompt):
    def __init__(self, responses, input_format=None, output_format=None):
        response_content = ""
        for i, response in enumerate(responses, start=1):
            response_content += f"[响应{i}]:\n{response}\n"
        input_format = input_format or (
            f"根据以下多个响应，合并并调整引用序号：\n"
            "[响应内容]:\n"
            f"{response_content}\n"
            "[响应结束]"
        )
        super().__init__(text="合并多个响应", input_format=input_format, output_format=output_format)
        self.role = "你是一位专业的响应合并和引用调整专家，能够帮助我将多个响应合并，并调整引用序号。"
        self.task = ("根据提供的多个响应内容，合并这些响应并调整引用序号。"
                     "确保每个响应中的引用序号在合并后是连续的，并且引用内容保持一致。"
                     "如果响应中包含相同的内容，将引用和响应一起合并，引用的位置也贴到一起。")

        self.add_example(PromptExample(
            input_text="""
            [响应1]:
            量子计算是一种使用量子位进行计算的技术[1][2]。
            [响应2]:
            量子计算的优势在于其并行处理能力[1][2][3]。
            """,
            output_text="""
            量子计算是一种使用量子位进行计算的技术[1][2]。其优势在于其并行处理能力[3][4][5]。
            """
        ))

        self.add_example(PromptExample(
            input_text="""
            [响应1]:
            量子计算是一种使用量子位进行计算的技术[1][2]。
            [响应2]:
            量子计算是一种使用量子位进行计算的技术，并且具有并行处理能力[3][4]。
            """,
            output_text="""
            量子计算是一种使用量子位进行计算的技术，并且具有并行处理能力[1][2][3][4]。
            """
        ))

    def _apply_dynamic_constraints(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'word_count':
                self.add_constraint(f"合并后的字数不应超过{value}字。")
            elif key == 'target_audience':
                self.add_constraint(f"针对{value}的受众。")
            elif key == 'language':
                self.add_constraint(f"使用{value}输出。")