from dotenv import load_dotenv
from shared.config_loader import ConfigLoader
from shared.logger import get_logger
from openai import OpenAI
from utils.image_parser import parse_contract_image
from models.contract_models import ContractChangeOutput
from agents.contextualization_agent import ContextualizationAgent
from agents.extraction_agent import ExtractionAgent
from shared.tracer import Tracer
from utils.retry_call import retry_llm_call



config = ConfigLoader()
logger = get_logger("pipeline")
load_dotenv()
client = OpenAI()

class ContractAnalysisPipeline:
    def __init__(self):
        self.client = OpenAI()
        self.tracer = Tracer()

        self.contextualization_agent = ContextualizationAgent(self.client)
        self.extraction_agent = ExtractionAgent(self.client)

    def run(self, documents):
        logger.info("LegalMove Contract Analyzer started")

        
        logger.info("Starting trace for contract analysis")


        with self.tracer.start_trace(
                name="m4-contract-analyzer",
                input_data={"documents":  {"original": documents["original"], "amendment": documents["amendment"]}}
            ) :
        
            with self.tracer.start_span( config.get("langfuse.spans.parse_original"), input_data={"path": documents["original"]}):
                logger.info("Parsing original contract")
                original_parsed = retry_llm_call(
                    lambda: parse_contract_image(documents["original"], client)
                )
                self.tracer.set_output({"text": original_parsed})
            
            with self.tracer.start_span( config.get("langfuse.spans.parse_amendment"), input_data={"path": documents["amendment"]}):
                logger.info("Parsing amendment")
                amendment_parsed = retry_llm_call(
                    lambda: parse_contract_image(documents["amendment"], client)
                )
                self.tracer.set_output({"text": amendment_parsed})
            
            

            with self.tracer.start_span( config.get("langfuse.spans.contextualization"), input_data={"original": original_parsed, "amendment": amendment_parsed}):
                logger.info("Contextualizing documents")
                document_analysis = self.contextualization_agent.contextualize(original_parsed, amendment_parsed)

                if not document_analysis or len(document_analysis.strip()) < 100:
                    raise ValueError("Contextualization agent returned empty response")
                
                self.tracer.set_output({"text": document_analysis})



            with self.tracer.start_span( config.get("langfuse.spans.extraction"), input_data={"original": original_parsed, "amendment": amendment_parsed, "context": document_analysis}):
                logger.info("Extracting changes between documents")
                changes_summary = self.extraction_agent.extract(original_parsed, amendment_parsed, document_analysis)
                self.tracer.set_output({"text": changes_summary})

            results =  ContractChangeOutput.validate_output(changes_summary)
            
            logger.info("LegalMove Contract Analyzer finished")
            self.tracer.flush()
            return results
        
