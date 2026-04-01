import streamlit as st
from openai import OpenAI
import json
from styles import get_custom_css

# --- 初始化配置 ---
st.set_page_config(page_title="AlphaInsight | AI 金融情报局", layout="wide")
st.markdown(get_custom_css(), unsafe_allow_html=True)

# --- 侧边栏配置 ---
with st.sidebar:
    st.title("🛡️ AlphaInsight")
    st.subheader("参数设置")
    api_key = st.text_input("DeepSeek API Key", type="password")
    model_choice = st.selectbox("选择模型", ["deepseek-chat", "deepseek-reasoner"])
    st.divider()
    st.info("AlphaInsight 利用 LLM 提取市场非对称信息。")

# 检查 API Key
if not api_key:
    st.warning("请在侧边栏输入 DeepSeek API Key 以启用 AI 分析。")
    client = None
else:
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# --- 模拟数据源 (实际开发可对接 API) ---
mock_news = [
    "英伟达(NVDA)宣布推出新款 Blackwell 芯片，预计 Q4 大规模出货，分析师上调目标价至150美元。",
    "受地缘政治影响，智利多家锂矿宣布因罢工减产，全球锂供应预计缩减 15%。",
    "美联储最新会议纪要暗示，由于通胀数据仍具韧性，降息节奏可能慢于市场预期。"
]

# --- AI 分析函数 ---
def analyze_news(text):
    if not client: return None
    
    prompt = f"""
    作为顶级金融分析师，分析以下新闻并以 JSON 格式输出。
    JSON 键名: 
    - summary: 一句话核心摘要
    - sentiment: 必须是 "Bullish", "Bearish", 或 "Neutral" 
    - impact_logic: 逻辑推导
    - tickers: 涉及的股票代码列表
    - alpha_score: 影响力评分 (1-10)

    新闻内容: {text}
    """
    
    try:
        response = client.chat.completions.create(
            model=model_choice,
            messages=[{"role": "system", "content": "你是一个精通全球资产关联的金融专家。"},
                      {"role": "user", "content": prompt}],
            response_format={'type': 'json_object'}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"AI 分析出错: {e}")
        return None

# --- UI 布局 ---

st.title("📈 实时“阿尔法”信号流")

# 顶部看板
col1, col2, col3, col4 = st.columns(4)
col1.metric("今日处理情报", "128 条", "+12%")
col2.metric("多头信号", "45", "Bullish", delta_color="normal")
col3.metric("空头信号", "12", "Bearish", delta_color="inverse")
col4.metric("AI 信心指数", "88%", "Stable")

st.divider()

# 主内容区
tab1, tab2 = st.tabs(["🔥 实时异动分析", "📄 深度研报解析"])

with tab1:
    st.subheader("最新捕捉到的信号")
    
    for news in mock_news:
        if st.button(f"分析此条: {news[:40]}..."):
            with st.spinner('DeepSeek 正在解析逻辑链...'):
                result = analyze_news(news)
                if result:
                    sentiment_class = f"sentiment-{result['sentiment'].lower()}"
                    
                    # 渲染信号卡片
                    st.markdown(f"""
                    <div class="alpha-card {sentiment_class}">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="font-weight: bold; font-size: 1.2rem;">{result['summary']}</span>
                            <span style="color: {'#00FFBD' if result['sentiment']=='Bullish' else '#FF3B6A'}">{result['sentiment']}</span>
                        </div>
                        <p style="margin-top: 10px; color: #BDC1C6;">{result['impact_logic']}</p>
                        <div style="margin-top: 10px;">
                            {' '.join([f'<span class="ticker-tag">${t}</span>' for t in result['tickers']])}
                            <span style="float: right; font-size: 0.8rem; color: #888;">影响力指数: {result['alpha_score']}/10</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

with tab2:
    st.subheader("上传研报/长文分析")
    doc_text = st.text_area("粘贴公司财报草稿或宏观快讯", height=200)
    if st.button("开始深度扫描"):
        if doc_text:
            with st.spinner('正在分析长文本结构...'):
                # 这里的逻辑可以调用同样的 analyze_news 或专门的长文本处理逻辑
                res = analyze_news(doc_text)
                if res:
                    st.success("分析完成")
                    st.json(res)
        else:
            st.warning("请输入内容")

# --- 页脚 ---
st.markdown("---")
st.caption("免责声明：AI 自动生成内容仅供参考，不构成任何投资建议。数据采集自公开网络。")
