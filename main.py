"""
EvidenceMap - Personal Health Evidence Graph
Hackathon MVP
"""

import streamlit as st
import os
import uuid
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from document_processor import process_document
from extractor import extract_from_text, extract_fallback
from graph_manager import EvidenceGraph

# Page config
st.set_page_config(
    page_title="EvidenceMap – Health Evidence Graph",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state
if "graph" not in st.session_state:
    st.session_state.graph = EvidenceGraph()
if "processed_files" not in st.session_state:
    st.session_state.processed_files = []

UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def main():
    st.title("🩺 EvidenceMap")
    st.markdown("**Personal Health Evidence Graph** — Turn messy medical documents into a clear, provenance-tracked evidence map.")
    
    with st.expander("What this tool does (and does not do)", expanded=False):
        st.markdown("""
        **Does:**
        - Extracts medical claims, findings, labs, treatments from your documents
        - Builds an interactive evidence graph with full provenance
        - Highlights relationships and potential contradictions
        - Lets you ask questions grounded only in the uploaded evidence
        
        **Does NOT:**
        - Diagnose or recommend treatments
        - Replace medical professionals
        - Store your data outside this session (unless you save)
        """)
    
    # Sidebar
    with st.sidebar:
        st.header("Controls")
        api_key = st.text_input("OpenAI API Key (optional)", type="password", 
                                help="Leave empty to use rule-based fallback extraction")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        st.divider()
        if st.button("Clear Graph", type="secondary"):
            st.session_state.graph = EvidenceGraph()
            st.session_state.processed_files = []
            st.rerun()
        
        st.divider()
        stats = st.session_state.graph.get_stats()
        st.metric("Documents", stats["documents"])
        st.metric("Claims", stats["claims"])
        st.metric("Nodes", stats["nodes"])
        st.metric("Edges", stats["edges"])
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📄 Upload & Extract", "🕸️ Evidence Graph", "⚠️ Contradictions & Gaps", "❓ Ask the Graph"])
    
    with tab1:
        st.subheader("Upload Documents")
        st.caption("PDF lab reports, doctor notes, guidelines, papers, personal notes (.pdf, .txt, .md)")
        
        uploaded_files = st.file_uploader(
            "Drop files here",
            type=["pdf", "txt", "md"],
            accept_multiple_files=True
        )
        
        if uploaded_files and st.button("Process Documents", type="primary"):
            progress = st.progress(0)
            status = st.empty()
            
            for i, uf in enumerate(uploaded_files):
                status.text(f"Processing {uf.name}...")
                
                # Save file
                file_id = str(uuid.uuid4())[:8]
                save_path = UPLOAD_DIR / f"{file_id}_{uf.name}"
                with open(save_path, "wb") as f:
                    f.write(uf.getbuffer())
                
                # Extract text
                text, doc_type = process_document(str(save_path))
                
                if not text or len(text) < 30:
                    st.warning(f"Could not extract useful text from {uf.name}")
                    continue
                
                # Extract evidence
                if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "sk-placeholder":
                    extraction = extract_from_text(text, file_id)
                else:
                    extraction = extract_fallback(text, file_id)
                    st.info("Using rule-based fallback (add OpenAI key for better extraction)")
                
                # Add to graph
                st.session_state.graph.add_extraction(extraction, uf.name)
                st.session_state.processed_files.append({
                    "name": uf.name,
                    "claims": len(extraction.get("claims", [])),
                    "id": file_id
                })
                
                progress.progress((i + 1) / len(uploaded_files))
            
            status.text("Done!")
            st.success(f"Processed {len(uploaded_files)} document(s)")
            st.rerun()
        
        if st.session_state.processed_files:
            st.subheader("Processed Files")
            for f in st.session_state.processed_files:
                st.write(f"• **{f['name']}** — {f['claims']} claims extracted")
    
    with tab2:
        st.subheader("Interactive Evidence Graph")
        
        stats = st.session_state.graph.get_stats()
        if stats["nodes"] == 0:
            st.info("Upload and process documents first to build the graph.")
        else:
            try:
                from pyvis.network import Network
                import streamlit.components.v1 as components
                
                net = Network(height="650px", width="100%", directed=True, notebook=False)
                net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=150)
                
                graph_data = st.session_state.graph.to_pyvis_json()
                
                for node in graph_data["nodes"]:
                    net.add_node(
                        node["id"],
                        label=node["label"],
                        title=node.get("title", ""),
                        color=node.get("color", "#9B9B9B"),
                        size=node.get("size", 15)
                    )
                
                for edge in graph_data["edges"]:
                    net.add_edge(
                        edge["source"],
                        edge["target"],
                        title=edge.get("title", ""),
                        label=edge.get("label", "")
                    )
                
                html_path = DATA_DIR / "graph.html"
                net.save_graph(str(html_path))
                
                with open(html_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                
                components.html(html_content, height=700, scrolling=True)
                
                st.caption("Node colors: Blue=Document · Green=Claim · Orange=Entity · Red=Diagnosis · Purple=Treatment · etc.")
            except Exception as e:
                st.error(f"Visualization error: {e}")
                st.json(st.session_state.graph.get_stats())
    
    with tab3:
        st.subheader("Contradictions & Gaps")
        
        contradictions = st.session_state.graph.detect_contradictions()
        
        if contradictions:
            st.warning(f"Found {len(contradictions)} potential contradiction(s)")
            for c in contradictions:
                st.markdown(f"- **{c['source_label']}** ⟷ **{c['target_label']}** ({c['type']})")
        else:
            st.info("No explicit contradictions detected yet. Add more documents or use LLM extraction for richer relationship detection.")
        
        st.divider()
        st.subheader("Current Evidence Coverage")
        stats = st.session_state.graph.get_stats()
        col1, col2, col3 = st.columns(3)
        col1.metric("Documents", stats["documents"])
        col2.metric("Claims Extracted", stats["claims"])
        col3.metric("Entities", stats["entities"])
        
        if stats["claims"] > 0:
            st.markdown("**Claim types present:**")
            types = {}
            for c in st.session_state.graph.claims.values():
                t = c.get("type", "other")
                types[t] = types.get(t, 0) + 1
            st.write(types)
    
    with tab4:
        st.subheader("Ask the Evidence Graph")
        st.caption("Questions are answered only from the uploaded evidence. No external knowledge is used.")
        
        question = st.text_input("Your question about the evidence")
        
        if question and st.button("Query"):
            if st.session_state.graph.get_stats()["claims"] == 0:
                st.warning("No evidence loaded yet.")
            else:
                # Simple retrieval for MVP
                relevant = []
                q_lower = question.lower()
                for cid, claim in st.session_state.graph.claims.items():
                    if any(w in claim["text"].lower() for w in q_lower.split() if len(w) > 3):
                        relevant.append(claim)
                
                if not relevant:
                    st.info("No directly matching claims found in the current evidence graph.")
                else:
                    st.markdown("### Grounded Evidence Found")
                    for r in relevant[:8]:
                        with st.container():
                            st.markdown(f"**[{r['type']}]** {r['text']}")
                            st.caption(f"Source: {r['filename']} · Evidence class: {r['evidence_class']} · Confidence: {r['confidence']:.2f}")
                            if r.get("source_snippet"):
                                st.code(r["source_snippet"], language=None)
                            st.divider()


if __name__ == "__main__":
    main()
