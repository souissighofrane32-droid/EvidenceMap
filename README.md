# EvidenceMap – Personal Health Evidence Graph

**Hackathon Project**

EvidenceMap turns the messy reality of medical documents (lab reports, doctor notes, guidelines, papers, personal tracking) into a living, interactive evidence graph with strict provenance.

## Problem

Patients and caregivers dealing with complex or chronic conditions are overwhelmed by conflicting information from different sources. Existing tools either give black-box AI answers or require perfectly structured data. There is almost no patient-facing tool that makes the *structure of evidence and uncertainty* visible.

## Solution

1. Upload mixed real-world documents (PDF, text, notes)
2. Automatic extraction of medical claims, findings, labs, treatments, and relationships
3. Interactive visual evidence graph with full provenance (source document + evidence class + confidence)
4. Explicit contradiction and gap detection
5. Questions answered strictly from the grounded evidence (no hallucinations from external knowledge)

**Important:** EvidenceMap does **not** diagnose or recommend treatments. It only maps what the documents actually say and where they conflict or leave gaps.

## Tech Stack

- **Frontend / UI:** Streamlit
- **Graph:** NetworkX + Pyvis
- **Document processing:** PyMuPDF + pdfplumber
- **AI Extraction:** OpenAI GPT-4o-mini (with rule-based fallback)
- **Language:** Python 3.10+

## How to Run

```bash
# Clone / enter project
cd EvidenceMap

# Install dependencies
pip install -r requirements.txt

# (Optional) set API key for better extraction
export OPENAI_API_KEY=sk-...

# Run
streamlit run app/main.py
```

## Project Structure

```
EvidenceMap/
├── app/
│   ├── main.py              # Streamlit UI
│   ├── document_processor.py
│   ├── extractor.py
│   └── graph_manager.py
├── uploads/                 # Uploaded files
├── data/                    # Graph exports
├── requirements.txt
└── README.md
```

## Key Features Implemented

- Multi-document upload (PDF + text)
- LLM-powered structured evidence extraction (claims + relationships + evidence class)
- Interactive force-directed evidence graph
- Provenance tracking on every claim
- Contradiction detection
- Grounded question answering over the graph
- Rule-based fallback when no API key is present

## Challenges Faced

- Balancing extraction quality vs. speed for a hackathon demo
- Making the graph readable when many documents are uploaded
- Designing the UI so it is clear the tool never gives medical advice
- Handling noisy real-world PDFs with varying quality

## Future Improvements

- Better OCR for scanned documents
- Persistent user accounts + private storage
- Stronger contradiction reasoning with LLM
- Export of evidence packs for clinicians
- Integration with wearable / lab data APIs

## Disclaimer

This is a prototype built for a hackathon. It is **not** a medical device and must not be used for clinical decision-making. Always consult qualified healthcare professionals.
