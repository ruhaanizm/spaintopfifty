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

/* FONTS */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:wght@500;600&display=swap');

/* ROOT VARIABLES — CONTROL THE VIBE */
:root {
    --bg-main: #020617;
    --bg-glass: rgba(255, 255, 255, 0.04);
    --border-glass: rgba(255,255,255,0.08);
    --accent: #7c3aed;
    --accent-soft: rgba(124,58,237,0.25);
    --text-main: #e2e8f0;
    --text-dim: #94a3b8;
}

/* GLOBAL */
html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
    background: radial-gradient(circle at 20% 20%, #0f172a, #020617 70%);
    color: var(--text-main);
    overflow-x: hidden;
}

/* SUBTLE BACKGROUND GLOW (THIS IS THE SAUCE) */
body::before {
    content: "";
    position: fixed;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(124,58,237,0.15), transparent 70%);
    top: -200px;
    left: -200px;
    filter: blur(120px);
    z-index: -1;
}

body::after {
    content: "";
    position: fixed;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(59,130,246,0.12), transparent 70%);
    bottom: -200px;
    right: -200px;
    filter: blur(120px);
    z-index: -1;
}

/* HEADINGS — SILKY TEXT */
h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem;
    background: linear-gradient(90deg, #ffffff, #a5b4fc, #c4b5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}

h2 {
    color: var(--text-main);
    font-weight: 600;
}

h3 {
    color: var(--text-dim);
}

/* METRIC CARDS — FLOATING GLASS */
[data-testid="stMetric"] {
    background: var(--bg-glass);
    border: 1px solid var(--border-glass);
    padding: 22px;
    border-radius: 20px;
    backdrop-filter: blur(18px);
    transition: all 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}

/* HOVER = MICRO “PULL” EFFECT */
[data-testid="stMetric"]:hover {
    transform: translateY(-6px) scale(1.015);
    box-shadow: 
        0 10px 30px rgba(0,0,0,0.4),
        0 0 25px var(--accent-soft);
}

/* SIDEBAR — DEPTH */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #0f172a);
    border-right: 1px solid var(--border-glass);
}

/* INPUTS — FOCUS GLOW */
.stSelectbox div, .stMultiSelect div, .stDateInput div {
    background: rgba(255,255,255,0.03);
    border-radius: 14px;
    border: 1px solid var(--border-glass);
    transition: all 0.25s ease;
}

.stSelectbox div:focus-within,
.stMultiSelect div:focus-within,
.stDateInput div:focus-within {
    border: 1px solid var(--accent);
    box-shadow: 0 0 0 2px rgba(124,58,237,0.2);
}

/* BUTTON — SMOOTH + TEMPTING */
button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed, #6366f1);
    border-radius: 14px;
    border: none;
    font-weight: 500;
    letter-spacing: 0.3px;
    transition: all 0.3s ease;
}

button[kind="primary"]:hover {
    transform: translateY(-2px) scale(1.03);
    box-shadow: 
        0 10px 25px rgba(124,58,237,0.4),
        0 0 20px rgba(99,102,241,0.5);
}

/* CHART CONTAINER — SOFT GLASS PANEL */
.stPlotlyChart {
    background: rgba(255,255,255,0.02);
    border-radius: 20px;
    padding: 16px;
    border: 1px solid var(--border-glass);
    backdrop-filter: blur(12px);
    transition: 0.3s ease;
}

.stPlotlyChart:hover {
    border: 1px solid rgba(124,58,237,0.4);
}

/* SCROLLBAR — MINIMAL */
::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-thumb {
    background: rgba(148,163,184,0.25);
    border-radius: 10px;
}

/* FOOTER */
footer {
    visibility: hidden;
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
    },
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")


st.caption("Built by: Ruhan Ansari")