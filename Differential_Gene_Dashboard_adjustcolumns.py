import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# Set page config
st.set_page_config(page_title="Differential Gene Expression Viewer", layout="wide")

# App title
st.title("🧬 Differential Gene Expression Dashboard")
st.markdown("""
Upload a CSV file containing differential gene expression results.  
Required data: gene name, log2 fold change, adjusted p-value (padj).  
Optionally: regulation column (Upregulated, Downregulated).
""")

def standardize_columns(df):
    # Lowercase, remove spaces and unify names
    rename_map = {}
    for col in df.columns:
        clean = col.strip().lower().replace(" ", "").replace("_", "")
        if "gene" in clean:
            rename_map[col] = "Gene"
        elif "log2fc" in clean or "log2foldchange" in clean:
            rename_map[col] = "log2FoldChange"
        elif "padj" in clean:
            rename_map[col] = "padj"
        elif "regulation" in clean:
            rename_map[col] = "regulation"
    df = df.rename(columns=rename_map)
    return df

# Upload file
uploaded_file = st.file_uploader("Upload your gene expression CSV file", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        # Clean and rename columns
        df.columns = df.columns.str.strip()
        df = standardize_columns(df)

        required_cols = {"Gene", "log2FoldChange", "padj"}
        if not required_cols.issubset(df.columns):
            st.error(f"Your file must include at least: {required_cols}. Current columns: {list(df.columns)}")
        else:
            st.success("File uploaded and processed successfully.")
            st.dataframe(df.head())

            # Convert to numeric safely
            df["log2FoldChange"] = pd.to_numeric(df["log2FoldChange"], errors="coerce")
            df["padj"] = pd.to_numeric(df["padj"], errors="coerce")

            # Calculate -log10(padj)
            df["-log10(padj)"] = df["padj"].apply(lambda x: -np.log10(x) if x > 0 else np.nan)

            # Set thresholds
            logfc_threshold = st.slider("Log2 Fold Change Threshold", 0.0, 5.0, 1.0, 0.1)
            padj_threshold = st.slider("Adjusted P-value Threshold", 0.0, 0.1, 0.05, 0.005)

            # Mark significance
            df["Significant"] = (
                (df["padj"] < padj_threshold) &
                (df["log2FoldChange"].abs() >= logfc_threshold)
            )

            # Optional regulation filter
            if "regulation" in df.columns:
                options = ["All"] + sorted(df["regulation"].dropna().unique())
                selected_reg = st.selectbox("Filter by Regulation", options)
                if selected_reg != "All":
                    df = df[df["regulation"] == selected_reg]

            # Volcano Plot
            st.subheader("Volcano Plot")
            chart = alt.Chart(df.dropna(subset=["-log10(padj)"])).mark_circle(size=60).encode(
                x=alt.X("log2FoldChange", title="log2 Fold Change"),
                y=alt.Y("-log10(padj)", title="-log10 Adjusted P-value"),
                color=alt.condition(
                    "datum.Significant == true",
                    alt.value("red"),
                    alt.value("gray")
                ),
                tooltip=["Gene", "log2FoldChange", "padj"]
            ).properties(width=800, height=500).interactive()

            st.altair_chart(chart, use_container_width=True)

            # Table of significant genes
            st.subheader("Significantly Differentially Expressed Genes")
            st.dataframe(df[df["Significant"]].sort_values("padj").reset_index(drop=True))

    except Exception as e:
        st.error(f"Error loading file: {e}")
else:
    st.info("Please upload your CSV file to begin.")
