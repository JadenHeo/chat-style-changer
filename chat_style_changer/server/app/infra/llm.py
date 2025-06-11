import os

from openai import OpenAI


class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4.1-2025-04-14"

    def generate_response(self, prompt: str, input: str) -> str:
        """Generate a response using the LLM."""
        response = self.client.responses.create(
            model=self.model,
            instructions=prompt,
            input=input
        )
        return response.output_text.strip()