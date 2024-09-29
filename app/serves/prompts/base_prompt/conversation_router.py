from app.serves.prompts.base_prompt.base_prompt import BasePrompt


class ConversationRouter(BasePrompt):
    def __init__(self, text, input_format=None, output_format=None):
        input_format = input_format or (
            f"根据以下人类信息，选择一个路径：\n"
            "[人类信息]:\n"
            f"{text}\n"
            "[信息结束]"
        )
        super().__init__(text, input_format, output_format)
        self.role = "你是一位路由器，负责根据人类的信息选择两个可能的行动路径中的一个。"
        self.task = ("根据人类的信息，判断是选择'COMPLEX'路径还是'SIMPLE'路径。"
                     "'COMPLEX'路径适用于需要高级聚合、数字计算或涉及特定讨论的详细信息的问题。"
                     "'SIMPLE'路径适用于可以用简单响应、问候、告别或社区讨论摘要回答的问题。"
                     "遵循以下规则："
                     "规则1：如果查询上下文中没有出现信息，你不应推断信息。"
                     "规则2：只能根据你选择路径的原因回答相应类型的查询。")
        self.constraints = ["只能回答一个词：'COMPLEX'或'SIMPLE'。"]
