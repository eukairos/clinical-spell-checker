"""
Masked Language Model wrapper for BioClinical-ModernBERT.
Provides contextual spell-checking via pseudo-log-likelihood scoring.
"""

import logging
import math
import time
from typing import List

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForMaskedLM

logger = logging.getLogger(__name__)


class ClinicalMLM:
    """Wraps any HuggingFace masked LM as a contextual spell scorer."""

    def __init__(self, model_name: str, device: str = "auto"):
        logger.info(f"Loading model: {model_name}")
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForMaskedLM.from_pretrained(model_name)

        if device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        self.model.to(self.device)
        self.model.eval()

        self.mask_token = self.tokenizer.mask_token
        self.mask_id = self.tokenizer.mask_token_id
        self.id_to_token = {v: k for k, v in self.tokenizer.get_vocab().items()}

        logger.info(f"Model loaded on {self.device} | vocab size: {len(self.tokenizer)}")

    @torch.no_grad()
    def predict_mask(self, context_before: str, context_after: str, top_k: int = 20) -> List[dict]:
        """Get top-k MLM predictions for a single [MASK] position."""
        text = f"{context_before} {self.mask_token} {context_after}".strip()
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(self.device)

        input_ids = inputs["input_ids"][0]
        mask_positions = (input_ids == self.mask_id).nonzero(as_tuple=True)[0]
        if len(mask_positions) == 0:
            return []

        outputs = self.model(**inputs)
        logits = outputs.logits[0, mask_positions[0].item(), :]
        probs = F.softmax(logits, dim=-1)
        topk_probs, topk_ids = probs.topk(top_k)

        results = []
        for prob, tid in zip(topk_probs.tolist(), topk_ids.tolist()):
            token_str = self.id_to_token.get(tid, "")
            clean = token_str.replace("##", "").replace("Ġ", "").replace("▁", "").strip()
            if clean and prob > 1e-5:
                results.append({
                    "token": clean, "token_id": tid,
                    "probability": round(prob, 6),
                    "is_whole_word": not token_str.startswith("##"),
                })
        return results

    @torch.no_grad()
    def score_candidate(self, context_before: str, candidate: str, context_after: str) -> float:
        """
        Score a candidate word using pseudo-log-likelihood (PLL).
        Handles multi-subword candidates correctly.
        """
        candidate_ids = self.tokenizer.encode(candidate, add_special_tokens=False)
        if not candidate_ids:
            return 0.0

        n_subwords = len(candidate_ids)
        full_text = f"{context_before} {candidate} {context_after}".strip()
        inputs = self.tokenizer(full_text, return_tensors="pt", truncation=True, max_length=512).to(self.device)
        input_ids = inputs["input_ids"][0].clone()

        # Find candidate subwords in tokenized sequence
        ids_list = input_ids.tolist()
        candidate_start = None
        for i in range(len(ids_list) - n_subwords + 1):
            if ids_list[i:i + n_subwords] == candidate_ids:
                candidate_start = i
                break

        if candidate_start is None:
            return self._score_single_mask(context_before, candidate, context_after)

        # PLL: mask each subword one at a time
        log_prob_sum = 0.0
        for offset in range(n_subwords):
            pos = candidate_start + offset
            masked_ids = input_ids.clone()
            masked_ids[pos] = self.mask_id
            masked_inputs = {"input_ids": masked_ids.unsqueeze(0), "attention_mask": inputs["attention_mask"]}

            outputs = self.model(**masked_inputs)
            logits = outputs.logits[0, pos, :]
            probs = F.softmax(logits, dim=-1)
            target_prob = probs[candidate_ids[offset]].item()
            log_prob_sum += math.log(target_prob) if target_prob > 0 else -20.0

        return round(math.exp(log_prob_sum / n_subwords), 6)

    @torch.no_grad()
    def _score_single_mask(self, context_before: str, candidate: str, context_after: str) -> float:
        """Fallback scoring via single [MASK]."""
        text = f"{context_before} {self.mask_token} {context_after}".strip()
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(self.device)
        input_ids = inputs["input_ids"][0]
        mask_positions = (input_ids == self.mask_id).nonzero(as_tuple=True)[0]
        if len(mask_positions) == 0:
            return 0.0
        outputs = self.model(**inputs)
        probs = F.softmax(outputs.logits[0, mask_positions[0].item(), :], dim=-1)
        candidate_ids = self.tokenizer.encode(candidate, add_special_tokens=False)
        return round(probs[candidate_ids[0]].item(), 6) if candidate_ids else 0.0

    def predict_for_oov(self, context_before: str, oov_token: str, context_after: str,
                        candidates: List[dict], top_k: int = 15) -> dict:
        """Full prediction pipeline for one OOV token."""
        t0 = time.time()
        mlm_preds = self.predict_mask(context_before, context_after, top_k=top_k)

        candidate_scores = []
        for cand in candidates:
            word = cand.get("word", cand) if isinstance(cand, dict) else cand
            dist = cand.get("dist", 1) if isinstance(cand, dict) else 1
            prob = self.score_candidate(context_before, word, context_after)
            candidate_scores.append({"word": word, "probability": prob, "edit_distance": dist})

        original_score = self.score_candidate(context_before, oov_token, context_after)

        all_scored = list(candidate_scores)
        for pred in mlm_preds:
            if pred["is_whole_word"] and pred["token"].isalpha() and len(pred["token"]) >= 3:
                if not any(cs["word"].lower() == pred["token"].lower() for cs in all_scored):
                    all_scored.append({"word": pred["token"], "probability": pred["probability"], "edit_distance": -1})

        all_scored.sort(key=lambda x: -x["probability"])
        best = None
        for cs in all_scored:
            if cs["probability"] > original_score and cs["word"].lower() != oov_token.lower():
                best = {"word": cs["word"], "probability": cs["probability"]}
                break

        return {
            "mlm_top_predictions": mlm_preds[:10],
            "candidate_scores": all_scored[:15],
            "original_score": original_score,
            "best_correction": best,
            "confidence": round(best["probability"] if best else original_score, 4),
            "elapsed_seconds": round(time.time() - t0, 3),
        }
