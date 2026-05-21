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

BASE_METADATA = {
    "pipeline": "m4-contract-analyzer"
}

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
                as_type="trace",
                name="m4-contract-analyzer",
                input_data={"documents":  {"original": documents["original"], "amendment": documents["amendment"]}}
            )  as trace:  
            with self.tracer.start_span( as_type="span", model=config.get("openai.model_vision"),name=config.get("langfuse.spans.parse_original"), input_data={"path": documents["original"]}) as span:
                try:
        
                    logger.info("Parsing original contract")
                    original_parsed = retry_llm_call(
                        lambda: parse_contract_image(documents["original"], self.client)
                    )

                    text = original_parsed["text"]
                    usage = original_parsed["usage"]

                    self.tracer.set_metadata(span, {
                        **BASE_METADATA,
                        "parser": "vision_ocr",
                        "retry_enabled": True,
                        "doc_type": "original"
                    })
            
                    self.tracer.set_output(span, {
                        "text": text,
                        "usage": usage
                    })


                except Exception as e:
                    self.tracer.set_metadata(span, {
                        **BASE_METADATA,
                        "failed_step": "parse_original",
                        "error_type": type(e).__name__
                    })
                    self.tracer.set_error(span, str(e))
                    raise
            
            with self.tracer.start_span( as_type="span",model=config.get("openai.model_vision"), name=config.get("langfuse.spans.parse_amendment"), input_data={"path": documents["amendment"]}) as span:
                try:
                
                    logger.info("Parsing amendment")
                    amendment_parsed = retry_llm_call(
                        lambda: parse_contract_image(documents["amendment"], self.client)
                    )

                    text = amendment_parsed["text"]
                    usage = amendment_parsed["usage"]

                    self.tracer.set_metadata(span, {
                        **BASE_METADATA,
                        "parser": "vision_ocr",
                        "retry_enabled": True,
                        "doc_type": "amendment",
                    })
                
                    self.tracer.set_output(span, {
                        "text": text,
                        "usage": usage
                    })

                except Exception as e:
                    self.tracer.set_metadata(span, {
                        **BASE_METADATA,
                        "failed_step": "parse_amendment",
                        "error_type": type(e).__name__
                    })
                    self.tracer.set_error(span, str(e))
                    raise
            

            with self.tracer.start_span( as_type="generation", model=config.get("openai.model_agents"), name= config.get("langfuse.spans.contextualization"), input_data={"original": original_parsed, "amendment": amendment_parsed}) as span:
                
                logger.info("Contextualizing documents")
                document_analysis = retry_llm_call(
                    lambda: self.contextualization_agent.contextualize(
                        original_parsed["text"],
                        amendment_parsed["text"]
                    )
                )

                text = document_analysis["text"]
                usage = document_analysis["usage"]
                
                self.tracer.set_metadata(span, {
                    **BASE_METADATA,
                    "model": config.get("openai.model_agents"),
                    "temperature": config.get("openai.temperature_contextualization"),
                    "strategy": "legal_context_merge"
                })
                self.tracer.set_output(span, {"text": text, "usage": usage})


            with self.tracer.start_span( as_type="generation",model=config.get("openai.model_agents"), name= config.get("langfuse.spans.extraction"), input_data={"original": original_parsed, "amendment": amendment_parsed, "context": document_analysis}) as span:
                
                logger.info("Extracting changes between documents")
                changes_summary = retry_llm_call(
                    lambda: self.extraction_agent.extract(
                        original_parsed["text"],
                        amendment_parsed["text"],
                        document_analysis["text"]
                    )
                )

                text =  changes_summary["text"]
                usage =  changes_summary["usage"]

                self.tracer.set_metadata(span, {
                    **BASE_METADATA,
                    "model": config.get("openai.model_agents"),
                    "temperature": config.get("openai.temperature_extraction"),
                    "diff_strategy": "llm_structured_diff",
                    "context_used": True
                })
                self.tracer.set_output(span, {"text": text, "usage": usage})
                
            results =  ContractChangeOutput.validate_output(text)
            logger.info("Output validated successfully")
            logger.info("Pipeline completed successfully")
            
            logger.info("LegalMove Contract Analyzer finished")
            self.tracer.set_output(trace, {
                "sections_changed": results.sections_changed,
                "topics_touched": results.topics_touched,
                "summary_of_the_change": results.summary_of_the_change
            })
            self.tracer.flush()
            return results
            

