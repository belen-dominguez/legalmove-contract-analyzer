from base64 import  b64encode

from prompts.templates import VISION_PROMPT
from shared.logger import get_logger
from shared.config_loader import ConfigLoader
from utils.llm_client import generate_response


logger = get_logger("image_parser")
config = ConfigLoader()

def parse_contract_image(image_path: str, client) -> str:
    """Recibe la ruta de una imagen que contiene un contrato y devuelve el texto completo del contrato extraído de la imagen.
    
    Args:
        image_path (str): La ruta de la imagen que contiene el contrato.
    Returns:
        str: El texto completo del contrato extraído de la imagen.
    Raises:
        ValueError: Si la ruta de la imagen es inválida o no es un archivo de imagen válido.
        FileNotFoundError: Si no se encuentra el archivo de imagen en la ruta especificada.
        RuntimeError: Si ocurre un error al procesar la imagen."""
    
    if not image_path or not image_path.strip():
                raise ValueError("La ruta de la imagen no puede estar vacía.")

    if not image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                raise ValueError("La ruta de la imagen debe ser un archivo de imagen válido (.png, .jpg, .jpeg, .webp).")      
      
    try:
        logger.info(f"Processing image: {image_path}")

        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()
            image_base64 = b64encode(image_bytes).decode('utf-8')
        
        model = config.get("openai.model_vision")
        temperature = config.get("openai.temperature_vision", 0)
        extension = image_path.lower().split('.')[-1]
        media_type = "image/png" if extension == "png" else "image/jpeg"
        input_data=[
                {
                    "role": "user",
                    "content": [
                        { "type": "input_text", "text": VISION_PROMPT },
                        {
                            "type": "input_image",
                            "image_url": f"data:{media_type};base64,{image_base64}",
                        },
                    ],
                }
            ]
    
        return generate_response(
            client=client,
            model=model,
            temperature=temperature,
            input_data=input_data
        )
        

    
    except FileNotFoundError:
        raise
    except Exception as e:
        raise RuntimeError(f"No se pudo procesar la imagen: {e}")

    