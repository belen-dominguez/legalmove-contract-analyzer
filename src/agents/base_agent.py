from shared.config_loader import ConfigLoader
from utils.llm_client import generate_response

config = ConfigLoader()


class BaseAgent:
    def __init__(self, client):
        self.client = client
        self.model = config.get("openai.model_agents")
        self.max_tokens = config.get("openai.max_tokens", 2000)
        self.temperature = 0

    def generate(self, system_prompt, user_prompt, temperature=0,json_mode=False):
        input_data = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]

        return generate_response(
            client=self.client,
            model=self.model,
            temperature=temperature,
            input_data=input_data,
            json_mode=json_mode
        )