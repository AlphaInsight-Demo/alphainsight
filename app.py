import streamlit as st
from openai import OpenAI
import json

# --- 1. 强力 CSS 注入 (直接写在 app.py 确保 100% 加载) ---
def inject_super_css():
    st.markdown("""
    <style>
    /* 强制全局深色背景 */
    [data-testid="stAppViewContainer"], .main, .stApp {
        background-color: #0E1117 !important;
        color: #FFFFFF !important;
    }
    
    /* 顶部导航和线条隐藏 */
    header, [data-testid="stHeader"] { visibility: hidden; }

    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background-color: #161B22 !important;
        border-right: 1px solid #30363D;
    }

    /* 自定义 Bento Box 指标卡片 */
    .bento-container {
        display: flex;
        flex-direction: row;
        gap: 15px;
        margin: 20px 0;
        width: 100%;
    }
    
    .bento-card {
        background: #1C2128;
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 20px;
        flex: 1;
        min-width: 150px;
        transition: all 0.3s ease;
    }
    
    .bento-card:hover {
        border: 1px solid #00FFA3;
        box-shadow: 0 0 15px rgba(0, 255, 163, 0.1);
    }

    .bento-label {
        color: #8B949E;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }

    .bento-value {
        color: #F0F6FC;
        font-size: 24px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }

    /* 信号卡片样式 */
    .signal-card {
        background: #161B22;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid #30363D;
    }
    .bullish-border { border-left: 4px solid #00FFA3; }
    .bearish-border { border-left: 4px solid #FF4B4B; }
    
    .summary-text {
        font-size: 18px;
        font-weight: 600;
        color: #F0F6FC;
        margin-bottom: 10px;
    }

    .logic-box {
        background: #0D1117;
        padding: 12px;
        border-radius: 6px;
        color: #C9D1D9;
        font-size: 14px;
        border: 1px solid #30363D;
    }

    /* 标签样式 */
    .ticker-tag {
        background: rgba(0, 255, 163, 0.1);
        color: #00FFA3;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        margin-right: 5px;
        border: 1px solid rgba(0, 255, 163, 0.2);
    }
    
    /* 修正 Tab 颜色 */
    .stTabs [data-baseweb="tab-list"] button {
        color: #8B949E !important;
    }
    .stTabs [aria-selected="true"] {
        color: #00FFA3 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 页面逻辑 ---
st.set_page_config(page_title="AlphaInsight Pro", layout="wide")
inject_super_css()

# API 配置 (从 Secrets 获取)
api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com") if api_key else None

# --- 3. 侧边栏 ---
with st.sidebar:
    st.title("🛡️ AlphaInsight")
    st.markdown("---")
    model_choice = st.selectbox("核心大脑", ["deepseek-chat", "deepseek-reasoner"])
    st.info("💡 状态: API 已连接")
    st.caption("开发者已充值额度")

# --- 4. 顶部横向 Bento Box ---
# 这里使用 HTML 拼接，确保它一定是横向的
st.markdown("""
<div class="bento-container">
    <div class="bento-card">
        <div class="bento-label">监测资产</div>
        <div class="bento-value">1,248</div>
    </div>
    <div class="bento-card">
        <div class="bento-label">多头信号</div>
        <div class="bento-value" style="color:#00FFA3;">32</div>
    </div>
    <div class="bento-card">
        <div class="bento-label">空头信号</div>
        <div class="bento-value" style="color:#FF4B4B;">14</div>
    </div>
    <div class="bento-card">
        <div class="bento-label">AI 信心指数</div>
        <div class="bento-value">98.2%</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("") # 留白

# --- 5. AI 分析函数 ---
def analyze_news(text):
    if not client: return None
    prompt = f"分析此新闻，输出 JSON: summary, sentiment(Bullish/Bearish), logic, tickers, score(1-10). 内容: {text}"
    try:
        response = client.chat.completions.create(
            model=model_choice,
            messages=[{"role": "user", "content": prompt}],
            response_format={'type': 'json_object'}
        )
        return json.loads(response.choices[0].message.content)
    except: return None

# --- 6. 主内容区 ---
tab1, tab2 = st.tabs(["🔥 实时异动流", "📄 深度研报解析"])

with tab1:
    mock_news = [
        "英伟达(NVDA)Blackwell芯片良率提升，预计Q4出货量将超出此前预期30%。",
        "由于地缘冲突加剧，国际油价大幅跳水，WTI原油跌破70美元大关。",
        "OpenAI发布新款模型，对算力需求暴增，电力能源股近期获机构大量加仓。"
    ]
    
    for news in mock_news:
        with st.expander(f"📌 {news[:50]}...", expanded=False):
            if st.button("运行诊断", key=news[:20]):
                with st.spinner("AI 正在推理..."):
                    res = analyze_news(news)
                    if res:
                        b_class = "bullish-border" if res['sentiment'] == "Bullish" else "bearish-border"
                        st.markdown(f"""
                        <div class="signal-card {b_class}">
                            <div class="summary-text">{res['summary']}</div>
                            <div class="logic-box"><strong>分析推导：</strong>{res['logic']}</div>
                            <div style="margin-top:15px; display:flex; justify-content:space-between; align-items:center;">
                                <div>{" ".join([f'<span class="ticker-tag">{t}</span>' for t in res['tickers']])}</div>
                                <div style="color:#8B949E; font-size:12px;">影响力评分: {res['score']}/10</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

with tab2:
    text_input = st.text_area("粘贴长文分析...", height=200)
    if st.button("生成报告"):
        res = analyze_news(text_input)
        if res: st.json(res)

st.markdown("<div style='text-align:center; color:#484F58; padding:20px;'>AlphaInsight Pro | Quant Terminal v1.1</div>", unsafe_allow_html=True)
