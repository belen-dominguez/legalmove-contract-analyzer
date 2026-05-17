from dotenv import load_dotenv
from shared.config_loader import ConfigLoader
from shared.logger import get_logger
from openai import OpenAI
from utils.image_parser import parse_contract_image
from models.contract_models import ContractChangeOutput
from agents.contextualization_agent import ContextualizationAgent
from agents.extraction_agent import ExtractionAgent
from shared.tracer import Tracer



config = ConfigLoader()
logger = get_logger("pipeline")
load_dotenv()
client = OpenAI()

def run_pipeline(documents):
    logger.info("LegalMove Contract Analyzer started")

    tracer = Tracer()
    logger.info("Starting trace for contract analysis")


    with tracer.start_trace(
            name="m4-contract-analyzer",
            input_data={"documents":  {"original": documents["original"], "amendment": documents["amendment"]}}
        ) :
    
        with tracer.start_span( config.get("langfuse.spans.parse_original"), input_data={"path": documents["original"]}):
            logger.info("Parsing original contract")
            original_parsed = parse_contract_image(documents["original"], client)
            tracer.set_output({"text": original_parsed})
        
        with tracer.start_span( config.get("langfuse.spans.parse_amendment"), input_data={"path": documents["amendment"]}):
            logger.info("Parsing amendment")
            amendment_parsed = parse_contract_image(documents["amendment"], client)
            tracer.set_output({"text": amendment_parsed})
        
        
        contextualization_agent = ContextualizationAgent(client)

        with tracer.start_span( config.get("langfuse.spans.contextualization"), input_data={"original": original_parsed, "amendment": amendment_parsed}):
            logger.info("Contextualizing documents")
            document_analysis = contextualization_agent.contextualize(original_parsed, amendment_parsed)
            tracer.set_output({"text": document_analysis})

        extraction_agent = ExtractionAgent(client)

        with tracer.start_span( config.get("langfuse.spans.extraction"), input_data={"original": original_parsed, "amendment": amendment_parsed, "context": document_analysis}):
            logger.info("Extracting changes between documents")
            changes_summary = extraction_agent.extract(original_parsed, amendment_parsed, document_analysis)
            tracer.set_output({"text": changes_summary})

        results =  ContractChangeOutput.validate_output(changes_summary)
        
        logger.info("LegalMove Contract Analyzer finished")
        tracer.flush()
        return results
    
