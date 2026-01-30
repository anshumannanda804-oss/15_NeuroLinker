import os
from groq import Groq
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()

class GroqReflectionAI:
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.api_key = None
        if enabled:
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                self.api_key = api_key
                self.client = Groq(api_key=api_key)

    def reflect(self, decision_history_text: str) -> str:
        if not self.enabled or not self.api_key:
            return "Reflection AI disabled or API key missing."

        try:
            # Call Groq model
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": decision_history_text}],
                max_tokens=1024,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Reflection AI failed: {str(e)}"
