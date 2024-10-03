from app.serves.prompts.base_prompt.base_prompt import BasePrompt, PromptExample


class SourceCite(BasePrompt):
    def __init__(self, question, documents, input_format=None, output_format=None):
        doc_content = ""
        for i, doc in enumerate(documents, start=1):
            doc_content += f"[文档{i}]:\n{doc}\n"
        input_format = input_format or (
            f"根据以下问题，总结文档内容并回答问题：\n"
            "[问题开始]"
            f"{question}"
            "[问题结束]"
            "[文档内容]"
            f"{doc_content}"
            "[文档结束]"
        )

        super().__init__(text=question, input_format=input_format, output_format=output_format)
        self.role = "你是一位专业的文献总结和引用专家，能够帮助我整理和总结信息。"
        self.task = ("根据提供的文档内容和来源，总结并回答给定的问题。"
                     "对于每个文档和来源对，检查内容是否足以回答问题。"
                     "如果足够，请在正文部分插入一个引用该文档的句子，并在句子末尾加上方括号中的数字引用。"
                     )
        self.add_example(PromptExample(
            input_text="""
                   [问题开始]: 
                   什么是人工智能？
                   [问题结束]
                   [文档内容]: 
                   [文档1]:
                   人工智能是一种模拟人类智能的技术。
                   [文档2]:
                   人工智能在医疗领域有广泛应用。
                   [文档结束]
                   """,
            output_text="人工智能是一种模拟人类智能的技术，在医疗领域有广泛应用[1][2]。",
        ))
        self.add_example(PromptExample(
            input_text="""
                   [问题开始]: 
                   什么是区块链？
                   [问题结束]
                   [文档内容]: 
                   [文档1]:
                   区块链是一种分布式账本技术。
                   [文档2]:
                   区块链在金融领域有重要应用。
                   [文档结束]
                   """,
            output_text="区块链是一种分布式账本技术[1]。",
        ))

    def _apply_dynamic_constraints(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'word_count':
                self.add_constraint(f"总结的字数不应超过{value}字。")
            elif key == 'target_audience':
                self.add_constraint(f"针对{value}的受众。")
            elif key == 'language':
                self.add_constraint(f"使用{value}输出。")
