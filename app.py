import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Music Lifecycle Intelligence",
    layout="wide",
    page_icon="🎧"
)

st.markdown("""
<style>

/* FONTS */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Orbitron:wght@400;600&display=swap');

:root {
    --bg-main: #01010a;
    --neon-purple: #a855f7;
    --neon-blue: #38bdf8;
    --neon-pink: #ec4899;
    --neon-green: #22c55e;
    --glass: rgba(255,255,255,0.04);
    --border: rgba(255,255,255,0.08);
}

/* GLOBAL */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: radial-gradient(circle at 10% 20%, #0f172a, #01010a 70%);
    color: #e2e8f0;
}

/* BACKGROUND GLOW */
body::before {
    content: "";
    position: fixed;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(168,85,247,0.25), transparent 70%);
    top: -200px;
    left: -200px;
    filter: blur(140px);
    z-index: -1;
}

body::after {
    content: "";
    position: fixed;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(56,189,248,0.25), transparent 70%);
    bottom: -200px;
    right: -200px;
    filter: blur(140px);
    z-index: -1;
}

/* TITLE — CYBERPUNK */
h1 {
    font-family: 'Orbitron', sans-serif;
    font-size: 3rem;
    background: linear-gradient(90deg, #a855f7, #38bdf8, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* METRIC CARDS */
[data-testid="stMetric"] {
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 22px;
    backdrop-filter: blur(20px);
    transition: 0.3s;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow:
        0 0 25px rgba(168,85,247,0.6),
        0 0 40px rgba(56,189,248,0.4);
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #01010a, #0f172a);
    border-right: 1px solid var(--border);
}

/* INPUTS */
.stSelectbox div, .stMultiSelect div, .stDateInput div {
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    border: 1px solid var(--border);
}

.stSelectbox div:focus-within,
.stMultiSelect div:focus-within,
.stDateInput div:focus-within {
    border: 1px solid var(--neon-purple);
    box-shadow: 0 0 12px rgba(168,85,247,0.6);
}

/* BUTTON */
button[kind="primary"] {
    background: linear-gradient(135deg, #a855f7, #ec4899);
    border-radius: 14px;
    border: none;
}

button[kind="primary"]:hover {
    box-shadow:
        0 0 20px #a855f7,
        0 0 40px #ec4899;
}

/* CHART CONTAINER */
.stPlotlyChart {
    background: rgba(255,255,255,0.02);
    border-radius: 20px;
    padding: 16px;
    border: 1px solid var(--border);
    backdrop-filter: blur(10px);
}

/* SCROLL */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.2);
    border-radius: 10px;
}

/* REMOVE FOOTER */
footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

df = pd.read_csv("data/processed/data_with_stages.csv")
lifecycle_df = pd.read_csv("data/processed/lifecycle_data.csv")
daily_songs = pd.read_csv("data/processed/daily_churn.csv")

df['date'] = pd.to_datetime(df['date'])
daily_songs['date'] = pd.to_datetime(daily_songs['date'])


st.title("🎧 Streaming Lifecycle Analytics Dashboard")
st.caption("Understanding playlist dynamics, content behavior, and lifecycle performance")


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


filtered_df = df.copy()

filtered_df = filtered_df[
    (filtered_df['date'] >= pd.to_datetime(start_date)) &
    (filtered_df['date'] <= pd.to_datetime(end_date))
]

filtered_df = filtered_df[filtered_df['stage'].isin(stage_filter)]

if explicit_filter == "Explicit":
    filtered_df = filtered_df[filtered_df['is_explicit'] == True]
elif explicit_filter == "Non-Explicit":
    filtered_df = filtered_df[filtered_df['is_explicit'] == False]

if album_filter != "All":
    filtered_df = filtered_df[filtered_df['album_type'] == album_filter]


st.markdown("## Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Avg Lifecycle", f"{lifecycle_df['total_days'].mean():.1f} days")
col2.metric("Time to Peak", f"{lifecycle_df['time_to_peak'].mean():.1f} days")
col3.metric("Churn Rate", f"{daily_songs['churn_rate'].mean()*100:.2f}%")
col4.metric("Stability Index", f"{lifecycle_df['total_days'].std():.1f}")

st.markdown("---")


neon_colors = ["#a855f7", "#38bdf8", "#ec4899", "#22c55e", "#facc15"]


st.markdown("## Aggregate Lifecycle Curve")

agg_lifecycle = filtered_df.groupby('days_since_entry')['position'].mean().reset_index()

fig = px.line(
    agg_lifecycle,
    x='days_since_entry',
    y='position',
    title="Average Song Lifecycle Pattern",
    labels={
        'days_since_entry': 'Days Since Entry',
        'position': 'Average Rank Position'
    },
    color_discrete_sequence=neon_colors
)

fig.update_layout(height=350, template="plotly_dark")
fig.update_yaxes(autorange="reversed")

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


st.markdown("## Playlist Flow Dynamics")

fig = px.line(
    daily_songs,
    x='date',
    y=['entries', 'exits'],
    labels={'value': 'Songs', 'variable': 'Metric', 'date': 'Date'}
)

fig.update_traces(selector=dict(name='entries'),
                  line=dict(color='#38bdf8', dash='dot'))

fig.update_traces(selector=dict(name='exits'),
                  line=dict(color='#f87171'))

fig.update_layout(height=350, template="plotly_dark")

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


st.markdown("## Lifecycle Distribution")

stage_dist = filtered_df['stage'].value_counts().reset_index()
stage_dist.columns = ['stage', 'count']

fig = px.pie(
    stage_dist,
    names='stage',
    values='count',
    hole=0.5,
    color_discrete_sequence=neon_colors
)

fig.update_traces(textinfo='percent+label', textfont=dict(color='white'))
fig.update_layout(height=350, template="plotly_dark")

st.plotly_chart(fig, use_container_width=True)


st.markdown("## Content Behavior")

col1, col2 = st.columns(2)

with col1:
    fig1 = px.box(
        filtered_df,
        x='is_explicit',
        y='popularity',
        labels={'is_explicit': 'Explicit', 'popularity': 'Popularity'},
        color_discrete_sequence=neon_colors
    )
    fig1.update_layout(height=350, template="plotly_dark")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.box(
        filtered_df,
        x='album_type',
        y='popularity',
        labels={'album_type': 'Album Type', 'popularity': 'Popularity'},
        color_discrete_sequence=neon_colors
    )
    fig2.update_layout(height=350, template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)


st.markdown("## Playlist Stability")

fig = px.line(
    daily_songs,
    x='date',
    y='churn_rate',
    labels={'date': 'Date', 'churn_rate': 'Churn Rate'},
    color_discrete_sequence=neon_colors
)

fig.update_layout(height=350, template="plotly_dark")

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


st.markdown("---")
st.caption("Built by Ruhan Ansari — powered by data & questionable sleep cycles")