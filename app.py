import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np

st.set_page_config(
    page_title="MagentaPulse: T-Mobile Customer Happiness Index",
    page_icon="💬",
    layout="wide"
)

# -------------------------------
# GLOBAL STYLE
# -------------------------------
st.markdown(""" 
<style>
.main {
    background: radial-gradient(circle at 20% 20%, #141416 0%, #0d0d0f 100%);
    color: #fff;
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
}
h1, h2, h3 { color: #E20074; font-weight: 700; letter-spacing: 0.5px; }
.sub-header { color: #b3b3b3; font-size: 15px; }
.metric-card {
    background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.12);
    border-radius: 18px; padding: 24px; text-align: center;
    backdrop-filter: blur(12px); box-shadow: 0 8px 30px rgba(226,0,116,0.15);
    transition: all 0.25s ease-in-out;
}
.metric-card:hover { transform: translateY(-6px); box-shadow: 0 12px 35px rgba(226,0,116,0.35); }
.metric-value { font-size: 34px; font-weight: 700; color: #fff; }
.metric-label { font-size: 15px; color: #ccc; }
.metric-sub { font-size: 12px; color: #999; }
.stTabs [role="tablist"] { border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 18px; }
.stTabs [role="tab"] { font-weight: 600; color: #aaa; padding: 10px 20px; border-radius: 6px 6px 0 0; }
.stTabs [aria-selected="true"] {
    color: #fff !important; background: linear-gradient(90deg,#E20074,#8a0060);
    box-shadow: 0 0 20px rgba(226,0,116,0.35);
}

/* Graph card styling */
.graph-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 25px;
    box-shadow: 0 4px 25px rgba(226,0,116,0.2);
    backdrop-filter: blur(8px);
    transition: all 0.25s ease-in-out;
}
.graph-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 30px rgba(226,0,116,0.35);
}

/* Recommendation cards */
.reco-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 18px;
    padding: 18px 24px;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# HEADER
# -------------------------------
st.markdown("<h1>MagentaPulse: T-Mobile Customer Happiness Index</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-header'>Last updated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}</div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "📊 Overview", "🤖 Insights", "💬 Reviews"
])

# -------------------------------
# DATASETS
# -------------------------------
months = pd.date_range(start="2025-01-01", periods=12, freq="M")
df = pd.DataFrame({
    "date": months,
    "sentiment_score": [0.72, 0.68, 0.70, 0.74, 0.78, 0.81, 0.76, 0.73, 0.75, 0.79, 0.83, 0.80],
    "positive": [65, 61, 63, 70, 72, 75, 68, 66, 70, 74, 78, 76],
    "neutral": [20, 22, 21, 18, 16, 15, 17, 20, 19, 16, 14, 15],
    "negative": [15, 17, 16, 12, 12, 10, 15, 14, 11, 10, 8, 9]
})

# -------------------------------
# TAB 1 — OVERVIEW
# -------------------------------
with tab1:
    st.markdown("### Overview Metrics")
    col1, col2, col3, col4 = st.columns(4)
    for col, (label, value, sub) in zip(
        [col1, col2, col3, col4],
        [
            ("Average Sentiment", "0.76", "(+4% MoM)"),
            ("Total Reviews", "12,534", "from all sources"),
            ("Top Source", "Trustpilot", "48% of data"),
            ("Average Rating", "4.1 ★", "last 30 days")
        ]
    ):
        with col:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-sub">{sub}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    left, right = st.columns(2)

    with left:
        st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
        pie = px.pie(
            pd.DataFrame({"Sentiment": ["Positive", "Neutral", "Negative"], "Percentage": [68, 19, 13]}),
            names="Sentiment",
            values="Percentage",
            color="Sentiment",
            color_discrete_map={"Positive": "#E20074", "Neutral": "#999", "Negative": "#444"}
        )
        pie.update_layout(paper_bgcolor="#0d0d0f", font_color="white")
        st.plotly_chart(pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
        trend = px.line(df, x="date", y="sentiment_score", markers=True,
                        line_shape="spline", color_discrete_sequence=["#E20074"])
        trend.update_layout(paper_bgcolor="#0d0d0f", font_color="white",
                            yaxis_title="Average Sentiment", xaxis_title="Month")
        st.plotly_chart(trend, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
    area = px.area(df, x="date", y=["positive", "neutral", "negative"],
                   color_discrete_sequence=["#E20074", "#888", "#333"])
    area.update_layout(paper_bgcolor="#0d0d0f", font_color="white", hovermode="x unified")
    st.plotly_chart(area, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# TAB 2 — INSIGHTS
# -------------------------------
with tab2:
    st.markdown("### 💬 Pulse Insights")
    st.write("Filter by date or sentiment to uncover key trends and AI-backed recommendations.")

    left, right = st.columns([1, 2])

    with left:
        st.markdown("#### 📅 Date")
        selected_date = st.date_input("", datetime.now())
        st.markdown("#### 💭 Sentiment")
        sentiment_choice = st.radio("", ["Good", "Bad", "Both"], index=2)

    with right:
        feedback_data = {
            "Good": {
                "summary": "Positive sentiment jumped 18% — customers love app stability and faster support.",
                "solutions": [
                    {"title": "Boost Loyalty Visibility", "evidence": "84% of praise mentioned Magenta Rewards."},
                    {"title": "Keep App Updates Rolling", "evidence": "Crash rate dropped from 4.5% → 1.2%."}
                ]
            },
            "Bad": {
                "summary": "Negative chatter centered on billing confusion and slow chat support.",
                "solutions": [
                    {"title": "Clarify Billing Cycles", "evidence": "42% cite unclear post-migration invoices."},
                    {"title": "Deploy 24/7 AI Chat", "evidence": "Wait times hit 17 mins at peak hours."}
                ]
            },
            "Both": {
                "summary": "Mixed signals — network reliability praised, but communication gaps remain.",
                "solutions": [
                    {"title": "Proactive Notifications", "evidence": "Outage alerts reduce negative sentiment by 27%."},
                    {"title": "Tailored Support Follow-ups", "evidence": "Personalization improves retention 23%."}
                ]
            }
        }

        selected = feedback_data[sentiment_choice]
        st.markdown(f"#### 🧭 Summary — {sentiment_choice} Feedback")
        st.write(selected["summary"])

        st.markdown("### 💡 Recommended Actions")
        for s in selected["solutions"]:
            st.markdown(f"""
                <div class='reco-card'>
                    <b style='color:#E20074;'>{s['title']}</b><br>
                    <span style='color:#ccc;'>{s['evidence']}</span>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
        df_chart = pd.DataFrame({
            "Category": ["Support", "Billing", "Coverage", "App"],
            "Mentions": np.random.randint(20, 100, 4)
        })
        chart = px.bar(df_chart, x="Category", y="Mentions", color_discrete_sequence=["#E20074"])
        chart.update_layout(
            paper_bgcolor="#0d0d0f", plot_bgcolor="#0d0d0f",
            font_color="white", height=300,
            title=f"{sentiment_choice} Feedback Breakdown — {selected_date.strftime('%b %d, %Y')}"
        )
        st.plotly_chart(chart, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# TAB 3 — REVIEWS
# -------------------------------
with tab3:
    st.markdown("### 💬 Customer Review Snapshot")

    st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
    gauge = px.pie(
        values=[76, 24],
        names=["Satisfied", "Unsatisfied"],
        hole=0.6, color_discrete_sequence=["#E20074", "#333"]
    )
    gauge.update_layout(paper_bgcolor="#0d0d0f", font_color="white",
                        showlegend=False, annotations=[dict(text="76% Happy", showarrow=False, font_size=18)])
    st.plotly_chart(gauge, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 🔎 Recent Feedback")
    reviews = [
        {"rating": 5, "text": "Love T-Mobile’s new plans — support was super fast!"},
        {"rating": 4, "text": "Great coverage, but billing clarity could improve."},
        {"rating": 3, "text": "Okay experience. App works fine but chat queues are long."},
        {"rating": 1, "text": "Frustrating billing system and call center."}
    ]
    for r in reviews:
        st.markdown(f"⭐ **{r['rating']} / 5** — *{r['text']}*")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("<div style='color:#999; font-size:14px; text-align:center; margin-top:40px;'>MagentaPulse © 2025 — Built with Streamlit.</div>", unsafe_allow_html=True)
