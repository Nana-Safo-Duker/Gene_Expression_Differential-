import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Flexible Gene Expression Dashboard", layout="wide")

st.title("🧬 Adaptive Differential Gene Expression Viewer")
st.markdown("""
Upload a CSV file containing differential gene expression results.  
Then, select the correct columns for:
- Gene names  
- log2 Fold Change  
- Adjusted P-values  
(Optional: regulation for filtering)
""")

uploaded_file = st.file_uploader("Upload CSV file", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip()

        st.success("File uploaded successfully!")
        st.write("Preview of your data:")
        st.dataframe(df.head())

        # Column selectors
        all_cols = list(df.columns)

        gene_col = st.selectbox("Select Gene Name Column", all_cols)
        logfc_col = st.selectbox("Select Log2 Fold Change Column", all_cols)
        padj_col = st.selectbox("Select Adjusted P-value (padj) Column", all_cols)

        regulation_col = st.selectbox(
            "Optional: Select Regulation Column (Up/Downregulated)",
            ["None"] + all_cols
        )

        # Rename columns internally
        df = df.rename(columns={
            gene_col: "Gene",
            logfc_col: "log2FoldChange",
            padj_col: "padj"
        })

        if regulation_col != "None":
            df = df.rename(columns={regulation_col: "regulation"})

        # Convert to numeric
        df["log2FoldChange"] = pd.to_numeric(df["log2FoldChange"], errors="coerce")
        df["padj"] = pd.to_numeric(df["padj"], errors="coerce")
        df["-log10(padj)"] = df["padj"].apply(lambda x: -np.log10(x) if x > 0 else np.nan)

        # Set thresholds
        st.markdown("### Filter Options")
        logfc_threshold = st.slider("Log2 Fold Change Threshold", 0.0, 5.0, 1.0, 0.1)
        padj_threshold = st.slider("Adjusted P-value Threshold", 0.0, 0.1, 0.05, 0.005)

        # Define significance
        df["Significant"] = (
            (df["padj"] < padj_threshold) &
            (df["log2FoldChange"].abs() >= logfc_threshold)
        )

        # Optional regulation filter
        if "regulation" in df.columns:
            values = ["All"] + sorted(df["regulation"].dropna().unique())
            selected = st.selectbox("Filter by Regulation", values)
            if selected != "All":
                df = df[df["regulation"] == selected]

        # Volcano Plot
        st.markdown("### Volcano Plot")
        volcano = alt.Chart(df.dropna(subset=["-log10(padj)"])).mark_circle(size=60).encode(
            x=alt.X("log2FoldChange", title="log2 Fold Change"),
            y=alt.Y("-log10(padj)", title="-log10 Adjusted P-value"),
            color=alt.condition(
                "datum.Significant == true",
                alt.value("red"),
                alt.value("gray")
            ),
            tooltip=["Gene", "log2FoldChange", "padj"]
        ).properties(width=800, height=500).interactive()

        st.altair_chart(volcano, use_container_width=True)

        # Table of significant genes
        st.markdown("### Significant Genes")
        st.dataframe(df[df["Significant"]].sort_values("padj").reset_index(drop=True))

    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Please upload a CSV file to begin.")
