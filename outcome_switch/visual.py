import pandas as pd
import plotly.graph_objects as go
from typing import List, Dict, Any, Tuple, Union


_PUBMED_LINK= "https://pubmed.ncbi.nlm.nih.gov/{article_id}/"
_PMC_LINK = "https://www.ncbi.nlm.nih.gov/pmc/articles/{article_id}/"
_MARKDOWN_TEMPLATE = """# [{article_title}]({article_link})
# Filtered sections :

{sections_md}"""

# entities highlighted text
def get_highlighted_text(entities:List[Dict[str,Any]], original_text:str) -> List[Tuple[str,Union[str,None]]] :
    """Convert the output of the model to a list of tuples (entity, label)
    for `gradio.HighlightedText`output"""
    conversion = {"PrimaryOutcome":"primary","SecondaryOutcome":"secondary"}
    highlighted_text = []
    for entity in entities:
        entity_original_text = original_text[entity["start"]:entity["end"]]
        if entity["entity_group"] == "O":
            entity_output = (entity_original_text, None)
        else:
            entity_output = (entity_original_text, conversion[entity["entity_group"]])
        highlighted_text.append(entity_output)
    return highlighted_text

# article filtered sections markdown output
def get_article_markdown(
        article_id:str,
        article_sections:dict[str,list[str]],
        filtered_sections:dict[str,list[str]]) -> str:
    """Get the markdown of a list of sections"""
    # link to online article
    article_link = _PMC_LINK if article_id.startswith("PMC") else _PUBMED_LINK
    article_link = article_link.format(article_id=article_id)   
    # get title, abstract, and filtered sections
    article_title = article_sections["Title"][0]
    sections_md = ""
    for title, content in filtered_sections.items():
        sections_md += f"## {title}\n"
        sections_md += " ".join(content) + "\n"
    return _MARKDOWN_TEMPLATE.format(
        article_link=article_link,
        article_title=article_title,
        sections_md=sections_md
    )

# registry dataframe display
def _highlight_df_rows(row):
    if row['type'] =='primary':
        return ['background-color: lightcoral'] * len(row)
    elif row['type'] == 'secondary':
        return ['background-color: lightgreen'] * len(row)
    else :
        return ['background-color: lightgrey'] * len(row)

def get_registry_dataframe(registry_outcomes: list[dict[str,str]]) -> str:
    return pd.DataFrame(registry_outcomes).style.apply(_highlight_df_rows, axis=1)

# fcts for sankey diagram
def _sent_line_formatting(sentence:str, max_words:int=10) -> str:
    """format a sentence to be displayed in a sankey diagram so that
    each line has a maximum of `max_words` words"""
    words = sentence.split()
    batchs = [words[i:i+max_words] for i in range(0, len(words), max_words)]
    return "<br>".join([" ".join(batch) for batch in batchs])

def _find_entity_score(entity_text, raw_entities):
    for tc_output in raw_entities:
        if entity_text == tc_output["word"]:
            return tc_output["score"]

def get_sankey_diagram(
        registry_outcomes: list[tuple[str,str]], 
        article_outcomes: list[tuple[str,str]],
        connections: set[tuple[int,int,float]], 
        raw_entities: list[Dict[str,Any]],
        cosine_threshold: float=0.44,
    ) -> go.Figure:

    color_map = {
        "primary": "red",
        "secondary": "green",
        "other": "grey",
    }
    # Create lists of formatted sentences and colors for the nodes
    list1 = [(_sent_line_formatting(sent), color_map[typ]) for typ, sent in registry_outcomes]
    list2 = [(_sent_line_formatting(sent), color_map[typ]) for typ, sent in article_outcomes]
    display_connections = [
        (list1[i][0],list2[j][0],"mediumaquamarine") if cosine > cosine_threshold
        else (list1[i][0],list2[j][0],"lightgray") for i,j,cosine in connections
    ]
    # Create a list of labels and colors for the nodes
    labels = [x[0] for x in list1 + list2]
    colors = [x[1] for x in list1 + list2]
    # Create lists of sources and targets for the connections
    sources = [labels.index(x[0]) for x in display_connections]
    targets = [labels.index(x[1]) for x in display_connections]
    # Create a list of values and colors for the connections
    values = [1] * len(display_connections)
    connection_colors = [x[2] for x in display_connections]

    # data appearing on hover of each node (outcome)
    node_customdata = [f"from: registry<br>type:{t}" for t,_ in registry_outcomes]
    node_customdata += [f"from: article<br>type: {t}<br>confidence: " + str(_find_entity_score(s, raw_entities)) for t,s in article_outcomes]
    node_hovertemplate = "outcome: %{label}<br>%{customdata} <extra></extra>"
    # data appearing on hover of each link (node connections)
    link_customdata = [cosine for _,_,cosine in connections]
    link_hovertemplate = "similarity: %{customdata} <extra></extra>"
    # sankey diagram data filling
    sankey =  go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=colors,
            customdata=node_customdata,
            hovertemplate=node_hovertemplate
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            customdata=link_customdata,
            color=connection_colors,
            hovertemplate=link_hovertemplate
        )
    )
    # conversion to figure
    fig = go.Figure(data=[sankey])
    fig.update_layout(
        title_text="Registry outcomes (left) connections with article outcomes (right), similarity threshold = " + str(cosine_threshold), 
        font_size=10,
        width=1200,
        xaxis=dict(rangeslider=dict(visible=True),type="linear")
    )
    return fig