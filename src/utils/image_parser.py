from base64 import  b64encode

from prompts.templates import VISION_PROMPT
from shared.config_loader import ConfigLoader



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
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()
            image_base64 = b64encode(image_bytes).decode('utf-8')
        
        model=config.get("openai.model_vision")
        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "user",
                    "content": [
                        { "type": "input_text", "text": VISION_PROMPT },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{image_base64}",
                        },
                    ],
                }
            ],
        )
        return response.output_text
    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo: {image_path}")
    except Exception as e:
        print(f"Error al procesar la imagen: {e}")
        raise RuntimeError("No se pudo procesar la imagen. Por favor, inténtalo de nuevo.")

    