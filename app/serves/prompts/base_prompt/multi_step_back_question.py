from app.serves.prompts.base_prompt.base_prompt import BasePrompt, PromptExample


class MultiStepBackQuestion(BasePrompt):
    def __init__(self, input_text, rewritten_records=None, input_format=None, output_format=None):
        self.rewritten_records = rewritten_records or []
        rewritten_record_text = "\n".join([f"{i + 1}. {record}" for i, record in enumerate(self.rewritten_records)])
        input_format = input_format or (
            f"根据以下输入问题和问题改写记录，生成一个抽象提示：\n"
            "[输入问题]:\n"
            f"{input_text}\n"
            "[输入结束]\n"
            "[已改写记录]:\n"
            f"{rewritten_record_text}\n"
            "[记录结束]\n"
        )
        super().__init__(input_text, input_format, output_format)
        self.role = "你是一个抽象提示生成器，负责根据给定的输入文本和输出文本格式，生成一个抽象提示。"
        self.task = ("根据输入问题和输出问题示例，提取其中包含的抽象概念和原则，并将其转化为一个更高级别的抽象问题。"
                     "该问题应引导模型理解输入文本和输出文本之间的逻辑关系。"
                     "同时，避免产生与改写记录相同的查询。")
        self.add_example(PromptExample(
            input_text="What is the birthplace of Albert Einstein?",
            output_text="what is Albert Einstein's personal history?",
        ))
        self.add_example(PromptExample(
            input_text="爱因斯坦的出生地是哪里？",
            output_text="爱因斯坦的个人历史是什么？",
        ))
        self.add_example(
            PromptExample(
                input_text="爱因斯坦在1970年做了什么？",
                output_text="爱因斯坦的个人历史是什么？",
            )
        )

    def add_rewritten_record(self, record):
        self.rewritten_records.append(record)

    def clear_rewritten_records(self):
        self.rewritten_records.clear()
