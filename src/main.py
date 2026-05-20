import argparse
from pipeline import ContractAnalysisPipeline



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LegalMove Contract Analyzer")
    parser.add_argument("original", help="Path a la imagen del contrato original")
    parser.add_argument("amendment", help="Path a la imagen de la enmienda")
    args = parser.parse_args()

    pipeline = ContractAnalysisPipeline()
    
    analysis_result = pipeline.run({
        "original": args.original,
        "amendment": args.amendment
    })

    print(analysis_result.model_dump_json(indent=2))