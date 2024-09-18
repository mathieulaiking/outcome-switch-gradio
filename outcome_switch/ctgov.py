import re
import ast
import requests
from typing import Union

def _find_nctid(text: str) -> Union[str,None]:
    "return nct string if found in text else none"
    match = re.search(r"[Nn][Cc][Tt]0*[1-9]\d{0,7}", text)
    return match[0] if match is not None else match

def _get_registry_outcomes(nct_id: str) -> Union[dict,None]:
    outcomes = None
    r = requests.get(f"https://clinicaltrials.gov/api/v2/studies/{nct_id}", params={"fields":"OutcomesModule"})
    if r.status_code == 200 and "outcomesModule" in r.json()["protocolSection"]:
        outcomes = ast.literal_eval(r.text)["protocolSection"]["outcomesModule"]
    return outcomes

def _reformat_outcomes(outcomes: dict) -> list[dict[str,str]]:
    new_outcomes = []
    for outcome_type, outcome_list in outcomes.items() :
        outcome_type = outcome_type.replace("Outcomes","")
        for outcome_item in outcome_list :
            outcome_item["type"] = outcome_type
            new_outcomes.append(outcome_item)
    return new_outcomes

def extract_nct_outcomes(text:str) -> Union[None,list[dict[str,str]]]:
    """Extract outcomes from a text using CTGOV APIV2 if a nct id is found else return None"""
    outcomes = None
    if text is None : 
        return outcomes
    nct_id = _find_nctid(text)
    if nct_id is not None:
        outcomes = _get_registry_outcomes(nct_id)
        outcomes = _reformat_outcomes(outcomes)
    return outcomes
