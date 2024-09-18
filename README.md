---
title: Outcome Switching Detector
emoji: 🔄 
colorFrom: blue
colorTo: gray
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: true
python_version: 3.11.9
models: ['aakorolyova/primary_and_secondary_outcome_extraction','Mathking/all-mpnet-outcome-similarity']
---

# Outcome Switching Detector

## Installation

1. Download dependencies : `pip install -r requirements.txt`

2. Define pretrained models path in config file : you must redefine `config.json` so that it points to the models if you do not have them on disk. You also can redefine ner_labe2id depending on the model you use
```json
{
    "ner_path": "aakorolyova/primary_and_secondary_outcome_extraction",
    "sim_path": "laiking/all-mpnet-outcome-similarity",
    "ner_label2id" : {
        "O": 0,
        "B-PrimaryOutcome": 1,
        "I-PrimaryOutcome": 2,
        "B-SecondaryOutcome": 3,
        "I-SecondaryOutcome": 4
    }
}
```

1. Run `python3 -m app.py`