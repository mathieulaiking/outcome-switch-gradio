import json
import gradio as gr
from outcome_switch import OutcomeSwitchingDetector, get_sections_text
from outcome_switch.visual import (
    get_article_markdown,
    get_highlighted_text,
    get_registry_dataframe,
    get_sankey_diagram,
)

_CALCULATED_COSINE_THRESHOLD = 0.44 
_app_description = open("front/app-description.md").read()
_article_id_examples = json.load(open("front/examples.json"))
_pmcid_start_value = _article_id_examples[0]
config = json.load(open('./config.json', 'r'))

# Load Detector (ner and sim model)
osd = OutcomeSwitchingDetector(
    config["ner_path"], 
    config["sim_path"],
    config["ner_label2id"]
)

def controller(article_id:str):
    # clean input and run detection
    article_id = str(article_id).strip()
    output = osd.detect(article_id)

    # init outputs
    article_markdown=None
    article_highlighted_text=None
    registry_df=None
    similarity_diagram=None

    # check whether article markdown can be displayed
    if output["db"] is None :
        gr.Warning(f"Wrong format for input id : {article_id}")
        return None, None, None, None
    elif output["article_sections"] is None or output["filtered_sections"] is None:
        gr.Warning(f"Could not retrieve text for id {article_id} (id not found in database or abstract/fulltext unavailable on PubMed/PMC)")
        return None, None, None, None
    else : 
        article_markdown = get_article_markdown(article_id, output["article_sections"], output["filtered_sections"])
    
    # check whether annotations can be displayed
    if output["raw_entities"] is not None and output["filtered_sections"] is not None:
        original_text = get_sections_text(output["filtered_sections"])
        article_highlighted_text = get_highlighted_text(output["raw_entities"], original_text)
    else :
        gr.Warning("Could not extract any outcomes entities in article text")
        
    # check whether registry outcomes can be displayed
    if output["ctgov_outcomes"] is not None:
        registry_df = get_registry_dataframe(output["ctgov_outcomes"])
    else:
        gr.Warning("ClinicalTrials.Gov outcomes were not found (either no NCTID detected or no outcomes declared in registry)")
        return article_markdown, article_highlighted_text, registry_df, similarity_diagram

    # check whether similarity diagram can be displayed
    if (output["connections"] is not None and output["raw_entities"] is not None and
        output["ctgov_outcomes"] is not None and output["article_outcomes"] is not None):
        registry_outcomes_tup = [(outcome["type"], outcome["measure"] + " , " + outcome["timeFrame"]) 
                        for outcome in output["ctgov_outcomes"]]
        similarity_diagram = get_sankey_diagram(
            registry_outcomes_tup,
            output["article_outcomes"],
            output["connections"],
            output["raw_entities"],
            _CALCULATED_COSINE_THRESHOLD
        )
    else:
        gr.Warning("Could not compute similarity diagram (missing registry or article outcomes)")

    return article_markdown, article_highlighted_text, registry_df, similarity_diagram

def clean():
    return None, None, None, None

with gr.Blocks() as blocks:
    with gr.Column():
        gr.Markdown('# Outcome Switching Detection \n' + _app_description )
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    pmid_input = gr.Textbox(value=_pmcid_start_value, label="PMID or PMCID (PMCID must be preceded by 'PMC' prefix)")
                with gr.Row():
                    clear_button = gr.ClearButton()    
                    detect_button = gr.Button(value="Detect", variant="primary")
        gr.Examples(examples = _article_id_examples, inputs=pmid_input)
        gr.Markdown("## Results  \n")
        with gr.Tabs():
            with gr.TabItem("Article Useful Sections"):
                filtered_article = gr.Markdown()
            with gr.TabItem("Article Detected Outcomes"):
                ner_output = gr.HighlightedText(
                    color_map={"primary": "lightcoral", "secondary": "lightgreen"},
                    show_legend=True,
                    combine_adjacent=True,
                )
            with gr.TabItem("Registry Outcomes"):
                ctgov_output = gr.DataFrame()
            with gr.TabItem("Similarity"):
                similarity_output = gr.Plot(show_label=False)
    # OUTPUTS AND BUTTONS
    outputs = [filtered_article, ner_output, ctgov_output,  similarity_output]
    clear_button.add([pmid_input]+outputs)
    detect_button.click(fn=controller, inputs=pmid_input, outputs=outputs)

blocks.launch()
