from shared.config_loader import ConfigLoader

config = ConfigLoader()


def generate_response(
    client,
    model,
    input_data,
    temperature=0,
):
    max_tokens = config.get("openai.max_tokens", 2000)

    response = client.responses.create(
        model=model,
        temperature=temperature,
        max_output_tokens=max_tokens,
        input=input_data,
    )

    response_text = response.output_text.strip()

    if len(response_text) < 50:
        raise ValueError("El modelo devolvió una respuesta vacía o inválida.")

    return response_text