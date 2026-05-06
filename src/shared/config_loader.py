"""Cargador de configuración desde config.yaml."""
import yaml


class ConfigLoader:
    """Carga y gestiona la configuración del proyecto."""

    def __init__(self, config_path: str = "config.yaml"):
        """Carga el archivo de configuración."""
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

    def get(self, key: str, default=None):
        """Obtiene un valor usando notación de puntos.

        Ejemplo: config.get("llm.model") retorna el valor de config["llm"]["model"]
        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value if value is not None else default