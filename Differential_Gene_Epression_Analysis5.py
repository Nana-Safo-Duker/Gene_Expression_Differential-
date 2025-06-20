import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configuration & Styling ---
st.set_page_config(layout="wide", page_title="Bioinformatics Gene Expression Dashboard")

# Custom CSS for better aesthetics (Tailwind-like feel with rounded corners, shadows)
st.markdown("""
    <style>
    /* Main container padding and background */
    .main .block-container {
        padding-left: 2rem;
        padding-right: 2rem;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    .stApp {
        background-color: #f0f2f6; /* Light gray background */
        font-family: "Inter", sans-serif; /* Inter font */
    }

    /* Sidebar styling */
    .stSidebar {
        background-color: #ffffff; /* White sidebar */
        border-right: 1px solid #e0e0e0;
        border-radius: 12px; /* Rounded corners for sidebar */
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); /* Subtle shadow */
        padding: 1rem;
    }
    .stSidebar > div:first-child { /* Target the inner sidebar content div for spacing */
        padding-top: 1rem;
    }

    /* Input fields (selectbox, textinput, multiselect) */
    .stSelectbox, .stTextInput, .stMultiSelect {
        border-radius: 8px; /* Rounded corners for input fields */
        border: 1px solid #cccccc;
    }

    /* Button styling */
    .stButton>button {
        border-radius: 8px; /* Rounded corners for buttons */
        border: none;
        background-color: #4CAF50; /* Green button */
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2); /* Button shadow */
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049; /* Darker green on hover */
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
    }

    /* DataFrame styling */
    .stDataFrame {
        border-radius: 8px; /* Rounded corners for dataframes */
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        overflow: hidden; /* Ensures content stays within rounded corners */
    }

    /* Headings styling */
    h1, h2, h3, h4, h5, h6 {
        color: #333333; /* Darker text for headings */
    }

    /* Info/Warning boxes */
    .stAlert {
        border-radius: 8px; /* Rounded corners for alerts */
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .stAlert.info {
        background-color: #e0f2f7; /* Light blue for info */
        color: #0288d1; /* Darker blue text */
        border-left: 5px solid #0288d1;
    }
    .stAlert.warning {
        background-color: #fff3e0; /* Light orange for warning */
        color: #f57c00; /* Darker orange text */
        border-left: 5px solid #f57c00;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Data Loading (Simulated for demonstration. In a real app, load your actual CSV/data) ---
@st.cache_data # Cache data to improve performance, runs only once
def load_mock_data():
    """
    Generates a mock gene expression dataset for demonstration.
    In a real application, you would load your pre-processed gene expression data,
    e.g., df = pd.read_csv('your_gene_expression_data.csv').
    """
    np.random.seed(42) # for reproducibility
    genes = [f'Gene{i}' for i in range(1, 101)] # 100 mock genes
    patient_ids = [f'Patient{i}' for i in range(1, 26)] # 25 mock patients
    cancer_types = ['Breast Cancer', 'Lung Cancer', 'Colon Cancer', 'Prostate Cancer']
    sample_types = ['Tumor', 'Normal']

    data = []
    for patient in patient_ids:
        # Assign a random cancer type to each patient (for simplicity in mock data)
        patient_cancer_type = np.random.choice(cancer_types)
        for gene in genes:
            # Simulate different expression patterns based on gene, sample type, and cancer type
            base_expr_normal = np.random.uniform(5, 50) # Base expression for normal tissue
            base_expr_tumor = base_expr_normal * np.random.uniform(0.8, 1.2) # Small variation for non-DE genes

            # Introduce differential expression for specific genes
            if gene in ['Gene1', 'Gene2', 'Gene3', 'Gene4', 'Gene5']: # Highly upregulated in some cancers
                if patient_cancer_type == 'Breast Cancer' and gene in ['Gene1', 'Gene2']:
                    tumor_expr = np.random.normal(loc=base_expr_normal * 5, scale=base_expr_normal * 0.5)
                elif patient_cancer_type == 'Lung Cancer' and gene == 'Gene3':
                    tumor_expr = np.random.normal(loc=base_expr_normal * 4, scale=base_expr_normal * 0.4)
                else:
                    tumor_expr = np.random.normal(loc=base_expr_normal * np.random.uniform(0.9, 1.1), scale=base_expr_normal * 0.1) # Small change
                normal_expr = np.random.normal(loc=base_expr_normal, scale=base_expr_normal * 0.1)

            elif gene in ['Gene10', 'Gene11', 'Gene12']: # Downregulated in some cancers
                if patient_cancer_type == 'Colon Cancer' and gene == 'Gene10':
                    tumor_expr = np.random.normal(loc=base_expr_normal * 0.2, scale=base_expr_normal * 0.05)
                else:
                    tumor_expr = np.random.normal(loc=base_expr_normal * np.random.uniform(0.9, 1.1), scale=base_expr_normal * 0.1) # Small change
                normal_expr = np.random.normal(loc=base_expr_normal, scale=base_expr_normal * 0.1)
            else: # Rest are mostly stable
                tumor_expr = np.random.normal(loc=base_expr_tumor, scale=base_expr_tumor * 0.1)
                normal_expr = np.random.normal(loc=base_expr_normal, scale=base_expr_normal * 0.1)

            # Ensure non-negative expression values
            tumor_expr = max(0.1, tumor_expr)
            normal_expr = max(0.1, normal_expr)

            data.append({'Gene': gene,
                         'Sample_ID': f'{patient}_{patient_cancer_type}_Tumor',
                         'Expression_Value': tumor_expr,
                         'Sample_Type': 'Tumor',
                         'Cancer_Type': patient_cancer_type})
            data.append({'Gene': gene,
                         'Sample_ID': f'{patient}_{patient_cancer_type}_Normal',
                         'Expression_Value': normal_expr,
                         'Sample_Type': 'Normal',
                         'Cancer_Type': patient_cancer_type})

    df_raw = pd.DataFrame(data)

    # Convert expression values to log2 for better visualization of differences
    df_raw['Log2_Expression'] = np.log2(df_raw['Expression_Value'])
    return df_raw

# Load data when the app starts (or from cache if already loaded)
df = load_mock_data()

# --- Dashboard Title & Introduction ---
st.title("🔬 Interactive Gene Expression Dashboard")
st.markdown("""
This dashboard allows you to explore **differential gene expression** in various simulated cancer types.
Leveraging principles from **Bioinformatics** and **Genomic Data Analysis**,
it provides a quick way to visualize gene expression patterns between tumor and normal tissues.
This is a demonstration of how **AI/ML** concepts can be applied in **Precision Medicine**
within a **Cloud Computing** environment.
""")
st.write("---")

# --- Sidebar for User Input ---
st.sidebar.header("Dashboard Controls")
st.sidebar.markdown("Use the options below to filter data and select genes for visualization.")

# Select Cancer Type
all_cancer_types_options = ['All Cancer Types'] + sorted(df['Cancer_Type'].unique().tolist())
selected_cancer_type = st.sidebar.selectbox(
    "Select Cancer Type:",
    all_cancer_types_options,
    help="Filter data by a specific cancer type."
)

# Filter data based on selected cancer type
if selected_cancer_type == 'All Cancer Types':
    filtered_df = df.copy()
else:
    filtered_df = df[df['Cancer_Type'] == selected_cancer_type].copy()

# Identify top differentially expressed genes (mock calculation for demo)
@st.cache_data(show_spinner=False) # Cache the result and hide spinner for speed
def get_mock_differential_genes(dataframe):
    """
    A highly simplified mock function to identify "differential" genes.
    In a real bioinformatics pipeline, this would involve robust statistical
    tests like t-tests, DESeq2, or edgeR to calculate fold changes and p-values.
    """
    if dataframe.empty:
        return []

    # Calculate mean expression for Tumor and Normal samples
    avg_expr = dataframe.groupby(['Gene', 'Sample_Type'])['Log2_Expression'].mean().unstack()

    # Calculate mock log2 fold change (Tumor vs Normal)
    if 'Tumor' in avg_expr.columns and 'Normal' in avg_expr.columns:
        avg_expr['Log2_Fold_Change'] = avg_expr['Tumor'] - avg_expr['Normal']
        # Sort by absolute fold change to get potentially "most differential" genes
        # For a real scenario, you'd filter by p-value and then fold change
        sorted_genes = avg_expr.sort_values(by='Log2_Fold_Change', ascending=False).index.tolist()
        return sorted_genes
    return []

top_mock_differential_genes = get_mock_differential_genes(filtered_df)

# Default genes for selection based on mock data that should show differences
default_genes_for_selection = []
if top_mock_differential_genes:
    # Attempt to pre-select a few genes that are known to be differential in the mock data
    priority_genes = ['Gene1', 'Gene2', 'Gene3', 'Gene10', 'Gene11']
    default_genes_for_selection = [gene for gene in priority_genes if gene in top_mock_differential_genes]
    # If less than 3, add more from the top
    if len(default_genes_for_selection) < 3:
        for gene in top_mock_differential_genes:
            if gene not in default_genes_for_selection:
                default_genes_for_selection.append(gene)
            if len(default_genes_for_selection) >= 3:
                break

# Multi-select for genes to visualize
all_unique_genes = sorted(filtered_df['Gene'].unique().tolist())
selected_genes = st.sidebar.multiselect(
    "Select Genes to Visualize:",
    options=all_unique_genes,
    default=default_genes_for_selection,
    help="Choose one or more genes to display their expression patterns (Log2 Scale)."
)

st.sidebar.write("---")
st.sidebar.info("""
**Data simulated for demonstration purposes.**
Real genomic datasets are significantly larger and require complex
bioinformatics pipelines for pre-processing and accurate
differential expression analysis.
""")

# --- Main Content Area for Visualizations ---

if not selected_genes:
    st.info("💡 Please select at least one gene from the sidebar to visualize its expression data.")
else:
    st.subheader(f"Expression of Selected Genes in {selected_cancer_type} Samples")

    # Filter data for selected genes
    plot_df = filtered_df[filtered_df['Gene'].isin(selected_genes)]

    if plot_df.empty:
        st.warning(f"No data available for the selected genes in {selected_cancer_type} (or 'All Cancer Types'). Please try different selections.")
    else:
        # Arrange plots in columns if many genes selected
        num_genes = len(selected_genes)
        num_cols = 2 if num_genes > 1 else 1
        cols = st.columns(num_cols)

        for i, gene in enumerate(selected_genes):
            with cols[i % num_cols]:
                st.markdown(f"#### {gene}")
                gene_df = plot_df[plot_df['Gene'] == gene].copy() # Use .copy() to avoid SettingWithCopyWarning

                # Create box plot
                fig, ax = plt.subplots(figsize=(7, 4)) # Adjust figsize for columns
                sns.boxplot(data=gene_df, x='Sample_Type', y='Log2_Expression',
                            palette={'Tumor': 'salmon', 'Normal': 'lightskyblue'}, ax=ax,
                            showfliers=False) # Hide outliers for cleaner look
                sns.stripplot(data=gene_df, x='Sample_Type', y='Log2_Expression',
                              color='black', size=4, jitter=0.2, ax=ax, alpha=0.6) # Add individual data points
                ax.set_title(f'Expression of {gene}', fontsize=12)
                ax.set_xlabel('Sample Type', fontsize=10)
                ax.set_ylabel('Log2 Expression Value', fontsize=10)
                plt.xticks(fontsize=10)
                plt.yticks(fontsize=10)
                st.pyplot(fig)
                plt.close(fig) # Close the figure to free up memory

                st.markdown("---") # Separator between gene plots

# --- Footer / About Section ---
st.markdown("### About this Dashboard")
st.info("""
This interactive tool demonstrates how **computational approaches** can be used to explore complex biological data.
It integrates concepts from:
- **Genomic Data Analysis** (focus on gene expression)
- **Bioinformatics** (data processing and visualization)
- **AI/ML** (underlying skills in data handling, feature engineering, and model interpretation, crucial for larger predictive tasks in this domain)
- **Cloud Computing** (via deployment on Streamlit Cloud, exemplifying accessible and scalable application delivery for **Precision Medicine** and **Cancer Research**).

The data presented here is **simulated** for demonstration purposes. A real-world application would utilize
actual patient genomic datasets, often requiring extensive pre-processing and advanced statistical or
machine learning models for robust insights.
""")

st.markdown("---")
st.markdown("Created by Nana Safo Duker")
st.markdown("[GitHub Repository Link Placeholder](YOUR_GITHUB_REPO_LINK_HERE)") # Remember to update this!
st.markdown("Feel free to connect on [LinkedIn Profile Link Placeholder](YOUR_LINKEDIN_PROFILE_LINK_HERE)") # Remember to update this!
