import os

class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")

    def generate(self, prompt: str) -> str:
        # TODO: Implement Gemini API call
        return "Stub response from Gemini"
