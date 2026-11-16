# Streamlit app for SurvSet EDA

import streamlit as st
from ydata_profiling import ProfileReport
from streamlit_ydata_profiling import st_profile_report
from SurvSet.data import SurvLoader

COLUMN_NAMES = {
    'ds': 'name',
    'is_td': 'has time-varying features',
    'n': 'sample size',
    'n_fac': 'number of categorical columns',
    'n_ohe': 'number of one-hot-encoded columns',
    'n_num': 'number of continuous columns',
}
# above this number of rows the minimal report is preselected (full report is slow)
LARGE_DATASET_ROWS = 5000


@st.cache_resource
def get_loader():
    return SurvLoader()


@st.cache_data(show_spinner=False)
def load_dataset(ds_name):
    df, ref = get_loader().load_dataset(ds_name=ds_name).values()
    return df, ref


@st.cache_resource(show_spinner="Generating profiling report ...")
def build_profile(ds_name, minimal):
    df, _ = load_dataset(ds_name)
    return ProfileReport(df, progress_bar=False, minimal=minimal)


# Set title and favicon
st.set_page_config(
    page_title="SurvSet EDA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title('SurvSet EDA')
st.write("This Streamlit app provides an EDA (exploratory data analysis) to roughly analyze the provided datasets by SurvSet: An open-source time-to-event dataset repository.")

# List of available datasets and meta-info
df_ds = get_loader().df_ds

# filter on sidebar
st.sidebar.header('Filter')
td_filter = st.sidebar.segmented_control('Time-Dependent?', ('Yes', 'No'), selection_mode='multi') or []
# filter data
if 'Yes' in td_filter and 'No' not in td_filter:
    df_ds = df_ds[df_ds['is_td']]
elif 'No' in td_filter and 'Yes' not in td_filter:
    df_ds = df_ds[~df_ds['is_td']]

# print number of datasets on sidebar
st.sidebar.write('Number of datasets:', df_ds.shape[0])
if df_ds.empty:
    st.sidebar.info('No datasets match the filter.')

st.sidebar.header('Select Dataset')
# select a dataset, OVERVIEW by default
selected_dataset = st.sidebar.selectbox('Select a dataset', ['OVERVIEW'] + df_ds.ds.tolist())

# if OVERVIEW selected, show all datasets
if selected_dataset == 'OVERVIEW':
    st.sidebar.markdown("[SurvSet on GitHub](https://github.com/ErikinBC/SurvSet)")
    st.sidebar.markdown("[SurvSet Paper](https://arxiv.org/pdf/2203.03094.pdf)")

    # print available datasets
    st.header('Available Datasets')
    # rename column names for better readability
    st.dataframe(df_ds.rename(columns=COLUMN_NAMES), hide_index=True)

else:
    # load dataset and its reference
    df, ref = load_dataset(selected_dataset)

    # print statistics and reference
    st.sidebar.header('Statistics')
    info = df_ds[df_ds.ds == selected_dataset].iloc[0].rename(COLUMN_NAMES).astype(str)
    st.sidebar.table(info.rename('value'))
    st.sidebar.markdown("**Reference:**")
    st.sidebar.write(ref)

    st.header('Dataset: ' + selected_dataset)
    st.write(f"Dataset Preview ({df.shape[0]} rows, {df.shape[1]} columns):")
    st.dataframe(df)
    st.download_button(
        'Download dataset as CSV',
        df.to_csv(index=False).encode('utf-8'),
        file_name=f'{selected_dataset}.csv',
        mime='text/csv',
    )

    # Profiling report: minimal mode is much faster for large datasets
    minimal = st.sidebar.toggle(
        'Minimal report (faster)',
        value=len(df) > LARGE_DATASET_ROWS,
        key=f'minimal_{selected_dataset}',
    )
    profile = build_profile(selected_dataset, minimal)

    # Display the profiling report in Streamlit
    st_profile_report(profile, navbar=True)
