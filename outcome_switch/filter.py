import re
from typing import Dict, List, Any, Tuple

STRICT_OUTCOME_REGEX = '(outcome|end(\s)?point)'
OUTCOME_REGEX = '(outcome|end(\s)?point|measure|assessment)'

METHOD_REGEX = '(method|approach|strategy|design|protocol)'
SAMPLE_SIZE_REGEX = 'sample\s(size|number)'
ABSTRACT_REGEX = '(abstract|summary)'

STRICT_PRIM_SEC_REGEX = f'(primary|secondary|main|)\s([a-z]+\s)?{STRICT_OUTCOME_REGEX}'
PRIM_SEC_REGEX = f'(primary|secondary|main|)\s([a-z]+\s)?{OUTCOME_REGEX}'
STRICT_METHOD_AND_PRIM_SEC_REGEX = f'{METHOD_REGEX}.+{STRICT_PRIM_SEC_REGEX}' 
METHOD_AND_PRIM_SEC_REGEX = f'{METHOD_REGEX}.+{PRIM_SEC_REGEX}'

CHECK_PRIORITY = [
    ("strict_method_and_prim_sec","title",STRICT_METHOD_AND_PRIM_SEC_REGEX),
    ("strict_prim_sec","title",STRICT_PRIM_SEC_REGEX),
    ("prim_sec","title",PRIM_SEC_REGEX),
    ("outcome","title",OUTCOME_REGEX),
    ("strict_prim_sec","content",STRICT_PRIM_SEC_REGEX),
    ("prim_sec","content",PRIM_SEC_REGEX),
    ("method_and_prim_sec","title",METHOD_AND_PRIM_SEC_REGEX),
    ("outcome","content",OUTCOME_REGEX),
    ("method","title",METHOD_REGEX),
    ("sample_size","title",SAMPLE_SIZE_REGEX),
    ("abstract","title",ABSTRACT_REGEX),
]

def filter_sections(sections_dict: Dict[str, List[str]]) -> Dict[str, Any] :
    """Filter sections to keep only the ones containing relevant information if the text is a fulltext
    else keep all sections of abstract

    Args:
        sections_dict (Dict[str,List[str]]): dictionary containing all sections titles (keys) and their corresponding text content (values)
        text_type (str): type of text to filter (abstract or fulltext)

    Returns:
        Dict[str,Any]: dictionary containing the following keys:
            - filtered_sections: dictionary containing all sections titles (keys) and their corresponding text content (values) that contain relevant information
            - regex_priority_index: index of the regex used to filter the sections in the CHECK_PRIORITY list
            - regex_priority_name: name of the regex used to filter the sections in the CHECK_PRIORITY list
            - check_type: type of check used to filter the sections (title or content)
    """
    filter_output = {
        "filtered_sections" : None,
        "regex_priority_index" : None,
        "regex_priority_name" : None,
        "check_type" : None,
    }
    if not sections_dict:
        return filter_output
    # else we filter the sections
    filter_output["filtered_sections"] = {} # init
    match_found = False
    for i, el  in enumerate(CHECK_PRIORITY) :
        priority_name, content_type, current_regex = el
        current_regex = re.compile(current_regex, re.IGNORECASE)
        for title, content_list in sections_dict.items() :
            content = title if content_type == "title" else '\n'.join(content_list)
            if current_regex.search(content) :
                filter_output["check_type"] = content_type
                filter_output["regex_priority_name"] = priority_name
                filter_output["regex_priority_index"] = i
                filter_output["filtered_sections"][title] = content_list
                match_found = True
        if match_found :
            break
    return filter_output


def filter_outcomes(entities: List[Dict[str, Any]]) -> List[Tuple[str,str]]:
    """Filter primary and secondary outcomes from the list of entities a key is created 
    only if at least one entity is found for the given group"""
    outcomes = []
    for entity in entities:
        if entity["entity_group"] == "O":
            continue
        elif entity["entity_group"] == "PrimaryOutcome" :
            outcomes.append(("primary", entity["word"]))
        elif entity["entity_group"] == "SecondaryOutcome":
            outcomes.append(("secondary", entity["word"]))
    return outcomes

def get_sections_text(sections: Dict[str, List[str]]) -> str:
    if not sections :
        return None
    sections_text = ""
    for title, content in sections.items():
        sections_text += title + '\n' + " ".join(content) + '\n'
    return sections_text