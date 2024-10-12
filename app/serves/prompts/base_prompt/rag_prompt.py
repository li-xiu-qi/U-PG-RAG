from app.serves.prompts.base_prompt.base_prompt import BasePrompt, PromptExample


class RAGPrompt(BasePrompt):
    def __init__(self, text, context, input_format=None, output_format=None):
        input_format = input_format or f"问题：{text} 上下文：{context} "
        output_format = output_format or ""
        super().__init__(text, input_format, output_format)
        self.role = "你是问答任务的助手。"
        self.task = ("1.使用以下检索到的上下文来回答问题。"
                     "2.如果您不知道答案，就说您不知道。"
                     "3.用户可以要求更多信息。"
                     "4.用户没有输出格式要求时，优先使用md格式。")
