import json
import textwrap
import streamlit as st
from classifier import classify_po

st.set_page_config(page_title="PO Category Classifier", layout="centered")

st.title("PO L1-L2-L3 Classifier")
st.caption("Paste a purchase order line and get a structured category prediction.")

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.subheader("Tips")
    st.write("Be specific: include material, service, or scope where possible.")
    st.write("Add supplier if it helps disambiguate the category.")
    st.subheader("Examples")
    example_choice = st.radio(
        "Pick a sample",
        [
            "Annual HVAC preventive maintenance for main office",
            "Laptop procurement - 25 units, 16GB RAM",
            "Catering services for quarterly town hall",
            "Office supplies: paper, pens, folders",
            "Forklift rental for warehouse",
        ],
        index=0,
    )
    if st.session_state.history:
        st.subheader("Recent")
        for item in st.session_state.history[:5]:
            st.code(item, language="text")

po_description = st.text_area(
    "PO Description",
    height=140,
    placeholder="e.g., Annual HVAC preventive maintenance for main office",
    value=example_choice,
)
supplier = st.text_input(
    "Supplier (optional)",
    placeholder="e.g., Acme Facilities",
)

col1, col2 = st.columns([1, 1])
with col1:
    classify_clicked = st.button("Classify", type="primary")
with col2:
    if st.button("Clear"):
        st.session_state.history = []
        st.experimental_rerun()

if classify_clicked:
    if not po_description.strip():
        st.warning("Please enter a PO description.")
    else:
        with st.spinner("Classifying..."):
            result = classify_po(po_description, supplier)

        st.session_state.history.insert(0, po_description.strip())
        st.session_state.history = st.session_state.history[:10]

        try:
            parsed = json.loads(result)
        except Exception:
            parsed = None

        if parsed is None:
            st.error("Model returned non-JSON output.")
            with st.expander("Raw response"):
                st.text(result)
        else:
            st.success("Classification complete.")
            st.json(parsed)

            pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
            col3, col4 = st.columns([1, 1])
            with col3:
                st.download_button(
                    "Download JSON",
                    data=pretty,
                    file_name="classification.json",
                    mime="application/json",
                )
            with col4:
                st.code(textwrap.shorten(pretty.replace("\n", " "), width=120), language="text")
