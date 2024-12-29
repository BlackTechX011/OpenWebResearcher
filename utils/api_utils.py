import time
import random
import google.api_core.exceptions
from config.settings import API_KEYS, MAX_RETRIES, INITIAL_DELAY
from models.gemini import GeminiModel

current_api_key_index = 0

def with_retry_and_key_rotation(func):
    """Decorator for retrying with exponential backoff and API key rotation."""
    def wrapper(*args, **kwargs):
        global current_api_key_index
        retries = 0
        delay = INITIAL_DELAY

        while retries < MAX_RETRIES:
            try:
                return func(*args, **kwargs)
            except google.api_core.exceptions.ResourceExhausted as e:
                print(f"Rate limit exceeded for API key index {current_api_key_index}.")
                current_api_key_index = (current_api_key_index + 1) % len(API_KEYS)
                new_api_key = API_KEYS[current_api_key_index]
                print(f"Switching to API key index {current_api_key_index} and retrying in {delay} seconds...")

                # Reconfigure the model if it's a GeminiModel instance
                model = kwargs.get("model")
                if isinstance(model, GeminiModel):
                    kwargs["model"] = GeminiModel(new_api_key)

                time.sleep(delay)
                delay *= 2  # Exponential backoff
                delay += random.uniform(-0.5, 0.5)
                retries += 1
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                return "<sum>Error generating summary.</sum>" if func.__name__ == "generate_summary" else None

        return "<sum>Failed to generate summary after multiple retries and API key switches.</sum>" if func.__name__ == "generate_summary" else None

    return wrapper
