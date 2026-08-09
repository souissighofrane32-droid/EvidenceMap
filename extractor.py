"""
Evidence extraction from documents using LLM.
Returns structured claims with provenance.
"""

import json
import os
from typing import List, Dict, Any
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "sk-placeholder"))

EXTRACTION_PROMPT = """You are a medical evidence extraction specialist.
Given the following document text, extract key medical claims, findings, symptoms, diagnoses, treatments, lab results, and relationships.

Return ONLY valid JSON in this exact format:
{
  "claims": [
    {
      "id": "c1",
      "text": "clear claim statement",
      "type": "finding|diagnosis|treatment|lab|symptom|guideline|other",
      "evidence_class": "RCT|observational|guideline|lab_result|expert_opinion|patient_report|anecdote|unknown",
      "confidence": 0.0-1.0,
      "entities": ["entity1", "entity2"],
      "source_snippet": "exact short quote from text"
    }
  ],
  "relationships": [
    {
      "source": "entity or claim id",
      "target": "entity or claim id",
      "relation": "supports|contradicts|causes|treats|associated_with|indicates|part_of",
      "confidence": 0.0-1.0
    }
  ]
}

Be strict. Only extract what is clearly stated. Prefer precision over recall.
Document text:
"""

def extract_from_text(text: str, doc_id: str, max_chars: int = 12000) -> Dict[str, Any]:
    """Extract structured evidence from document text."""
    if not text or len(text.strip()) < 20:
        return {"claims": [], "relationships": [], "doc_id": doc_id}

    truncated = text[:max_chars]
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You extract structured medical evidence. Reply only with valid JSON."},
                {"role": "user", "content": EXTRACTION_PROMPT + truncated}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        data["doc_id"] = doc_id
        return data
    except Exception as e:
        print(f"Extraction error: {e}")
        return {"claims": [], "relationships": [], "doc_id": doc_id, "error": str(e)}


def extract_fallback(text: str, doc_id: str) -> Dict[str, Any]:
    """Simple rule-based fallback when no API key is available."""
    claims = []
    # Very basic keyword heuristic for demo without API
    keywords = {
        "diagnosis": ["diagnosed", "diagnosis", "condition", "disease"],
        "lab": ["mg/dl", "mmol", "result", "level", "hemoglobin", "glucose", "creatinine"],
        "treatment": ["prescribed", "treatment", "therapy", "medication", "dose"],
        "symptom": ["symptom", "pain", "fatigue", "nausea", "reported"]
    }
    
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if len(s.strip()) > 30]
    for i, sent in enumerate(sentences[:15]):
        sent_lower = sent.lower()
        claim_type = "other"
        for t, kws in keywords.items():
            if any(k in sent_lower for k in kws):
                claim_type = t
                break
        claims.append({
            "id": f"c{i+1}",
            "text": sent[:200],
            "type": claim_type,
            "evidence_class": "unknown",
            "confidence": 0.4,
            "entities": [],
            "source_snippet": sent[:120]
        })
    
    return {"claims": claims, "relationships": [], "doc_id": doc_id}
