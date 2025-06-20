import streamlit as st
import pandas as pd
import altair as alt

# Page configuration
st.set_page_config(page_title="Gene Expression Dashboard", layout="wide")

# Title and instructions
st.title("🧬 Gene Expression Explorer")
st.markdown("""
Upload your gene expression CSV file to explore expression levels across samples.
- Rows = samples  
- Columns = gene names (one column should be sample IDs or labels)
""")

# File uploader
uploaded_file = st.file_uploader("Upload CSV", type="csv")

# Main logic
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        
        # Check if there are at least 2 columns
        if df.shape[1] < 2:
            st.error("The file must contain at least one sample ID column and one gene expression column.")
        else:
            # Display a preview of the dataset
            st.success("File uploaded successfully.")
            st.dataframe(df.head())

            # Let user pick which column is the sample ID
            sample_col = st.selectbox("Select the sample ID column", df.columns)
            gene_cols = [col for col in df.columns if col != sample_col]

            # Let user select gene to visualize
            gene = st.selectbox("Select a gene to visualize", gene_cols)

            # Prepare data for plotting
            chart_data = df[[sample_col, gene]].copy()
            chart_data.columns = ["Sample", "Expression"]

            # Create bar chart
            chart = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X("Sample:N", sort=None),
                y="Expression:Q",
                tooltip=["Sample", "Expression"]
            ).properties(
                title=f"Expression of {gene}",
                width=800,
                height=400
            )

            st.altair_chart(chart, use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
else:
    st.info("Please upload a gene expression CSV file to begin.")
