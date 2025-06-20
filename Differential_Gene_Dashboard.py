import streamlit as st
import pandas as pd
import altair as alt

st.title("🧬 Gene Expression Dashboard")

uploaded_file = st.file_uploader("Upload a CSV file with gene expression data", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Preview of your data:", df.head())

    gene = st.selectbox("Select a gene", df.columns[1:])  # skip first column if it's 'Sample'

    chart = alt.Chart(df).mark_bar().encode(
        x='Sample',
        y=gene,
        tooltip=['Sample', gene]
    ).properties(
        title=f'Expression of {gene} across samples'
    )

    st.altair_chart(chart, use_container_width=True)
else:
    st.info("Please upload a file to get started.")
