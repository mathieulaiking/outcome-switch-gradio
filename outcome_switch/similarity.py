import torch
import torch.nn.functional as F
from sentence_transformers.util import cos_sim
from transformers import AutoTokenizer, AutoModel


class OutcomeSimilarity:
    """ similarity detector between outcomes statements"""
    ID2LABEL = ["different", "similar"]

    def __init__(self, model_path: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModel.from_pretrained(model_path)

    def _mean_pooling(self, model_output, attention_mask: torch.Tensor):
        """ Mean Pooling - Take attention mask into account for correct averaging"""
        # First element of model_output contains all token embeddings
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(
            -1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def _encode(self, outcomes_lot: list[tuple[str,str]]):
        # Parse sentences
        sentences = []
        if len(outcomes_lot) > 0:
            _, sentences = zip(*outcomes_lot)
        # Tokenize sentences
        encoded_input = self.tokenizer(
            sentences, padding=True, truncation=True, return_tensors='pt')
        # Compute token embeddings
        with torch.no_grad():
            model_output = self.model(**encoded_input)
        # Perform pooling
        sentence_embeddings = self._mean_pooling(
            model_output, encoded_input['attention_mask'])
        # Normalize embeddings
        sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
        return sentence_embeddings

    def get_similarity(
            self, 
            registry_outcomes:list[tuple[str,str]], 
            article_outcomes:list[tuple[str,str]]
        ) -> list[tuple[int,int,float]]:
        """For each outcome in true_dict, find the most similar outcome in compared_dict and return a mapping
        of all matchs , for each tuple : registry is the first index (at i=0); article is the second index (at i=1)
        and the third index (i=3) is the cosine similarity score"""
        connections = set()
        rembs = self._encode(registry_outcomes)
        aembs = self._encode(article_outcomes)
        cosines_scores = cos_sim(rembs, aembs)
        lines_max = torch.argmax(cosines_scores, dim=1)
        col_max = torch.argmax(cosines_scores, dim=0)
        remaining_cols = set(range(len(col_max)))
        for i in range(len(lines_max)):
            connection = (i, lines_max[i].item(), cosines_scores[i, lines_max[i]].item())
            remaining_cols.discard(lines_max[i].item())
            connections.add(connection)
        for j in remaining_cols:
            connection = (col_max[j].item(), j, cosines_scores[col_max[j], j].item())
            connections.add(connection)
        return connections
