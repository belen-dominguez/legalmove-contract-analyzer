# LegalMove Contract Analyzer 🏛️

Sistema multi-agente que analiza contratos y sus enmiendas usando visión artificial e inteligencia artificial, identificando automáticamente qué cláusulas cambiaron y generando un reporte estructurado.

---

## El problema

El equipo de Compliance de LegalMove pasaba más de 40 horas semanales comparando manualmente contratos originales con sus enmiendas. Este proceso era lento, propenso a errores y un cuello de botella que impedía escalar el negocio.

---

## La solución

Un pipeline multi-agente que recibe dos imágenes escaneadas de contratos (original + enmienda), las procesa con GPT-4o Vision y produce un JSON validado con los cambios detectados, trazable de punta a punta en Langfuse.

---

## Arquitectura

```
imagen original ─┐
                 ├──► GPT-4o Vision ──► texto original ─┐
imagen enmienda ─┘                                       │
                 ├──► GPT-4o Vision ──► texto enmienda ──┤
                                                         │
                                        ┌────────────────┘
                                        │
                                        ▼
                              ContextualizationAgent
                              (Analista Senior)
                              Mapea estructura y secciones
                                        │
                                        ▼
                                ExtractionAgent
                                (Auditor Legal)
                                Identifica cambios
                                        │
                                        ▼
                              Validación Pydantic
                              ContractChangeOutput
                                        │
                                        ▼
                                JSON estructurado ✅
```

Cada etapa queda registrada en **Langfuse** con inputs, outputs y latencia.

---

## Stack técnico

| Herramienta     | Uso                                       |
| --------------- | ----------------------------------------- |
| `GPT-4o`        | Parsing multimodal de imágenes            |
| `GPT-4o-mini`   | Agentes de contextualización y extracción |
| `Pydantic`      | Validación del output estructurado        |
| `Langfuse`      | Trazabilidad completa del pipeline        |
| `python-dotenv` | Manejo seguro de variables de entorno     |
| `PyYAML`        | Configuración centralizada                |
| `Rich`          | Logging con colores en terminal           |

---

## Estructura del proyecto

```
legalmove-contract-analyzer/
├── src/
│   ├── main.py                          # Entry point
│   ├── pipeline.py                      # Orquestación del pipeline completo
│   ├── agents/
│   │   ├── contextualization_agent.py   # Agente 1: Analista Senior
│   │   └── extraction_agent.py          # Agente 2: Auditor Legal
│   ├── parsers/
│   │   └── image_parser.py           # Parsing multimodal con GPT-4o Vision
│   ├── utils/
│   │   ├── llm_client.py
│   │   └── retry_llm_call.py
│   ├── models/
│   │   └── contract_models.py           # Schema Pydantic del output
│   ├── prompts/
│   │   └── templates.py                 # System prompts de cada agente
│   └── shared/
│       ├── config_loader.py             # Carga config.yaml
│       ├── logger.py                    # Logger con Rich
│       └── tracer.py                    # Instrumentación con Langfuse
├── data/
│   ├── test_contracts/                  # Imágenes de contratos de prueba
│   └── golden_cases.json               # Casos de prueba con outputs esperados
├── evaluation/
│   └── evaluate.py                     # Evaluación automatizada con métricas
├── config.yaml                         # Configuración centralizada
├── .env.example                        # Template de variables de entorno
├── requirements.txt                    # Dependencias con versiones fijadas
└── README.md
```

---

## Setup

### 1. Clonar el repositorio

```bash
git clone https://github.com/belen-dominguez/legalmove-contract-analyzer
cd legalmove-contract-analyzer
```

### 2. Crear entorno virtual e instalar dependencias

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

Completar el `.env` con las keys reales:

```
OPENAI_API_KEY=your-openai-api-key-here
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

---

## Uso

### Correr el pipeline

Primer par de contratos:

```bash
python src/main.py data/test_contracts/documento_1__original.jpg data/test_contracts/documento_1__enmienda.jpg
```

Segundo par de contratos:

```bash
python src/main.py data/test_contracts/documento_2__original.jpg data/test_contracts/documento_2__enmienda.jpg
```

### Output esperado

```json
{
  "sections_changed": ["2. Plazo", "3. Pago", "7. Protección de Datos"],
  "topics_touched": [
    "Duración del contrato",
    "Tarifa de licencia",
    "Protección de datos"
  ],
  "summary_of_the_change": "La enmienda extiende el plazo de 12 a 24 meses, aumenta la tarifa anual de USD 12.000 a USD 15.000 y agrega una nueva cláusula de Protección de Datos."
}
```

### Correr la evaluación automatizada

```bash
python evaluation/evaluate.py
```

---

## Contratos de prueba

| Par                                                       | Tipo              | Descripción                                                                                                       |
| --------------------------------------------------------- | ----------------- | ----------------------------------------------------------------------------------------------------------------- |
| `documento_1__original.jpg` + `documento_1__enmienda.jpg` | Cambios simples   | Contrato de licencia de software con cambios en plazo, tarifa y soporte                                           |
| `documento_2__original.jpg` + `documento_2__enmienda.jpg` | Cambios complejos | Contrato de consultoría con cambios en alcance, honorarios, entregables y nueva cláusula de propiedad intelectual |

---

## Trazabilidad en Langfuse

Cada ejecución genera una traza con la siguiente jerarquía de spans:

```
contract-analysis                    ← trace raíz
├── parse_original_contract          ← parsing imagen original
├── parse_amendment_contract         ← parsing imagen enmienda
├── contextualization_agent          ← Agente 1
└── extraction_agent                 ← Agente 2
```

Cada span registra: input, output y latencia.

---

## Resiliencia y validación

El pipeline incorpora mecanismos de resiliencia para mitigar respuestas inconsistentes de modelos LLM:

- Retry automático ante respuestas vacías o inválidas
- Validación estructural intermedia entre etapas
- Validación final estricta con Pydantic
- Logging detallado de cada etapa del pipeline
- Trazabilidad completa mediante Langfuse

---

## Decisiones técnicas

**¿Por qué dos agentes en lugar de uno?**
Separar contextualización de extracción mejora la calidad del análisis. El Agente 1 (Analista Senior) construye un mapa estructural de los documentos sin distracciones. El Agente 2 (Auditor Legal) recibe ese mapa ya procesado y puede enfocarse exclusivamente en identificar cambios con mayor precisión.

**¿Por qué GPT-4o para el parsing de imágenes?**
GPT-4o ofrece capacidades multimodales robustas para interpretar documentos escaneados con jerarquía de cláusulas compleja. GPT-4o-mini es más eficiente en costo y latencia para los agentes que trabajan sobre texto ya extraído.

**¿Por qué Langfuse y no otra herramienta de observabilidad?**
Langfuse tiene integración nativa con Python, permite jerarquía de spans, y su dashboard facilita la auditoría del pipeline durante la defensa en vivo.

**¿Por qué Pydantic para validar el output?**
El output del Agente 2 es texto libre que puede contener ruido. Pydantic garantiza que el JSON final cumple estrictamente el esquema requerido antes de ser consumido por otros sistemas, con validación de tipos y longitudes mínimas por campo.

---

## Limitaciones

- La calidad del parsing depende de la legibilidad de las imágenes.
- Contratos extremadamente extensos pueden requerir chunking o procesamiento incremental.
- El pipeline está optimizado para contratos en español
