# EvidenceMap – Submission Description

## Project Link
[https://github.com/souissighofrane32-droid/EvidenceMap](https://github.com/souissighofrane32-droid/EvidenceMap)

## Detailed Description

**EvidenceMap** is a personal health evidence graph tool that helps patients and caregivers make sense of messy, conflicting medical information.

### The Problem
People dealing with complex or chronic health conditions receive information from many sources: lab reports, different doctors, guidelines, research papers, and personal notes. These sources often conflict or leave important gaps. Existing AI health tools usually give direct answers (sometimes hallucinated) or require clean structured data that real patients never have. There is a clear need for a tool that makes the *structure of evidence and uncertainty* visible without pretending to be a doctor.

### What EvidenceMap Does
1. Accepts real-world messy documents (PDFs of labs, doctor notes, guidelines, personal notes).
2. Extracts medical claims, findings, lab values, treatments, and relationships using AI (with a rule-based fallback).
3. Builds an interactive visual evidence graph where every claim carries full provenance (source document, evidence class, confidence, original snippet).
4. Detects explicit contradictions and surfaces coverage gaps.
5. Answers questions strictly from the grounded evidence — it refuses to use external knowledge.

The tool is deliberately designed **not** to diagnose or recommend treatment. Its only job is to turn chaos into an auditable map so patients can have better conversations with clinicians.

### Technologies Used
- **Python 3**
- **Streamlit** – rapid interactive UI ideal for hackathon demos
- **NetworkX** – graph construction and analysis
- **Pyvis** – interactive force-directed visualization
- **PyMuPDF + pdfplumber** – robust PDF text extraction
- **OpenAI API (GPT-4o-mini)** – structured evidence extraction (optional; rule-based fallback included)
- **python-dotenv** – configuration management

### Architecture
- Document ingestion → text extraction
- LLM (or fallback) structured extraction of claims + relationships + evidence class
- Graph construction with provenance metadata
- Interactive visualization + contradiction detection + grounded Q&A

### Challenges Faced
- Extracting reliable structured claims from noisy real-world medical PDFs within a short time budget.
- Keeping the interactive graph readable as more documents are added.
- Designing clear UX that repeatedly communicates the tool never gives medical advice.
- Providing a useful experience even when the user has no API key (rule-based fallback).
- Balancing feature richness with the need for a stable, demoable MVP in limited time.

### How to Run
```bash
pip install -r requirements.txt
export OPENAI_API_KEY=your_key_here   # optional but recommended
streamlit run app/main.py
```

### Future Work
- Stronger multi-document contradiction reasoning
- Better OCR for scanned documents
- Export of clinician-ready evidence packs
- Private persistent storage
- Integration with lab / wearable data sources

---

**Disclaimer:** This is a hackathon prototype. It is not a medical device and must not be used for clinical decisions. Always consult qualified healthcare professionals.
