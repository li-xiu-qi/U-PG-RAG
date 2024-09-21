from app.serves.prompts.langchain.base_prompt import BasePrompt

class SourceSummarizationPromptTemplate(BasePrompt):
    def __init__(self, question, doc_content, input_format=None, output_format=None):
        super().__init__(text=question, input_format=input_format, output_format=output_format)
        self.role = "你是一位专业的文献总结和引用专家，能够帮助我整理和总结信息。"
        self.task = ("根据提供的文档内容和来源，总结并回答给定的问题。"
                     "对于每个文档和来源对，检查内容是否足以回答问题。"
                     "如果足够，请在正文部分插入一个引用该文档的句子，并在句子末尾加上方括号中的数字引用。"
                     "在最后提供来源的图例。")
        self.doc_content = doc_content
        self.question = question
        self.sources = []

    def _apply_dynamic_constraints(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'word_count':
                self.add_constraint(f"总结的字数不应超过{value}字。")
            elif key == 'target_audience':
                self.add_constraint(f"针对{value}的受众。")
            elif key == 'language':
                self.add_constraint(f"使用{value}输出。")