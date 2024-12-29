from google.generativeai import configure, GenerativeModel
from config.settings import API_KEYS, MODEL_NAME

class GeminiModel:
    def __init__(self, api_key, model_name=MODEL_NAME):
        configure(api_key=api_key)
        self.model = GenerativeModel(model_name)

    def generate_content(self, prompt):
        """Generates content using the Gemini model."""
        response = self.model.generate_content(prompt)
        return response
