from pydantic import BaseModel, Field
from shared.logger import get_logger

log = get_logger("contract_models")

class ContractChangeOutput(BaseModel):
    """
    Esquema de validación del output final del pipeline.
    Define la estructura esperada del JSON que produce el Agente 2
    antes de ser devuelto al sistema.
    """
    sections_changed: list[str] = Field(..., min_length=1, description="Secciones modificadas en la enmienda")
    topics_touched: list[str] = Field(..., min_length=1, description="Temas legales afectados por los cambios")
    summary_of_the_change: str = Field(..., min_length=20, description="Resumen detallado de los cambios realizados")

    @staticmethod
    def validate_output(data) -> "ContractChangeOutput": 
        """
        Valida que un JSON  cumpla con la estructura definida.
        Si el JSON es válido, devuelve una instancia de ContractChangeOutput.
        Si no es válido, lanza una excepción con detalles del error.
        """
        
        try:
            log.info("Validating output format")
            # CASO 1: string JSON
            if isinstance(data, str):
                cleaned = data.strip().removeprefix("```json").removesuffix("```").strip()
                return ContractChangeOutput.model_validate_json(cleaned)

            # CASO 2: dict directo (nuevo flow)
            elif isinstance(data, dict):
                return ContractChangeOutput.model_validate(data)

            else:
                raise ValueError(f"Unsupported type: {type(data)}")
            
        except Exception as e:
            log.error(f"Invalid output format: {e}")
            raise ValueError(f"Invalid output format: {e}")