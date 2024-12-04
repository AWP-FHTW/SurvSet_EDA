# Streamlit app for SurvSet EDA

import streamlit as st
from SurvSet.data import SurvLoader
from streamlit_pandas_profiling import st_profile_report
from ydata_profiling import ProfileReport

column_names = ['name', 'has time-varying features', 'sample size', 'number of categorical columns', 'not of one-hot-encoded columns', 'number of continuous columns']

# Set title and favicon
st.set_page_config(
    page_title="SurvSet EDA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title('SurvSet EDA')

# List of available datasets and meta-info
loader = SurvLoader()
df_ds= loader.df_ds

# filter on sidebar
st.sidebar.header('Filter')
td_filter = st.sidebar.segmented_control('Time-Dependent?', ('Yes', 'No'), selection_mode='multi')
# filter data
if 'Yes' in td_filter and 'No' not in td_filter:
    df_ds = df_ds[df_ds['is_td'] == True]
elif 'No' in td_filter and 'Yes' not in td_filter:
    df_ds = df_ds[df_ds['is_td'] == False]

# print number of datasets on sidebar
st.sidebar.write('Number of datasets:', df_ds.shape[0])

st.sidebar.header('Select Dataset')
# select a dataset, None by default as overview
selected_dataset = st.sidebar.selectbox('Select a dataset', ['OVERVIEW'] + df_ds.ds.tolist())

# if None selected, show all datasets
if selected_dataset == 'OVERVIEW':
    st.sidebar.write("SurvSet on Github:", "https://github.com/ErikinBC/SurvSet")
    st.sidebar.write("SurvSet Paper:", "https://arxiv.org/pdf/2203.03094.pdf")
    
    # print available datasets
    st.header('Available Datasets')
    # rename column names for better readability
    df_ds.columns = column_names
    st.dataframe(df_ds)

else:
    # load dataset and its reference
    df, ref = loader.load_dataset(ds_name=selected_dataset).values()

    # print statistics and reference
    st.sidebar.header('Statistics')
    info= df_ds[df_ds.ds == selected_dataset].iloc[0]
    info.index = column_names
    st.sidebar.write(info)
    st.sidebar.write("Reference:", ref)

    st.header('Dataset: ' + selected_dataset)
    st.write("Dataset Preview:")
    st.dataframe(df)

    # Generate profiling report with user-selected options
    profile = ProfileReport(df, progress_bar=False)

    # Display the profiling report in Streamlit
    st_profile_report(profile)
