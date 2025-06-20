import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Flexible Gene Expression Dashboard", layout="wide")

st.title("🧬 Adaptive Differential Gene Expression Viewer")
st.markdown("""
Upload your gene expression CSV file and select the correct columns for:
- Gene names  
- Log2 Fold Change  
- Adjusted P-values  
(Optional: regulation column for filtering)
""")

uploaded_file = st.file_uploader("Upload CSV file", type="csv")

if uploaded_file:
    try:
        # Load and preview the uploaded CSV
        df_raw = pd.read_csv(uploaded_file)
        df_raw.columns = df_raw.columns.str.strip()

        st.success("File uploaded successfully.")
        st.write("Here is a preview of your data:")
        st.dataframe(df_raw.head())

        all_cols = list(df_raw.columns)

        # Let user select key columns
        gene_col = st.selectbox("Select Gene Name Column", all_cols)
        logfc_col = st.selectbox("Select Log2 Fold Change Column", all_cols)
        padj_col = st.selectbox("Select Adjusted P-value (padj) Column", all_cols)
        regulation_col = st.selectbox("Optional: Select Regulation Column", ["None"] + all_cols)

        # Create a copy and rename columns for consistency
        df = df_raw.copy()
        df.rename(columns={
            gene_col: "Gene",
            logfc_col: "log2FoldChange",
            padj_col: "padj"
        }, inplace=True)

        if regulation_col != "None":
            df.rename(columns={regulation_col: "regulation"}, inplace=True)

        # Convert numerical columns to proper types
        df["log2FoldChange"] = pd.to_numeric(df["log2FoldChange"], errors="coerce")
        df["padj"] = pd.to_numeric(df["padj"], errors="coerce")
        df = df.dropna(subset=["log2FoldChange", "padj"])
        df["-log10(padj)"] = -np.log10(df["padj"])

        # Add user-controlled thresholds
        st.markdown("### 🔧 Filter Options")
        logfc_threshold = st.slider("Log2 Fold Change Threshold", 0.0, 5.0, 1.0, 0.1)
        padj_threshold = st.slider("Adjusted P-value Threshold", 0.0, 0.1, 0.05, 0.005)

        df["Significant"] = (
            (df["padj"] < padj_threshold) &
            (df["log2FoldChange"].abs() >= logfc_threshold)
        )

        # Optional regulation filter
        if "regulation" in df.columns:
            unique_regs = df["regulation"].dropna().unique().tolist()
            regulation_filter = st.selectbox("Filter by Regulation", ["All"] + unique_regs)
            if regulation_filter != "All":
                df = df[df["regulation"] == regulation_filter]

        # 🔬 Volcano Plot
        st.markdown("### Volcano Plot")

        if df.shape[0] > 0:
            volcano = alt.Chart(df).mark_circle(size=60).encode(
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
        else:
            st.warning("No data to plot. Try relaxing your filters.")

        # 🧬 Table of significant genes
        st.markdown("### Significant Genes")
        sig_genes = df[df["Significant"]].sort_values("padj")
        st.dataframe(sig_genes.reset_index(drop=True))

    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Please upload your CSV file to get started.")
