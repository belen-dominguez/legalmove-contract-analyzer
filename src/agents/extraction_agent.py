# La funcion de este agente es recibir dos textos extraidos y producir un resumen de los cambios realizados entre ambos documentos

from openai import OpenAI
from shared.config_loader import ConfigLoader
from shared.logger import get_logger

from prompts.templates import EXTRACTION_AGENT_PROMPT

client = OpenAI()
config = ConfigLoader()
log = get_logger("extraction_agent")

class ExtractionAgent:

    def extract(self, original_text, amendment_text, document_analysis):
        """Recibe el texto completo del contrato original, el texto completo de la enmienda y un análisis del documento (mapa conceptual) y produce un resumen de los cambios realizados entre ambos documentos.
        
        Args:
            original_text (str): El texto completo del contrato original.
            amendment_text (str): El texto completo de la enmienda.
            document_analysis (str): Un análisis del documento que refleja la estructura del contrato, sus secciones principales, cláusulas relevantes y temas tratados.
        Returns:
            str: Un resumen de los cambios realizados entre ambos documentos.
        """
        log.info("Extraction agent started")

        try:
            model = config.get("openai.model_agents")
            client_response = client.responses.create(
                model=model,
                input=[
                    {
                        "role": "system",
                        "content": EXTRACTION_AGENT_PROMPT
                    },
                    {
                        "role": "user",
                        "content": f"documento original:\n{original_text}\n\nEnmienda:\n{amendment_text}\n\nMapa conceptual de los documentos a comparar:\n{document_analysis}"
                    }
                ],
            )

            log.info("Extraction completed successfully")
            
            return client_response.output_text
        except Exception as e:
            log.error(f"Error en ExtractionAgent: {e}")
            raise e