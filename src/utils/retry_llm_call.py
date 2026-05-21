import time
from shared.logger import get_logger

logger = get_logger("retry_llm_call")


def retry_llm_call(fn, retries=3, delay=2):
    last_error = None

    for attempt in range(retries):
        try:
            logger.info(f"LLM attempt {attempt + 1}/{retries}")
            return fn()

        except (ValueError, FileNotFoundError) as e:
            logger.error(f"Non-retryable error: {e}")
            raise e

        except Exception as e:
            last_error = e
            logger.error(f"Error en intento {attempt + 1}: {e}")

            if attempt < retries - 1:
                time.sleep(delay)

    raise ValueError(
        f"El modelo falló luego de {retries} intentos. Último error: {last_error}"
    )
