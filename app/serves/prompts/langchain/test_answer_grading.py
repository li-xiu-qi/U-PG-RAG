from app.serves.prompts.langchain.base_prompt import BasePrompt


class TestAnswerGrading(BasePrompt):
    def __init__(self, question, ground_truth_answer, student_answer, input_format=None, output_format=None):
        output_format = output_format or "评分："
        super().__init__(student_answer, input_format, output_format)
        self.role = "你是一位老师，正在批改一个测验。"
        self.task = ("根据给定的题目、正确答案和学生答案，"
                     "基于以下评分标准进行评分："
                     "1. 仅根据学生答案相对于正确答案的事实准确性进行评分。"
                     "2. 确保学生答案不包含任何冲突的陈述。"
                     "3. 如果学生答案包含比正确答案更多的信息，只要它相对于正确答案在事实上是准确的，这是可以接受的。"
                     "分数："
                     "100分意味着学生的答案符合所有标准。这是最高（最好）的分数。"
                     "0分意味着学生的答案不符合所有标准。这是你可以给出的最低分数。"
                     "请逐步解释你的推理过程，以确保你的推理和结论是正确的。"
                     "避免一开始就简单地陈述正确答案。")
        self.question = question
        self.ground_truth_answer = ground_truth_answer

    def _apply_dynamic_constraints(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'additional_info':
                self.add_constraint(f"学生答案可以包含比正确答案更多的信息，只要它在事实上是准确的。")
            elif key == 'no_conflict':
                self.add_constraint(f"学生答案不得包含任何冲突的陈述。否则，判断为0分。")
