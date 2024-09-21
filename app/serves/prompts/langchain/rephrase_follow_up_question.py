from app.serves.prompts.langchain.base_prompt import BasePrompt

class RephraseFollowUpQuestion(BasePrompt):
    def __init__(self, chat_history, question, input_format=None, output_format=None):
        output_format = output_format or "重新表述的问题："
        super().__init__(question, input_format, output_format)
        self.role = "你是一位擅长理解和重构问题的助手，能够帮助我重新表述问题。"
        self.task = ("根据提供的对话历史和后续问题，重新表述后续问题，使其成为一个独立的问题。"
                     "确保新问题清晰、准确，并保持原问题的意图和核心内容不变。")
        self.context = chat_history

    def _apply_dynamic_constraints(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'question_type':
                self.add_constraint(f"将问题重新表述为{value}类型的问题。")
            elif key == 'target_audience':
                self.add_constraint(f"针对{value}的受众重新表述问题。")
            elif key == 'language':
                self.add_constraint(f"使用{value}重新表述问题。")