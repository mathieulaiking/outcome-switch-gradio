Demo of outcome switching detection using transformers models. Outcome switching is defined as the modification, inversion, suppression of a primary outcome in a Randomized Controlled Trial(RCT) between the  published article and the registry entry.

What this demo is doing : 
1. Retrieve abstract (PMID given) or fulltext (PMCID given) of an article
2. Parse the Methods section of the article and get section text
3. Use finetuned NER model for detecting primary outcomes in that text
4. Use a RegEx to find the NCT ID (ClinicalTrials.gov) in the full text
5. Use CTGOV API to extract registry primary outcome (considered as ground truth)
6. Use Semantic Textual Similarity Model to compare CTGOV outcome to article detected outcomes