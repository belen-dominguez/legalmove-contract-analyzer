# La funcion de este agente es recibir dos textos extraidos y producir un resumen de los cambios realizados entre ambos documentos

from agents.base_agent import BaseAgent
from shared.config_loader import ConfigLoader
from shared.logger import get_logger
from utils.llm_client import generate_response
from prompts.templates import EXTRACTION_AGENT_PROMPT

config = ConfigLoader()
log = get_logger("extraction_agent")

class ExtractionAgent(BaseAgent):
    def __init__(self, client):
        super().__init__(client)

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
            response = self.generate(
                system_prompt=EXTRACTION_AGENT_PROMPT,
                user_prompt=f"""
                Documento original:
                {original_text}

                Enmienda:
                {amendment_text}

                Mapa contextual de los documentos a comparar:
                {document_analysis}
                """
            )

            log.info("Extraction completed successfully")

            return response
                    
        except Exception as e:
            log.error(f"Error en ExtractionAgent: {e}")
            raise 