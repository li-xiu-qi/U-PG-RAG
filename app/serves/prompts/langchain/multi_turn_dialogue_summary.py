from app.serves.prompts.langchain.base_prompt import BasePrompt, PromptExample

class MultiTurnDialogueSummary(BasePrompt):
    def __init__(self, summary, new_lines, input_format=None, output_format=None):
        input_format = input_format or (
            f"Current summary:\n{summary}\n\n"
            f"New conversation lines:\n{new_lines}\n"
        )
        super().__init__(new_lines, input_format, output_format)
        self.role = "You are a multi-turn dialogue summarizer, responsible for updating the dialogue summary based on the provided conversation content."
        self.task = ("Based on the current dialogue summary and the newly added conversation lines, generate a new, more comprehensive dialogue summary."
                     "The new summary should include all relevant information, while maintaining simplicity and coherence.")

        self.add_example(PromptExample(
            input_text="""
            Current summary:
            The human asks what the AI thinks of artificial intelligence. The AI thinks artificial intelligence is a force for good.

            New conversation lines:
            Human: Why do you think artificial intelligence is a force for good?
            AI: Because artificial intelligence will help humans reach their full potential.
            """,
            output_text="""
            New summary:
            The human asks what the AI thinks of artificial intelligence. The AI thinks artificial intelligence is a force for good because it will help humans reach their full potential.
            """
        ))