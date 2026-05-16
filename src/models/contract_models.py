from pydantic import BaseModel
from shared.logger import get_logger

log = get_logger("contract_models")

class ContractChangeOutput(BaseModel):
    """
    Esquema de validación del output final del pipeline.
    Define la estructura esperada del JSON que produce el Agente 2
    antes de ser devuelto al sistema.
    """
    sections_changed: list[str]  
    topics_touched: list[str]  
    summary_of_the_change: str 

    @staticmethod
    def validate_output(json_string: str) -> "ContractChangeOutput": 
        """
        Valida que un JSON  cumpla con la estructura definida.
        Si el JSON es válido, devuelve una instancia de ContractChangeOutput.
        Si no es válido, lanza una excepción con detalles del error.
        """
        
        try:
            log.info("Validating output format")
            json_string = json_string.strip().removeprefix("```json").removesuffix("```").strip()
            return ContractChangeOutput.model_validate_json(json_string)
        except Exception as e:
            log.error(f"Invalid output format: {e}")
            raise ValueError(f"Invalid output format: {e}")