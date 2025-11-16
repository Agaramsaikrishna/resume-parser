import streamlit as st
import requests
import os
import json
import time
from typing import Any, Dict, List
from datetime import datetime, timezone

# ---------------------------------------------------
# Configuration
# ---------------------------------------------------
DEFAULT_API_BASE = "http://localhost:8000"
API_BASE = os.getenv("API_BASE", DEFAULT_API_BASE)

st.set_page_config(
    page_title="AI Resume Parser",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------
# Custom Styles
# ---------------------------------------------------
st.markdown("""
<style>
:root {
  --muted: #6b7280;
  --accent: #2563eb;
  --chip-bg: #1e293b;
  --chip-text: #fff;
}
.title { font-size:32px; font-weight:700; margin-bottom:0; }
.subtitle { color: var(--muted); font-size:16px; margin-top:2px; }
.card {
    padding:18px;
    border-radius:12px;
    background:white;
    box-shadow:0 6px 25px rgba(0,0,0,0.05);
    border:1px solid rgba(0,0,0,0.04);
    margin-bottom:14px;
}
.success {
    background: linear-gradient(90deg,#ecfdf5,#f0fdf4);
    border-left:4px solid #10b981;
    padding:12px;
    border-radius:8px;
    margin:16px 0;
}
.chip {
    display:inline-block;
    padding:7px 14px;
    margin:5px 6px 5px 0;
    border-radius:999px;
    background:var(--chip-bg);
    color:var(--chip-text);
    font-size:13px;
    font-weight:600;
}
.small-muted { color:var(--muted); font-size:13px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# Toast Helper
# ---------------------------------------------------
def toast(msg: str, time_ms: int = 1100):
    js = f"""
    <script>
      const el = document.createElement('div');
      el.innerText = "{msg}";
      el.style.position='fixed';
      el.style.right='20px';
      el.style.bottom='20px';
      el.style.padding='10px 14px';
      el.style.background='rgba(17,24,39,0.95)';
      el.style.color='white';
      el.style.borderRadius='8px';
      el.style.zIndex=9999;
      document.body.appendChild(el);
      setTimeout(()=>document.body.removeChild(el), {time_ms});
    </script>
    """
    st.components.v1.html(js)

# ---------------------------------------------------
# Render Components
# ---------------------------------------------------
def render_contact(contact: Dict[str, Any]):
    if not contact:
        st.write("_No contact info found_")
        return
    st.markdown("**Name:** " + str(contact.get("name", "—")))
    st.markdown("**Email:** " + str(contact.get("email", "—")))
    st.markdown("**Phone:** " + str(contact.get("phone", "—")))
    st.markdown("**Location:** " + str(contact.get("location", "—")))

def render_skills(skills: List[str]):
    if not skills:
        st.write("_No skills found_")
        return
    
    # Display skills in a simple list format
    st.markdown("**Skills:**")
    st.write(", ".join(skills))  # Comma-separated list

def render_experience(exps: List[Dict[str, Any]]):
    if not exps:
        st.write("_No experience found_")
        return
    for i, e in enumerate(exps):
        title = f"{e.get('role','Role')} • {e.get('company','Company')}"
        with st.expander(title, expanded=(i == 0)):
            st.markdown(f"**Role:** {e.get('role','—')}")
            st.markdown(f"**Company:** {e.get('company','—')}")
            st.markdown(f"**Duration:** {e.get('duration','—')}")
            resp = e.get("responsibilities") or []
            if resp:
                st.markdown("**Responsibilities:**")
                for r in resp:
                    st.markdown("- " + r)

def render_education(edus: List[Dict[str, Any]]):
    if not edus:
        st.write("_No education found_")
        return
    for ed in edus:
        st.markdown(f"**{ed.get('degree','')}** — {ed.get('institution','')} ({ed.get('year','')})")

# ---------------------------------------------------
# Sidebar (Settings)
# ---------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    with st.expander("API Settings", expanded=False):
        api_base_in = st.text_input("Backend API Base URL", value=API_BASE)
        os.environ["API_BASE"] = api_base_in

# ---------------------------------------------------
# Session State
# ---------------------------------------------------
st.session_state.setdefault("parsed", None)
st.session_state.setdefault("document_id", "")
st.session_state.setdefault("manual_fetch_id", "")

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.markdown("""
<div style="text-align:center;">
<h1 class="title">📄 AI Resume Parser</h1>
<p class="subtitle">Upload → Extract → Fetch by ID → Review JSON Output</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------
# TABS — Extract | Fetch
# ---------------------------------------------------
tab_extract, tab_fetch = st.tabs(["🔍 Extract Resume", "📥 Fetch by ID"])

# ---------------------------------------------------
# TAB 1 — Extract Resume
# ---------------------------------------------------
with tab_extract:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Upload Resume File")

    uploaded_file = st.file_uploader("Upload PDF/DOCX", type=["pdf", "docx"])
    extract_btn = st.button("🚀 Extract", use_container_width=True)

    if extract_btn:
        if not uploaded_file:
            st.error("Upload a file first!")
        else:
            try:
                start = time.time()
                with st.spinner("Extracting resume..."):
                    api_base = os.getenv("API_BASE", API_BASE)
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    resp = requests.post(f"{api_base}/api/upload", files=files, timeout=120)

                    if resp.status_code == 200:
                        res = resp.json()
                        st.session_state.parsed = None
                        st.session_state.document_id = res.get("document_id", "")
                        st.session_state.manual_fetch_id = ""
                        toast("Extraction successful")
                        end = time.time()
                        st.success(f"⏱ Processed in {end-start:.2f} seconds")

                        # ONLY show Document ID after extraction
                        st.markdown("### 🆔 Document ID")
                        st.code(st.session_state.document_id)

                    else:
                        st.error(f"Error {resp.status_code}: {resp.text}")

            except Exception as e:
                st.error(f"Request failed: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# TAB 2 — Fetch by ID
# ---------------------------------------------------
with tab_fetch:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Fetch a Previously Parsed Resume")

    doc_id_in = st.text_input("Enter Document ID", value=st.session_state.document_id or "", key="fetch_id")
    fetch_btn = st.button("📥 Fetch", use_container_width=True)

    if fetch_btn and doc_id_in.strip():
        try:
            with st.spinner("Fetching..."):
                api_base = os.getenv("API_BASE", API_BASE)
                resp = requests.get(f"{api_base}/api/resume/{doc_id_in}", timeout=60)

                if resp.status_code == 200:
                    st.session_state.parsed = resp.json()
                    st.session_state.document_id = doc_id_in
                    st.session_state.manual_fetch_id = doc_id_in
                    toast("Fetched successfully")
                else:
                    st.error(f"Error {resp.status_code}: {resp.text}")

        except Exception as e:
            st.error(f"Network error: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# RESULT SECTION (Only after Fetch)
# ---------------------------------------------------
if st.session_state.manual_fetch_id and st.session_state.parsed and st.session_state.document_id:
    data = st.session_state.parsed

    st.markdown("## 🧾 Parsed Resume")
    st.markdown('<div class="success"><b>Resume fetched successfully!</b></div>', unsafe_allow_html=True)

    # Clear Button
    if st.button("🧹 Clear Parsed Data", use_container_width=True):
        st.session_state.parsed = None
        st.session_state.document_id = ""
        st.session_state.manual_fetch_id = ""
        toast("Cleared")
        st.experimental_rerun()

    # Download JSON button
    st.download_button(
        label="💾 Download JSON",
        data=json.dumps(data, indent=2),
        file_name=f"resume_{st.session_state.document_id}.json",
        mime="application/json"
    )

    # Contact
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("👤 Contact")
    render_contact(data.get("contact"))
    st.markdown("</div>", unsafe_allow_html=True)

    # Summary
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📝 Summary")
    st.write(data.get("summary", "_No summary found_"))
    st.markdown("</div>", unsafe_allow_html=True)

    # Experience
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("💼 Experience")
    render_experience(data.get("experience", []))
    st.markdown("</div>", unsafe_allow_html=True)

    # Education + Skills
    st.markdown('<div class="card">', unsafe_allow_html=True)
    colA, colB = st.columns([2,1])
    with colA:
        st.subheader("🎓 Education")
        render_education(data.get("education", []))
    with colB:
        st.subheader("🛠 Skills")
        render_skills(data.get("skills", []))
    st.markdown("</div>", unsafe_allow_html=True)

    # SHOW RAW JSON
    st.markdown("### 📦 Raw JSON Output")
    with st.expander("Click to view JSON"):
        st.json(data)

    st.caption(f"Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
