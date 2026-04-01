import streamlit as st
from openai import OpenAI
import json
from styles import get_custom_css

# --- 1. 配置 ---
st.set_page_config(page_title="AlphaInsight Pro", layout="wide")
st.markdown(get_custom_css(), unsafe_allow_html=True)

# API 密钥获取
DEEPSEEK_API_KEY = st.secrets.get("DEEPSEEK_API_KEY", "")
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com") if DEEPSEEK_API_KEY else None

# --- 2. 侧边栏 ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2092/2092663.png", width=50) # 一个科技感Icon
    st.title("AlphaInsight")
    st.markdown("---")
    model_choice = st.selectbox("核心大脑", ["deepseek-chat", "deepseek-reasoner"])
    st.success("⚡ 系统就绪")

# --- 3. 顶部 Bento Box 指标 (解决看不清的问题) ---
st.markdown(f"""
<div class="metric-container">
    <div class="metric-card">
        <div class="metric-label">监测资产</div>
        <div class="metric-value">1,248</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">看多信号</div>
        <div class="metric-value" style="color: #00FFA3;">32</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">看空信号</div>
        <div class="metric-value" style="color: #FF4B4B;">14</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">AI 信心值</div>
        <div class="metric-value">98.2%</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 4. AI 处理函数 ---
def analyze_news(text):
    if not client: return None
    prompt = f"作为高级分析师，将此新闻转化为投资信号，严格按JSON输出: summary, sentiment(Bullish/Bearish/Neutral), logic, tickers, score(1-10). 内容: {text}"
    try:
        response = client.chat.completions.create(
            model=model_choice,
            messages=[{"role": "user", "content": prompt}],
            response_format={'type': 'json_object'}
        )
        return json.loads(response.choices[0].message.content)
    except: return None

# --- 5. 主内容区 ---
tab1, tab2 = st.tabs(["🔥 实时异动流", "📄 深度研报解析"])

with tab1:
    mock_news = [
        "Nvidia (NVDA) 宣布 Blackwell 架构 GPU 已进入全面量产阶段，市场预期大幅提升。",
        "地缘风险导致苏伊士运河航运再次受阻，原油及航运板块可能出现短期异动。",
        "美联储官员暗示下月可能暂停降息，美债收益率攀升至三个月高点。"
    ]
    
    for news in mock_news:
        with st.expander(f"📌 {news[:50]}...", expanded=False):
            if st.button("运行 AI 扫描", key=news[:20]):
                res = analyze_news(news)
                if res:
                    border_class = f"{res['sentiment'].lower()}-border"
                    st.markdown(f"""
                    <div class="alpha-card {border_class}">
                        <div class="summary-text">{res['summary']}</div>
                        <div class="logic-box"><strong>分析师逻辑：</strong>{res['logic']}</div>
                        <div style="margin-top:15px; display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                {" ".join([f'<span class="ticker-tag">{t}</span>' for t in res['tickers']])}
                            </div>
                            <div style="color:#8E9AAF; font-weight:bold;">评分: {res['score']}/10</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

with tab2:
    text_input = st.text_area("粘贴需要分析的金融长文...", height=300)
    if st.button("生成结构化深度报告"):
        if text_input:
            res = analyze_news(text_input)
            if res:
                st.json(res)

st.markdown("<br><center style='color:#4A5568;'>AlphaInsight Pro © 2024 高级量化分析终端</center>", unsafe_allow_html=True)
