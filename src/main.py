import argparse
import json
from dotenv import load_dotenv
from shared.logger import get_logger
from openai import OpenAI
from models.contract_models import ContractChangeOutput
from utils.image_parser import parse_contract_image
from agents.contextualization_agent import ContextualizationAgent
from agents.extraction_agent import ExtractionAgent

logger = get_logger(__name__)
load_dotenv()
client = OpenAI()

def main(documents):
    logger.info("LegalMove Contract Analyzer started")
    
    parse_documents = parse_contract_image(documents["original"], client), parse_contract_image(documents["amendment"], client)
    
    contextualization_agent = ContextualizationAgent(client)
    document_analysis = contextualization_agent.contextualize(*parse_documents)

    extraction_agent = ExtractionAgent(client)
    changes_summary = extraction_agent.extract(*parse_documents, document_analysis)

    results =  ContractChangeOutput.validate_output(changes_summary)
    
    logger.info("LegalMove Contract Analyzer finished")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LegalMove Contract Analyzer")
    parser.add_argument("original", help="Path a la imagen del contrato original")
    parser.add_argument("amendment", help="Path a la imagen de la enmienda")
    args = parser.parse_args()

    answer = main({
        "original": args.original,
        "amendment": args.amendment
    })
    print(answer.model_dump_json(indent=2))