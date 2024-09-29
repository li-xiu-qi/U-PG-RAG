from app.serves.prompts.base_prompt.base_prompt import BasePrompt


class TextAnalysis(BasePrompt):
    def __init__(self, text, topic, input_format=None, output_format=None):
        input_format = input_format or (
            f"请判断以下文本是否与以下主题相关：{topic}。\n"
            "[文本开始]:\n"
            f"{text}\n"
            "[文本结束]"
        )
        output_format = output_format or (
            "如果文本与主题相关，请提供与给定主题相关的文本摘要。\n"
            "以最事实的方式回答。只使用文本中的内容。\n"
            "请使用以下格式返回结果：\n"
            "- 相关性：是/否\n"
            "- 谁：\n"
            "- 什么：\n"
            "- 哪里：\n"
            "- 何时：\n"
            "- 为什么：\n"
            "如果文本与主题不相关，请返回：'相关性：否'\n"
            "答案："
        )
        super().__init__(text, input_format, output_format)
        self.role = "你是一位文本分析专家，能够判断文本与特定主题的相关性。"
        self.task = ("分析给定的文本，判断其是否与指定的主题相关。"
                     "如果相关，提供文本的摘要，包括关键信息如谁、什么、哪里、何时和为什么。"
                     "确保回答基于文本内容，避免添加个人观点或未在文本中提及的信息。"
                     "如果文本与主题不相关，明确指出。")
        self.add_constraint("只使用文本中的内容进行分析。")
        self.add_constraint("以事实为基础，避免主观判断。")
        self.add_constraint("如果文本与主题不相关，只返回'相关性：否'。")
