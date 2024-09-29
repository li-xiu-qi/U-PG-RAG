from app.serves.prompts.base_prompt.base_prompt import BasePrompt, PromptExample


class RetrievalTextRelevance(BasePrompt):
    def __init__(self, document, user_question, input_format=None, output_format=None):
        input_format = input_format or f"""
        用户问题：
        {user_question}
        文档：
        {document}
        """
        super().__init__(document, input_format, output_format)
        self.role = "你是一个评分员，负责评估检索到的文档与用户问题的相关性。"
        self.task = ("如果文档包含与用户问题相关的关键词或语义意义，将其评为相关。"
                     "不需要严格的测试，目标是过滤掉错误的检索。"
                     "给出一个二进制分数，1或0，其中1表示文档与问题相关。")

        self.add_example(PromptExample(
            input_text="用户问题: 什么是量子计算？\n文档: 量子计算是一种使用量子位进行计算的技术。",
            output_text="1"
        ))
