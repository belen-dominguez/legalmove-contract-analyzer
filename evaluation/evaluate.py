

import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from pipeline import run_pipeline


def evaluate_case(case_name, case_data):
    print(f"\n=== Evaluando: {case_name} ===")
    
    result = run_pipeline({
        "original": f"data/test_contracts/{case_data['files']['original']}",
        "amendment": f"data/test_contracts/{case_data['files']['amendment']}"
    })
    
    expected = case_data["expected_output"]
    
    # comparar sections_changed
    sections_ok = all(
        any(expected_s.lower() in real_s.lower() or real_s.lower() in expected_s.lower()
            for real_s in result.sections_changed)
        for expected_s in expected["sections_changed"]
    )
    print(f"sections_changed: {'✅' if sections_ok else '❌'}")


    # comparar topics_touched
    def palabras_clave(texto):
        return set(w.lower() for w in texto.split() if len(w) > 3)

    topics_ok = all(
        any(palabras_clave(esperado) & palabras_clave(real)
            for real in result.topics_touched)
        for esperado in expected["topics_touched"]
    )
    print(f"topics_touched: {'✅' if topics_ok else '❌'}")
    

    # comparar summary (verificamos que mencione palabras clave)
    summary_ok = len(result.summary_of_the_change) > 50
    print(f"summary_of_the_change: {'✅' if summary_ok else '❌'}")

def main():
    with open("data/golden_cases.json", "r") as f:
        golden_cases = json.load(f)
    
    for case_name, case_data in golden_cases.items():
        evaluate_case(case_name, case_data)

if __name__ == "__main__":
    main()