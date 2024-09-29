from app.serves.prompts.base_prompt.base_prompt import BasePrompt, PromptExample


class ResponseFormatConverter(BasePrompt):
    def __init__(self, response, input_format=None, output_format=None):
        input_format = input_format or (
            f"""
            # 转化下面的内容：
            {response}
            成输出格式
            """

        )
        super().__init__(response, input_format, output_format)
        self.role = "你是一个响应转换器，负责将响应内容按照指定的响应格式进行转换。"
        self.task = ("根据提供的响应内容和一个响应格式，准确、高效地将响应内容转换为响应格式。"
                     "转换后的响应应保持原意，同时严格遵循响应格式的规范。")

        self.add_example(PromptExample(
            input_text="""
            # 输出
            {
                "Relevance": "Yes",
                "Who": "",
                "What": "",
                "Where": "",
                "When": "",
                "Why": ""
            }
            # 转化下面的内容：
            "- Relevance: Yes"
            "- Who:"
            "- What:"
            "- Where:"
            "- When:"
            "- Why:
            成输出格式"
            """,
            output_text="""
            {
                "Relevance": "Yes",
                "Who": "",
                "What": "",
                "Where": "",
                "When": "",
                "Why": ""
            }
            """
        ))
