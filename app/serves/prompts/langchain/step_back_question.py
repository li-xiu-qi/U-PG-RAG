from app.serves.prompts.langchain.base_prompt import BasePrompt, PromptExample


class StepBackQuestion(BasePrompt):
    def __init__(self, input_text, input_format=None, output_format=None):
        super().__init__(input_text, input_format, output_format)
        self.role = "你是一个抽象提示生成器，负责根据给定的输入文本和输出文本，生成一个抽象提示。"
        self.task = ("根据输入文本和输出文本，提取其中包含的抽象概念和原则，并将其转化为一个更高级别的抽象问题。"
                     "该问题应引导模型理解输入文本和输出文本之间的逻辑关系。")
        self.add_example(PromptExample(
            input_text="What is the birthplace of Albert Einstein?",
            output_text="what is Albert Einstein's personal history?",
        ))
