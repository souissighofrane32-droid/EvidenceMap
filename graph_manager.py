"""
Evidence Graph manager using NetworkX.
Stores claims, entities, relationships with full provenance.
"""

import networkx as nx
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import uuid


class EvidenceGraph:
    def __init__(self):
        self.G = nx.DiGraph()
        self.documents: Dict[str, Dict] = {}
        self.claims: Dict[str, Dict] = {}
    
    def add_document(self, doc_id: str, filename: str, text_preview: str):
        self.documents[doc_id] = {
            "id": doc_id,
            "filename": filename,
            "preview": text_preview[:300]
        }
        self.G.add_node(doc_id, type="document", label=filename, group="document")
    
    def add_extraction(self, extraction: Dict[str, Any], filename: str):
        doc_id = extraction.get("doc_id") or str(uuid.uuid4())[:8]
        
        if doc_id not in self.documents:
            self.add_document(doc_id, filename, "")
        
        # Add claims
        for claim in extraction.get("claims", []):
            claim_id = f"{doc_id}_{claim.get('id', str(uuid.uuid4())[:6])}"
            claim_data = {
                "id": claim_id,
                "text": claim.get("text", ""),
                "type": claim.get("type", "other"),
                "evidence_class": claim.get("evidence_class", "unknown"),
                "confidence": float(claim.get("confidence", 0.5)),
                "source_snippet": claim.get("source_snippet", ""),
                "doc_id": doc_id,
                "filename": filename,
                "entities": claim.get("entities", [])
            }
            self.claims[claim_id] = claim_data
            
            # Node for the claim
            label = claim_data["text"][:60] + ("..." if len(claim_data["text"]) > 60 else "")
            self.G.add_node(
                claim_id,
                type="claim",
                label=label,
                full_text=claim_data["text"],
                evidence_class=claim_data["evidence_class"],
                confidence=claim_data["confidence"],
                claim_type=claim_data["type"],
                group=claim_data["type"],
                title=f"{claim_data['type']} | {claim_data['evidence_class']} | conf={claim_data['confidence']:.2f}"
            )
            
            # Link claim to document
            self.G.add_edge(doc_id, claim_id, relation="contains", weight=1.0)
            
            # Add entity nodes
            for ent in claim.get("entities", []):
                if not ent or len(ent) < 2:
                    continue
                ent_id = f"ent_{ent.lower().replace(' ', '_')[:40]}"
                if not self.G.has_node(ent_id):
                    self.G.add_node(ent_id, type="entity", label=ent, group="entity")
                self.G.add_edge(claim_id, ent_id, relation="mentions", weight=0.7)
        
        # Add relationships
        for rel in extraction.get("relationships", []):
            src = rel.get("source")
            tgt = rel.get("target")
            relation = rel.get("relation", "associated_with")
            conf = float(rel.get("confidence", 0.5))
            
            # Try to resolve to existing nodes
            src_id = self._resolve_node(src, doc_id)
            tgt_id = self._resolve_node(tgt, doc_id)
            
            if src_id and tgt_id and src_id != tgt_id:
                self.G.add_edge(src_id, tgt_id, relation=relation, weight=conf, confidence=conf)
    
    def _resolve_node(self, name: str, doc_id: str) -> Optional[str]:
        if not name:
            return None
        # Direct claim id
        candidate = f"{doc_id}_{name}"
        if self.G.has_node(candidate):
            return candidate
        # Entity
        ent_id = f"ent_{name.lower().replace(' ', '_')[:40]}"
        if self.G.has_node(ent_id):
            return ent_id
        # Fuzzy search in claims
        name_l = name.lower()
        for cid, cdata in self.claims.items():
            if name_l in cdata["text"].lower() or name_l in str(cdata.get("entities", [])).lower():
                return cid
        return None
    
    def detect_contradictions(self) -> List[Dict]:
        """Find potential contradictions (edges labeled contradicts + keyword heuristic)."""
        contradictions = []
        
        # Explicit contradict edges
        for u, v, data in self.G.edges(data=True):
            if data.get("relation") == "contradicts":
                contradictions.append({
                    "source": u,
                    "target": v,
                    "type": "explicit",
                    "source_label": self.G.nodes[u].get("label", u),
                    "target_label": self.G.nodes[v].get("label", v)
                })
        
        # Simple heuristic: same entities with opposing claim types
        # (kept lightweight for MVP)
        return contradictions
    
    def get_stats(self) -> Dict:
        return {
            "documents": len(self.documents),
            "claims": len(self.claims),
            "nodes": self.G.number_of_nodes(),
            "edges": self.G.number_of_edges(),
            "entities": sum(1 for n, d in self.G.nodes(data=True) if d.get("type") == "entity")
        }
    
    def to_pyvis_json(self) -> Dict:
        """Export for visualization."""
        nodes = []
        edges = []
        
        color_map = {
            "document": "#4A90E2",
            "claim": "#7ED321",
            "entity": "#F5A623",
            "finding": "#50E3C2",
            "diagnosis": "#D0021B",
            "treatment": "#9013FE",
            "lab": "#BD10E0",
            "symptom": "#F8E71C",
            "guideline": "#417505",
            "other": "#9B9B9B"
        }
        
        for node, data in self.G.nodes(data=True):
            ntype = data.get("type", "other")
            group = data.get("group", ntype)
            color = color_map.get(group, color_map.get(ntype, "#9B9B9B"))
            
            nodes.append({
                "id": node,
                "label": data.get("label", node)[:50],
                "title": data.get("title", data.get("full_text", node)),
                "color": color,
                "group": group,
                "size": 25 if ntype == "document" else (18 if ntype == "entity" else 15)
            })
        
        for u, v, data in self.G.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "label": data.get("relation", ""),
                "title": f"{data.get('relation', '')} (conf={data.get('confidence', data.get('weight', 0)):.2f})"
            })
        
        return {"nodes": nodes, "edges": edges}
    
    def save(self, path: str):
        data = {
            "documents": self.documents,
            "claims": self.claims,
            "graph": nx.node_link_data(self.G)
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    
    def load(self, path: str):
        if not Path(path).exists():
            return
        with open(path) as f:
            data = json.load(f)
        self.documents = data.get("documents", {})
        self.claims = data.get("claims", {})
        self.G = nx.node_link_graph(data.get("graph", {"nodes": [], "links": []}))
