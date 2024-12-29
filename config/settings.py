# --- Configuration ---
# Multiple API Keys (add your keys here)
API_KEYS = [
    "API_KEY_1",
    "API_KEY_2",
]

FINAL_REPORT_MODEL_API_KEY = "API_KEY_3"



MODEL_NAME = "gemini-2.0-flash-exp"  # Or any other model you prefer

# Rate Limiting (adjust based on your API's limits)
RATE_LIMIT_REQUESTS_PER_MINUTE = 20
DELAY_SECONDS = 10 / RATE_LIMIT_REQUESTS_PER_MINUTE

# --- Other Settings ---
MAX_RETRIES = 5
INITIAL_DELAY = 2

# --- Final Report Model---
FINAL_REPORT_MODEL = "gemini-exp-1206" 

