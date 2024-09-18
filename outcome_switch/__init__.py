from typing import Any
from outcome_switch.ctgov import extract_nct_outcomes
from outcome_switch.similarity import OutcomeSimilarity
from outcome_switch.entrez import dl_and_parse
from outcome_switch.filter import filter_sections, filter_outcomes, get_sections_text
from transformers import (BertConfig, 
                          BertTokenizerFast, 
                          BertForTokenClassification, 
                          TokenClassificationPipeline)

class OutcomeSwitchingDetector:
    """Main Class for the whole pipeline of outcome switching detection"""
    def __init__(self, ner_path:str, sim_path:str, ner_label2id:dict[str,str]):
        # define config
        config = BertConfig.from_pretrained(ner_path, 
                                            label2id=ner_label2id, 
                                            id2label={v: k for k, v in ner_label2id.items()})
        self.outcomes_ner = TokenClassificationPipeline(
            model = BertForTokenClassification.from_pretrained(ner_path,config=config),
            tokenizer = BertTokenizerFast.from_pretrained(ner_path),
            ignore_labels = [],
            aggregation_strategy = "average",
            stride=64
        )
        self.outcome_sim = OutcomeSimilarity(sim_path)

    def _extract_article_outcomes(self, article_text:str) -> dict[str, Any]:
        if not article_text :
            return {"raw_entities" : None, "article_outcomes" : None}
        # get article outcomes (all pieces of text annotated)
        entities_list = self.outcomes_ner(article_text)
        # filter outcomes and reformat
        detected_outcomes =  filter_outcomes(entities_list)
        return {"raw_entities" : entities_list, "article_outcomes" : detected_outcomes}

    def _compare_outcomes(
            self, 
            registry_outcomes:list[tuple[str,str]],
            article_outcomes:list[tuple[str,str]],
        ) -> dict[str, Any]:
        if not registry_outcomes or not article_outcomes :
            return None
        registry_outcomes = [(outcome["type"], outcome["measure"] + " , " + outcome["timeFrame"]) 
                                for outcome in registry_outcomes]
        # semantic similarity of outcomes between registry and article
        return self.outcome_sim.get_similarity(registry_outcomes,article_outcomes)
    
    def detect(self, article_id:str) -> dict[str,Any]:
        """detect outcome switching in input id (pmid, pmcid)
        returns a dictionary with the following keys :  
        - article_xml : xml string of the article
        - article_sections : dict of all sections of the article key=title, value=list of text content
        - check_type : type of the check for regex outcome section filtering (title or content)
        - regex_priority_name : name of the regex used for outcome section filtering
        - regex_priority_index : number of priority of the regex used for outcome section filtering (0 is the highest priority)
        - filtered_sections : dict of all filtered sections of the article key=title, value=list of text content
        - raw_entities : output of huggingface token classification pipeline with aggregated entities but also O text (non-entity)
        - article_outcomes : List of tuples (type, outcome) of all outcomes detected in the article
        - detected_nct_id : first nct id detected in the article
        - ctgov_outcomes : List of tuples (type, outcome) of all outcomes detected in the registry
        """
        # download and parse article
        parse_output = dl_and_parse(article_id)
        # search nct id in text, then download and parse registry outcomes
        registry_outcomes = extract_nct_outcomes(parse_output["article_xml"]) 
        # filter article sections and get text
        filter_output = filter_sections(parse_output["article_sections"])
        sections_text = get_sections_text(filter_output["filtered_sections"])
        # outcomes ner in article text
        ner_output = self._extract_article_outcomes(sections_text)
        # compare outcomes between article and registry
        connections = self._compare_outcomes(registry_outcomes, ner_output["article_outcomes"])
        return parse_output | {"ctgov_outcomes":registry_outcomes} | filter_output | ner_output | {"connections":connections}