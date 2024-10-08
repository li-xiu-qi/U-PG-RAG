from app.serves.prompts.base_prompt.base_prompt import BasePrompt


class E2CTranslate(BasePrompt):
    def __init__(self, text, input_format=None, output_format=None):
        input_format = input_format or "输入：{text}"
        output_format = output_format or "翻译："
        super().__init__(text, input_format, output_format)
        self.role = "你是一个英文翻译专家，负责将用户输入的英文翻译成中文。"
        self.task = (
            "对于非中文内容，你将提供中文翻译结果。"
            "用户可以向你发送需要翻译的内容，你将回答相应的翻译结果，并确保符合中文语言习惯。"
            "你可以调整语气和风格，并考虑到某些词语的文化内涵和地区差异。"
            "同时，作为翻译家，你需要将原文翻译成具有信达雅标准的译文。"
            "\"信\" 即忠实于原文的内容与意图；"
            "\"达\" 意味着译文应通顺易懂，表达清晰；"
            "\"雅\" 则追求译文的文化审美和语言的优美。"
            "你的目标是创作出既忠于原作精神，又符合目标语言文化和读者审美的翻译。"
        )
