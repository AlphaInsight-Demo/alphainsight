import streamlit as st
from openai import OpenAI
import json
from styles import get_custom_css

# --- 1. 页面基本配置 ---
st.set_page_config(
    page_title="AlphaInsight | AI 金融情报局",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入自定义样式
st.markdown(get_custom_css(), unsafe_allow_html=True)

# --- 2. 安全获取 API Key ---
# 自动从 Streamlit 后台 Secrets 读取，无需用户干预
try:
    DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
except Exception:
    st.error("❌ 错误：未检测到 API Key。请在 Streamlit Cloud 后台 Secrets 中配置 DEEPSEEK_API_KEY。")
    st.stop()

# --- 3. 侧边栏 ---
with st.sidebar:
    st.title("🛡️ AlphaInsight")
    st.markdown("---")
    model_choice = st.selectbox(
        "AI 分析引擎", 
        ["deepseek-chat", "deepseek-reasoner"],
        help="deepseek-reasoner (R1) 适合分析极其复杂的金融逻辑"
    )
    st.success("API 状态: 已连接")
    st.divider()
    st.markdown("""
    **关于本工具**
    AlphaInsight 利用 DeepSeek 大模型实时分析市场异动，捕捉非对称信息。
    """)
    st.caption("版本: v1.0.2 | 开发者已预付额度")

# --- 4. AI 逻辑处理函数 ---
def analyze_financial_data(content):
    prompt = f"""
    你是一个拥有20年经验的顶级量化基金分析师。
    请分析以下新闻或研报，并严格以 JSON 格式输出：
    {{
        "summary": "一句话核心结论",
        "sentiment": "Bullish / Bearish / Neutral",
        "logic": "深层因果链推导，100字以内",
        "tickers": ["股票代码1", "股票代码2"],
        "impact_score": 1-10之间的数字
    }}
    
    待处理内容: {content}
    """
    
    try:
        response = client.chat.completions.create(
            model=model_choice,
            messages=[
                {"role": "system", "content": "你只输出 JSON 格式的专业金融分析报告。"},
                {"role": "user", "content": prompt}
            ],
            response_format={'type': 'json_object'}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"AI 分析失败: {str(e)}")
        return None

# --- 5. UI 主界面 ---
st.title("📈 实时“阿尔法”信号看板")

# 顶部数据指标
c1, c2, c3, c4 = st.columns(4)
c1.metric("监测资产", "1,200+", "Global")
c2.metric("多头信号", "28", "Bullish")
c3.metric("空头信号", "14", "-5", delta_color="inverse")
c4.metric("AI 推理深度", "High", "98.2%")

st.divider()

tab1, tab2 = st.tabs(["🔥 实时异动流", "📄 深度研报解析"])

with tab1:
    # 模拟新闻源
    mock_news = [
        "英伟达(NVDA)Blackwell芯片良率提升，预计Q4出货量将超出此前预期30%。",
        "由于地缘冲突加剧，国际油价大幅跳水，WTI原油跌破70美元大关。",
        "OpenAI发布新款模型，对算力需求暴增，电力能源股近期获机构大量加仓。"
    ]
    
    st.subheader("最新捕捉情报")
    for news in mock_news:
        with st.expander(f"🔔 {news[:45]}...", expanded=False):
            if st.button("开始 AI 诊断", key=news[:10]):
                with st.spinner("DeepSeek 正在构建逻辑图谱..."):
                    res = analyze_financial_data(news)
                    if res:
                        sentiment_color = "#00FFBD" if res['sentiment'] == "Bullish" else "#FF3B6A" if res['sentiment'] == "Bearish" else "#888888"
                        st.markdown(f"""
                        <div class="alpha-card sentiment-{res['sentiment'].lower()}">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <h3 style="margin:0; color:{sentiment_color};">{res['sentiment']}</h3>
                                <span style="font-size: 1.2rem; font-weight: bold;">影响分: {res['impact_score']}/10</span>
                            </div>
                            <div style="font-size: 1.1rem; font-weight: 600; margin: 10px 0;">{res['summary']}</div>
                            <div class="logic-text"><strong>逻辑推导：</strong>{res['logic']}</div>
                            <div style="margin-top: 15px;">
                                {' '.join([f'<span class="ticker-tag">${t}</span>' for t in res['tickers']])}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

with tab2:
    st.subheader("专业分析模式")
    doc_input = st.text_area("在此粘贴长篇研报、公告或市场快讯...", height=250, placeholder="例如：输入某公司的 Q3 财报摘要...")
    
    if st.button("生成深度洞见报告", use_container_width=True):
        if doc_input:
            with st.spinner("AI 正在通过推理模型分析基本面变化..."):
                res = analyze_financial_data(doc_input)
                if res:
                    st.balloons()
                    st.subheader("AI 诊断结论")
                    st.json(res)
        else:
            st.warning("请输入需要分析的内容")

# --- 6. 页脚 ---
st.markdown("---")
st.caption("AlphaInsight Pro | 基于 DeepSeek V3/R1 驱动 | 投资有风险，决策需谨慎")
