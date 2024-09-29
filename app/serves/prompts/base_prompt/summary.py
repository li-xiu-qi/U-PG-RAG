from app.serves.prompts.base_prompt.base_prompt import BasePrompt


class Summary(BasePrompt):
    def __init__(self, text, input_format=None, output_format=None):
        """
        初始化 SummaryPromptTemplate，继承自 PromptTemplate，并指定特定的任务和角色。
        :param text: 需要生成总结的文本
        :param input_format: 输入格式，默认为"输入：{text}"
        :param output_format: 输出格式，默认为"总结："
        """
        output_format = output_format or "总结："
        super().__init__(text, input_format, output_format)
        # 设置特定的角色和任务描述
        self.role = "你是一位擅长总结和分析的专家，能够协助我。"
        self.task = ("从给定输入的文本中提炼出一个简洁且连贯的总结。"
                     "该总结应精炼地捕捉文本的主要思想、关键点和见解，同时保持信息的完整性和简洁性。"
                     "确保总结传达文本的核心信息及支持性细节，使读者即使未阅读原文也能全面理解。"
                     "在必要时提供背景信息，避免使用过多的专业术语或冗词。")

    def _apply_dynamic_constraints(self, **kwargs):
        """
        动态处理kwargs中的约束条件，如字数限制、目标受众等。
        :param kwargs: 包含动态约束的参数字典
        """
        for key, value in kwargs.items():
            if key == 'word_count':
                self.add_constraint(f"总结的字数不应超过{value}字。")
            elif key == 'target_audience':
                self.add_constraint(f"针对{value}的受众。")
            elif key == 'language':
                self.add_constraint(f"使用{value}输出。")
