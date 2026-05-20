from dotenv import load_dotenv
from shared.config_loader import ConfigLoader
from shared.logger import get_logger
from openai import OpenAI
from parsers.image_parser import parse_contract_image
from models.contract_models import ContractChangeOutput
from agents.contextualization_agent import ContextualizationAgent
from agents.extraction_agent import ExtractionAgent
from shared.tracer import Tracer
from utils.retry_llm_call import retry_llm_call



config = ConfigLoader()
logger = get_logger("pipeline")
load_dotenv()

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
                    lambda: parse_contract_image(documents["original"], self.client)
                )
                self.tracer.set_output({"text": original_parsed})
            
            with self.tracer.start_span( config.get("langfuse.spans.parse_amendment"), input_data={"path": documents["amendment"]}):
                logger.info("Parsing amendment")
                amendment_parsed = retry_llm_call(
                    lambda: parse_contract_image(documents["amendment"], self.client)
                )
                self.tracer.set_output({"text": amendment_parsed})
            
            

            with self.tracer.start_span( config.get("langfuse.spans.contextualization"), input_data={"original": original_parsed, "amendment": amendment_parsed}):
                logger.info("Contextualizing documents")
                document_analysis = retry_llm_call(
                    lambda: self.contextualization_agent.contextualize(
                        original_parsed,
                        amendment_parsed
                    )
                )
                
                self.tracer.set_output({"text": document_analysis})


            with self.tracer.start_span( config.get("langfuse.spans.extraction"), input_data={"original": original_parsed, "amendment": amendment_parsed, "context": document_analysis}):
                logger.info("Extracting changes between documents")
                changes_summary = retry_llm_call(
                    lambda: self.extraction_agent.extract(
                        original_parsed,
                        amendment_parsed,
                        document_analysis
                    )
                )
                self.tracer.set_output({"text": changes_summary})

            results =  ContractChangeOutput.validate_output(changes_summary)
            logger.info("Output validated successfully")
            logger.info("Pipeline completed successfully")
            
            logger.info("LegalMove Contract Analyzer finished")
            self.tracer.flush()
            return results
        
