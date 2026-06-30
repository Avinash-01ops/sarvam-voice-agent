from dotenv import load_dotenv
import os

load_dotenv()

print(os.getenv("SARVAM_API_KEY"))