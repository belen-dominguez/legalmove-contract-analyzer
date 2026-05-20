

import json
import sys
import os


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from pipeline import ContractAnalysisPipeline

pipeline = ContractAnalysisPipeline()

def palabras_clave(texto):
    return set(w.lower() for w in texto.split() if len(w) > 3)

def calculate_metrics(real_list: list, expected_list: list) -> dict:
    # completeness: de los esperados, cuántos aparecen en los reales
    encontrados = sum(
        any(palabras_clave(esperado) & palabras_clave(real) for real in real_list)
        for esperado in expected_list
    )
    completeness = encontrados / len(expected_list) if expected_list else 0.0

    # accuracy: de los reales, cuántos coinciden con algún esperado
    correctos = sum(
        any(palabras_clave(real) & palabras_clave(esperado) for esperado in expected_list)
        for real in real_list
    )
    accuracy = correctos / len(real_list) if real_list else 0.0

    return {"accuracy": round(accuracy, 2), "completeness": round(completeness, 2)}


def evaluate_case(case_name, case_data):
    print(f"\n=== Evaluando: {case_name} ===")
    
    result = pipeline.run({
        "original": f"data/test_contracts/{case_data['files']['original']}",
        "amendment": f"data/test_contracts/{case_data['files']['amendment']}"
    })
    
    expected = case_data["expected_output"]
    
    # sections_changed
    sections_ok = all(
        any(expected_s.lower() in real_s.lower() or real_s.lower() in expected_s.lower()
            for real_s in result.sections_changed)
        for expected_s in expected["sections_changed"]
    )
    metrics_sections = calculate_metrics(result.sections_changed, expected["sections_changed"])
    print(f"sections_changed: {'✅' if sections_ok else '❌'} | accuracy: {metrics_sections['accuracy']} | completeness: {metrics_sections['completeness']}")

    # topics_touched
    topics_ok = all(
        any(palabras_clave(esperado) & palabras_clave(real)
            for real in result.topics_touched)
        for esperado in expected["topics_touched"]
    )
    metrics_topics = calculate_metrics(result.topics_touched, expected["topics_touched"])
    print(f"topics_touched: {'✅' if topics_ok else '❌'} | accuracy: {metrics_topics['accuracy']} | completeness: {metrics_topics['completeness']}")

    # summary
    summary_ok = len(result.summary_of_the_change) > 50
    print(f"summary_of_the_change: {'✅' if summary_ok else '❌'}")

    # promedio general
    avg_accuracy = round((metrics_sections['accuracy'] + metrics_topics['accuracy']) / 2, 2)
    avg_completeness = round((metrics_sections['completeness'] + metrics_topics['completeness']) / 2, 2)
    print(f"→ avg accuracy: {avg_accuracy} | avg completeness: {avg_completeness}")
    
    return avg_accuracy, avg_completeness

def main():
    with open("data/golden_cases.json", "r") as f:
        golden_cases = json.load(f)
    
    resultados = []
    for case_name, case_data in golden_cases.items():
        resultados.append(evaluate_case(case_name, case_data))
    
    avg_acc = round(sum(r[0] for r in resultados) / len(resultados), 2)
    avg_comp = round(sum(r[1] for r in resultados) / len(resultados), 2)
    print(f"\n=== Resumen general ===")
    print(f"avg accuracy: {avg_acc} | avg completeness: {avg_comp}")

if __name__ == "__main__":
    main()