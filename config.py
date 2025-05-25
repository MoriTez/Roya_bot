import os

# Bot configuration
BOT_TOKEN = os.getenv("7538244929:AAG8moGzCUlkxo8Oy06WiQhQZbAkyDVguao" "YOUR_BOT_TOKEN_HERE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 5  # max requests per window per user

# Image processing configuration
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
SUPPORTED_FORMATS = ['JPEG', 'JPG', 'PNG', 'WEBP']
