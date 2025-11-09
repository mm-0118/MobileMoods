import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from bs4 import BeautifulSoup
from datetime import datetime
import json, re, os

# -------------------------------
# STREAMLIT PAGE CONFIG + STYLE
# -------------------------------
st.set_page_config(
    page_title="MagentaPulse: T-Mobile Customer Happiness Index",
    page_icon="💬",
    layout="wide"
)

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
.graph-card:hover { transform: translateY(-4px); box-shadow: 0 6px 30px rgba(226,0,116,0.35); }
</style>
""", unsafe_allow_html=True)


# -------------------------------
# SCRAPER
# -------------------------------
def scrape_downdetector(html_file):
    soup = BeautifulSoup(html_file, "html.parser")
    comment_blocks = soup.find_all("p")

    username_to_id = {}
    next_user_id = 1
    all_comments = []

    for block in comment_blocks:
        links = block.find_all("a")
        if len(links) >= 2:
            username = links[0].text.strip()
            comment_text = links[1].text.strip()

            if username not in username_to_id:
                username_to_id[username] = next_user_id
                next_user_id += 1
            user_id = username_to_id[username]

            comment_time = datetime.now().isoformat()
            comment_data = {
                "username": username,
                "user_id": user_id,
                "comment_time": comment_time,
                "comment": comment_text,
                "reported_outages_at_time": 0,
            }
            all_comments.append(comment_data)
    return all_comments


# -------------------------------
# GEMINI SENTIMENT CLASSIFIER (BATCH)
# -------------------------------
def JsonTo2DList(data, apiKey):
    genai.configure(api_key=apiKey)
    model = genai.GenerativeModel("gemini-2.5-flash")

    combined_comments = "\n".join([f"{i+1}. {item['comment']}" for i, item in enumerate(data)])
    prompt = f"""
    You are a precise sentiment classifier. 
    Classify each of the following T-Mobile customer comments as 'positive', 'negative', or 'neutral'
    based ONLY on tone toward T-Mobile service.
    Output ONLY valid JSON array like:
    [{{"id":1,"sentiment":"positive"}},{{"id":2,"sentiment":"negative"}},...]
    Comments:
    {combined_comments}
    """

    response = model.generate_content(prompt)
    text = response.text.strip()

    # --- Fix: Extract JSON even if Gemini adds fluff ---
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        text = match.group(0)

    try:
        sentiments = json.loads(text)
    except Exception as e:
        print("⚠️ Gemini JSON parsing failed:", e)
        print("Raw Gemini output:", text)
        sentiments = []

    results = []
    for i, item in enumerate(data):
        sentiment_str = "neutral"
        if i < len(sentiments):
            sentiment_str = sentiments[i].get("sentiment", "neutral").lower()

        sentiment = 1 if "positive" in sentiment_str else -1 if "negative" in sentiment_str else 0
        results.append([
            item["username"],
            item["user_id"],
            item["comment_time"],
            item["comment"],
            sentiment,
            item["reported_outages_at_time"],
            0,
        ])

    # Optional: print debug counts
    positives = sum(1 for r in results if r[4] == 1)
    negatives = sum(1 for r in results if r[4] == -1)
    neutrals = sum(1 for r in results if r[4] == 0)
    print(f"✅ Sentiment counts → Positive: {positives}, Negative: {negatives}, Neutral: {neutrals}")

    return results


# -------------------------------
# FEEDBACK SUMMARIZER
# -------------------------------
def summarize_feedback(comments, apiKey, sentiment_type):
    genai.configure(api_key=apiKey)
    model = genai.GenerativeModel("gemini-2.5-flash")
    filtered = [
        c for c in comments
        if (sentiment_type == "positive" and c[4] == 1)
        or (sentiment_type == "negative" and c[4] == -1)
    ]
    joined = "\n".join([f"{c[2]} - {c[3]}" for c in filtered])
    prompt = f"Summarize these {sentiment_type} T-Mobile customer comments in 4 lines or less:\n{joined}"
    return model.generate_content(prompt).text


# -------------------------------
# LOAD KEY + HTML
# -------------------------------
GEMINI_API_KEY = os.getenv("AIzaSyCA-l_rtWk3d8BiWsNkpPB517BL6UJwDbQ")  # hidden via .env
HTML_PATH = "savedDownDetectorPage.html"



with open(HTML_PATH, "r", encoding="utf-8") as f:
    html_content = f.read()

# -------------------------------
# ANALYSIS PIPELINE
# -------------------------------
st.markdown("<h1>MobileMoods: T-Mobile Customer Happiness Index</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-header'>Last updated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}</div>", unsafe_allow_html=True)

with st.spinner("🔍 Analyzing T-Mobile feedback..."):
    comments_json = scrape_downdetector(html_content)
    output = JsonTo2DList(comments_json, GEMINI_API_KEY)

    df = pd.DataFrame(output, columns=["username", "user_id", "comment_time", "comment", "sentiment", "reported_outages", "duplicate"])
    positive_count = len(df[df["sentiment"] == 1])
    negative_count = len(df[df["sentiment"] == -1])
    neutral_count = len(df[df["sentiment"] == 0])
    avg_sentiment = df["sentiment"].mean()

    bad_summary = summarize_feedback(output, GEMINI_API_KEY, "negative")
    good_summary = summarize_feedback(output, GEMINI_API_KEY, "positive")


# -------------------------------
# DASHBOARD UI
# -------------------------------
tab1, tab2, tab3 = st.tabs(["📊 Overview", "🤖 Insights", "💬 Reviews"])

# --- OVERVIEW TAB ---
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        ("Average Sentiment", f"{avg_sentiment:.2f}", ""),
        ("Total Reviews", f"{len(df)}", ""),
        ("Positive", f"{positive_count}", ""),
        ("Negative", f"{negative_count}", "")
    ]
    for col, (label, value, sub) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-sub">{sub}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
    sentiment_pie = px.pie(
        values=[positive_count, neutral_count, negative_count],
        names=["Positive", "Neutral", "Negative"],
        color=["Positive", "Neutral", "Negative"],
        color_discrete_map={"Positive": "#E20074", "Neutral": "#888", "Negative": "#333"}
    )
    sentiment_pie.update_layout(paper_bgcolor="#0d0d0f", font_color="white")
    st.plotly_chart(sentiment_pie, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- INSIGHTS TAB ---
with tab2:
    st.markdown("### 💡 AI-Generated Insights")
    st.markdown("#### 👍 Positive Feedback Summary")
    st.write(good_summary)
    st.markdown("#### ⚠️ Negative Feedback Summary")
    st.write(bad_summary)

# --- REVIEWS TAB ---
with tab3:
    st.markdown("### 💬 Individual Reviews")
    for _, row in df.iterrows():
        sentiment_label = "Positive" if row["sentiment"] == 1 else "Negative" if row["sentiment"] == -1 else "Neutral"
        st.markdown(f"**{row['username']}** — {sentiment_label} — *{row['comment']}*")
