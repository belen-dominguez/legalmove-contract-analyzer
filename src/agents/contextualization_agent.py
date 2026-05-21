# La funcion de este agente es recibir dos textos extraidos y producir un mapa conceptual (analisis del documento)

from agents.base_agent import BaseAgent
from shared.config_loader import ConfigLoader
from shared.logger import get_logger
from prompts.templates import CONTEXT_AGENT_PROMPT

config = ConfigLoader()
log = get_logger("contextualization_agent")

class ContextualizationAgent(BaseAgent):
    def __init__(self, client):
        super().__init__(client)

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
            response = self.generate(
                system_prompt=CONTEXT_AGENT_PROMPT,
                user_prompt=f"""
                    contrato original:
                    {original_text}

                    Enmienda:
                    {amendment_text}
                    """,
                temperature=config.get(
                    "openai.temperature_contextualization",
                    0
                )
            )

            log.info("Context map generated successfully")

            return response  
        except Exception as e:
            log.error(f"Error en ContextualizationAgent: {e}")
            raise 