from app.serves.prompts.base_prompt.base_prompt import BasePrompt


class HelpfulAssistant(BasePrompt):
    def __init__(self, text, input_format=None, output_format=None):
        input_format = input_format or (
            f"根据以下观察结果，回答以下问题：\n"
            "[观察结果]:\n"
            f"{text}\n"
            "[结果结束]"
        )
        super().__init__(text, input_format, output_format)
        self.role = "你是一位乐于助人的助手，负责直接回应给定的任务。"
        self.task = ("根据提供的观察结果，直接并简洁地回答问题。"
                     "如果无法从观察结果中得到答案，请直接回答'I can't answer'。"
                     "确保你的回答与问题的语言一致。")
