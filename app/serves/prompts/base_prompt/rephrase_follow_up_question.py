from app.serves.prompts.base_prompt.base_prompt import BasePrompt


class RephraseQuestion(BasePrompt):
    def __init__(self, text, input_format=None, output_format=None):
        output_format = output_format or "重新表述的问题："
        super().__init__(text, input_format, output_format)
        self.role = "你是一位擅长理解和重组信息的专家，能够帮助我重新表述问题。"
        self.task = ("根据提供的对话历史和后续问题，重新表述后续问题，使其成为一个独立的问题。"
                     "确保重新表述的问题清晰、准确，并保持原问题的意图和关键信息不变。"
                     "避免添加任何额外的信息或假设，只需专注于问题的重组。")
        self.add_constraint(f"确保重新表述的问题清晰易懂。")
        self.add_constraint(f"保持原问题的意图不变。")
        self.add_constraint(f"确保重新表述的问题准确无误。")
