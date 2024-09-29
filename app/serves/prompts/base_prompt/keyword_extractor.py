from app.serves.prompts.base_prompt.base_prompt import BasePrompt, PromptExample


class KeywordExtractor(BasePrompt):
    def __init__(self, content, input_format=None, output_format=None):
        input_format = input_format or (
            f"""
            # 提取关键词：
            {content}
            """
        )
        output_format = output_format or "关键词: {keywords}"
        super().__init__(content, input_format, output_format)
        self.role = "您是一位多语言关键词提取器，用于搜索引擎。"
        self.task = ("根据用户提供的内容，提取主题名称作为关键词，并用逗号逐词分隔。"
                     "提取的原则是以少量的关键词来形容核心主题。"
                     )

        self.add_example(PromptExample(
            input_text="""
            # 提取关键词：
            "人工智能在医疗领域的应用正在迅速发展。"
            """,
            output_text="""
            关键词: 人工智能, 医疗, 应用
            """
        ))
        self.add_example(PromptExample(
            input_text="""
            # 提取关键词：
            "人生苦短，我用Python。"
            """,
            output_text="""
            关键词: Python
            """
        ))

    def _apply_dynamic_constraints(self, **kwargs):
        """
        应用动态约束条件，根据输入内容的长度设置字数限制。
        :param kwargs: 输入内容的关键字参数
        """
        # 动态调整关键词个数，默认是三个
        for key, value in kwargs.items():
            if key == 'keyword_count':
                self.add_constraint(f"提取的关键词数量不应超过{value}个。")
            elif key == 'target_audience':
                self.add_constraint(f"针对{value}的受众。")
            elif key == 'language':
                self.add_constraint(f"使用{value}输出。")
        if "keyword_count" not in kwargs:
            self.add_constraint("提取的关键词数量不应超过3个。")
