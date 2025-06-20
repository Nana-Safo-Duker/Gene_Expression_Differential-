import streamlit as st
import pandas as pd
import altair as alt

# Set page config
st.set_page_config(page_title="Differential Gene Expression Viewer", layout="wide")

# App title
st.title("🧬 Differential Gene Expression Dashboard")
st.markdown("""
Upload a CSV file containing differential gene expression results.  
The file should have columns: `Gene`, `log2FoldChange`, `padj`, and optionally `regulation`.
""")

# Upload file
uploaded_file = st.file_uploader("Upload your gene expression CSV file", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        # Ensure required columns exist
        required_cols = {"Gene", "log2FoldChange", "padj"}
        if not required_cols.issubset(df.columns):
            st.error(f"Your file must contain the following columns: {required_cols}")
        else:
            st.success("File uploaded successfully!")
            st.dataframe(df.head())

            # Convert values safely
            df["log2FoldChange"] = pd.to_numeric(df["log2FoldChange"], errors="coerce")
            df["padj"] = pd.to_numeric(df["padj"], errors="coerce")

            # Volcano plot settings
            logfc_threshold = st.slider("Log2 Fold Change Threshold", 0.0, 5.0, 1.0, 0.1)
            padj_threshold = st.slider("Adjusted P-value Threshold", 0.0, 0.1, 0.05, 0.005)

            # Filtered dataframe
            df["-log10(padj)"] = -df["padj"].apply(lambda x: np.log10(x) if x > 0 else None)
            df["Significant"] = (
                (df["padj"] < padj_threshold) & 
                (abs(df["log2FoldChange"]) >= logfc_threshold)
            )

            # Volcano plot
            st.subheader("Volcano Plot")

            chart = alt.Chart(df).mark_circle(size=60).encode(
                x="log2FoldChange",
                y="-log10(padj)",
                color=alt.condition(
                    "datum.Significant == true",
                    alt.value("red"),
                    alt.value("gray")
                ),
                tooltip=["Gene", "log2FoldChange", "padj"]
            ).properties(
                width=800,
                height=500
            ).interactive()

            st.altair_chart(chart, use_container_width=True)

            # Optional: Show table of significant genes
            st.subheader("Significantly Differentially Expressed Genes")
            st.write(df[df["Significant"]].sort_values("padj").reset_index(drop=True))

    except Exception as e:
        st.error(f"Error loading file: {e}")
else:
    st.info("Please upload your CSV file to begin.")
