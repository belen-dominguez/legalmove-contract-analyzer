from shared.logger import get_logger

log = get_logger("retry")

def retry_llm_call(fn, retries=3, min_length=50):
    last_error = None

    for attempt in range(retries):
        try:
            log.info(f"LLM attempt {attempt + 1}/{retries}")

            result = fn()

            if result and len(result.strip()) > min_length:
                return result

            log.warning("LLM devolvió una respuesta vacía o muy corta")

        except Exception as e:
            last_error = e
            log.error(f"Error en intento {attempt + 1}: {e}")

    raise ValueError(
        f"El modelo falló luego de {retries} intentos. Último error: {last_error}"
    )