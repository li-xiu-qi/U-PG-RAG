from app.serves.prompts.langchain.base_prompt import BasePrompt


class MultiPerspectiveQuery(BasePrompt):
    def __init__(self, text, query_count, input_format=None, output_format=None):
        input_format = input_format or (
            f"生成以下问题的{query_count}个不同版本，以便从向量数据库中检索相关文档：\n"
            "[问题]:\n"
            f"{text}\n"
            "[问题结束]"
        )
        super().__init__(text, input_format, output_format)
        self.role = "你是一位AI语言模型助手，负责生成多个版本的查询以从向量数据库中检索相关文档。"
        self.task = ("生成给定用户问题的不同版本，以帮助用户克服基于距离的相似性搜索的限制。"
                     "每个问题应从不同的角度或方面重新表述原始问题，以便更全面地覆盖相关信息。"
                     "请确保每个问题都清晰、准确地表达了原始问题的核心内容。")
