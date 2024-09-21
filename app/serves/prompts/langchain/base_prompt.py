from abc import ABC


class PromptExample:
    def __init__(self, input_text, output_text):
        """
        初始化Example实例，表示输入和输出的配对。
        :param input_text: 示例的输入文本
        :param output_text: 示例的输出文本
        """
        self.input_text = input_text
        self.output_text = output_text

    def __str__(self):
        """
        定义对象的字符串表示形式，方便打印输出。
        :return: 输入和输出的格式化字符串
        """
        return f"输入：{self.input_text}\n输出：{self.output_text}"


class BasePrompt(ABC):
    def __init__(self, text=None, input_format=None, output_format=None):
        """
        初始化PromptTemplate实例，定义基本结构。
        :param text: 需要生成提示的原始文本
        :param input_format: 输入文本的格式，默认格式为"输入：{text}"
        :param output_format: 输出文本的格式，默认格式为空
        """
        self.text = text  # 原始文本
        self.role = ""  # 系统角色
        self.task = ""  # 模板任务描述
        self.constraints = []  # 约束条件列表
        self.context = ""  # 上下文信息
        self.examples = []  # 示例列表
        self.input_format = input_format or f"""输入：{text}"""  # 输入格式
        self.output_format = output_format or ""  # 输出格式

    def add_constraint(self, constraint):
        """
        添加约束到当前模板的约束列表。
        :param constraint: 约束条件（如字数限制等）
        """
        self.constraints.append(constraint)

    def remove_constraint(self, constraint):
        """
        从约束列表中移除指定的约束。
        :param constraint: 要移除的约束
        """
        if constraint in self.constraints:
            self.constraints.remove(constraint)

    def add_context(self, context):
        """
        添加上下文信息，用于丰富生成的提示。
        :param context: 上下文信息
        """
        self.context = context

    def add_example(self, example):
        """
        添加示例到当前模板的示例列表。示例必须为Example类的实例。
        :param example: Example类的实例
        :raises ValueError: 如果example不是Example的实例，则抛出异常
        """
        if isinstance(example, PromptExample):
            self.examples.append(example)
        else:
            raise ValueError("示例必须是 PromptExample 类的实例")

    def clear_examples(self):
        """
        清除所有添加的示例。
        """
        self.examples.clear()

    def clear_constraints(self):
        """
        清除所有约束。
        """
        self.constraints.clear()

    def generate_sections(self):
        """
        生成各个部分的内容。
        :return: 包含部分内容的字典
        """
        return {
            "任务": self.task,
            "约束": "\n".join(self.constraints) if self.constraints else "",
            "示例": "\n".join(str(example) for example in self.examples) if self.examples else "",
            "上下文": self.context,
            "输入": self.input_format,
            "输出": self.output_format
        }

    def generate_prompt(self, **kwargs):
        """
        生成提示文本，包含各个部分的内容。
        :param kwargs: 动态参数，用于生成提示时的自定义约束和要求
        :return: 生成的提示文本
        """
        self._apply_dynamic_constraints(**kwargs)
        sections = self.generate_sections()
        markdown_prompt = "\n\n".join(f"# {title}\n{content}" for title, content in sections.items() if content)
        return markdown_prompt

    def to_messages(self, **kwargs):
        """
        将生成的提示转换为消息格式，适合用于聊天机器人接口。
        :param kwargs: 动态参数，用于生成提示时的自定义约束和要求
        :return: 消息列表，包含系统消息和用户消息
        """
        # 调用generate_prompt生成用户消息内容
        prompt = self.generate_prompt(**kwargs)
        system_message = {"role": "system", "content": self.role}  # 系统角色消息
        user_message = {"role": "user", "content": prompt}  # 用户输入消息
        return [system_message, user_message]

    def _apply_dynamic_constraints(self, **kwargs):
        pass
