# La funcion de este agente es recibir dos textos extraidos y producir un mapa conceptual (analisis del documento)

from shared.config_loader import ConfigLoader
from shared.logger import get_logger

from prompts.templates import CONTEXT_AGENT_PROMPT

config = ConfigLoader()
log = get_logger("contextualization_agent")

class ContextualizationAgent:
    def __init__(self, client):
        self.client = client

    def contextualize(self, original_text, amendment_text):
        """Recibe el texto completo del contrato original y el texto completo de la enmienda y produce un mapa conceptual que refleja la estructura del documento, sus secciones principales, cláusulas relevantes y temas tratados.
        
        Args:
            original_text (str): El texto completo del contrato original.
            amendment_text (str): El texto completo de la enmienda.
        Returns:
            str: Un mapa conceptual que refleja la estructura del documento, sus secciones principales, cláusulas relevantes y temas tratados.
        """
        log.info("Contextualization agent started")

        try:
            model = config.get("openai.model_agents")
            client_response = self.client.responses.create(
                model=model,
                input=[
                    {
                        "role": "system",
                        "content": CONTEXT_AGENT_PROMPT
                    },
                    {
                        "role": "user",
                        "content": f"contrato original:\n{original_text}\n\nEnmienda:\n{amendment_text}"
                    }
                ],
            )

            log.info("Context map generated successfully")

            return client_response.output_text
        except Exception as e:
            log.error(f"Error en ContextualizationAgent: {e}")
            raise e