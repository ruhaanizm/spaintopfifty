import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Music Lifecycle Intelligence",
    layout="wide",
    page_icon="🎧"
)

# -----------------------------
# CUSTOM CSS (THIS IS THE MAGIC)
# -----------------------------
st.markdown("""
<style>
    body {
        background-color: #0e1117;
        color: #ffffff;
    }
    .main {
        background-color: #0e1117;
    }
    h1, h2, h3 {
        color: #ffffff;
        font-weight: 600;
    }
    .stMetric {
        background-color: #1a1f2b;
        padding: 15px;
        border-radius: 12px;
    }
    .css-1d391kg {
        background-color: #111827;
    }
</style>
""", unsafe_allow_html=True)


df = pd.read_csv("data/processed/data_with_stages.csv")
lifecycle_df = pd.read_csv("data/processed/lifecycle_data.csv")
daily_songs = pd.read_csv("data/processed/daily_churn.csv")

df['date'] = pd.to_datetime(df['date'])

#header
st.title("Music Lifecycle Intelligence Dashboard")
st.caption("Understanding playlist dynamics, content behavior, and lifecycle performance")



#sidebar

with st.sidebar:
    st.header("Filters")

    date_range = st.date_input(
    "Date Range",
    value=(df['date'].min(), df['date'].max()),
    min_value=df['date'].min(),
    max_value=df['date'].max()
)
    if isinstance(date_range, (list, tuple)) and len(date_range) == 1:
        st.warning("Bro started the timeline and dipped. Pick an end date too 💀")
        st.stop()

    start_date, end_date = date_range
    if isinstance(date_range, tuple):
        if len(date_range) == 2:
            start_date, end_date = date_range
        elif len(date_range) == 1:
            start_date = end_date = date_range[0]
        else:
            start_date = end_date = df['date'].min()
    else:
        start_date = end_date = date_range

    stage_filter = st.multiselect(
        "Lifecycle Stage",
        df['stage'].unique(),
        default=df['stage'].unique()
    )

    explicit_filter = st.selectbox(
        "Explicit Content",
        ["All", "Explicit", "Non-Explicit"]
    )

    album_filter = st.selectbox(
        "Album Type",
        ["All"] + list(df['album_type'].unique())
    )

#filters
filtered_df = df.copy()

filtered_df = filtered_df[
    (filtered_df['date'] >= pd.to_datetime(date_range[0])) &
    (filtered_df['date'] <= pd.to_datetime(date_range[1]))
]

filtered_df = filtered_df[filtered_df['stage'].isin(stage_filter)]

if explicit_filter == "Explicit":
    filtered_df = filtered_df[filtered_df['is_explicit'] == True]
elif explicit_filter == "Non-Explicit":
    filtered_df = filtered_df[filtered_df['is_explicit'] == False]

if album_filter != "All":
    filtered_df = filtered_df[filtered_df['album_type'] == album_filter]

#KPIs
st.markdown("## Key Metrics")

col1, col2, col3, col4 = st.columns(4)

avg_days = lifecycle_df['total_days'].mean()
avg_peak = lifecycle_df['time_to_peak'].mean()
avg_churn = daily_songs['churn_rate'].mean()
stability = lifecycle_df['total_days'].std()

col1.metric("Avg Lifecycle", f"{avg_days:.1f} days")
col2.metric("Time to Peak", f"{avg_peak:.1f} days")
col3.metric("Churn Rate", f"{avg_churn*100:.2f}%")
col4.metric("Stability Index", f"{stability:.1f}")

st.markdown("---")

#lifecycle
st.markdown("## Song Lifecycle Explorer")

song_choice = st.selectbox("Select a song", filtered_df['song_id'].unique())

song_data = filtered_df[filtered_df['song_id'] == song_choice]

fig = px.line(
    song_data,
    x='date',
    y='position',
    title="Lifecycle Curve",
    markers=True
)

fig.update_yaxes(autorange="reversed")

st.plotly_chart(fig, use_container_width=True)

#entry and exit
st.markdown("## Playlist Flow Dynamics")

fig = px.line(
    daily_songs,
    x='date',
    y=['entries', 'exits'],
    title="Daily Entries vs Exits"
)

st.plotly_chart(fig, use_container_width=True)

#stages
st.markdown("## Lifecycle Distribution")

stage_dist = filtered_df['stage'].value_counts().reset_index()
stage_dist.columns = ['stage', 'count']

fig = px.pie(
    stage_dist,
    names='stage',
    values='count',
    hole=0.5
)

st.plotly_chart(fig, use_container_width=True)

#content
st.markdown("## Content Behavior")

col1, col2 = st.columns(2)

with col1:
    fig = px.box(
        filtered_df,
        x='is_explicit',
        y='popularity',
        title="Explicit vs Popularity",
        labels={'is_explicit':'Explicit', 'popularity':'Popularity'}
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.box(
        filtered_df,
        x='album_type',
        y='popularity',
        title="Album Type vs Popularity",
        labels={'album_type':'Album Type', 'popularity':'Popularity'}
    )
    st.plotly_chart(fig, use_container_width=True)

#churn
st.markdown("## Playlist Stability")

fig = px.line(
    daily_songs,
    x='date',
    y='churn_rate',
    title="Churn Rate Over Time",
    labels={
        'date':'Date', 'churn_rate':'Churn Rate'
    }
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")


st.caption("Built by: Ruhan Ansari")