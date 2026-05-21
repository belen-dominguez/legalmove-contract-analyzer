import argparse
import sys
from pipeline import ContractAnalysisPipeline
from shared.logger import get_logger

logger = get_logger(__name__)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LegalMove Contract Analyzer")
    parser.add_argument("original", help="Path a la imagen del contrato original")
    parser.add_argument("amendment", help="Path a la imagen de la enmienda")
    args = parser.parse_args()

    pipeline = ContractAnalysisPipeline()
    
    try:
        analysis_result = pipeline.run({
            "original": args.original,
            "amendment": args.amendment
        })

        print(analysis_result.model_dump_json(indent=2))

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)
