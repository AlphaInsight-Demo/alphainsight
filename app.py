import streamlit as st
import openai
import json

# 页面配置
st.set_page_config(page_title="AlphaInsight", layout="wide", page_icon="🚀")

# 1. 从 Secrets 读取 Key (如果设置了 Secrets，用户点开即用)
if "DEEPSEEK_API_KEY" in st.secrets:
    default_api_key = st.secrets["DEEPSEEK_API_KEY"]
else:
    default_api_key = ""

# 自定义 CSS 样式
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 AlphaInsight: 金融超额收益分析系统")
st.markdown("---")

# 侧边栏：仅保留系统设置
with st.sidebar:
    st.header("⚙️ 系统设置")
    user_key = st.text_input("API Key", value=default_api_key, type="password")
    st.info("💡 提示：本应用已通过 DeepSeek 提供算力支持，直接粘贴新闻即可开始。")

# 主界面布局
col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.subheader("📥 第一步：输入新闻/研报文本")
    news_input = st.text_area("在此粘贴原始文本（如路透社、彭博社或公司公告）：", height=400, placeholder="在此粘贴内容...")
    analyze_btn = st.button("🔍 开始 AI 逻辑穿透", type="primary", use_container_width=True)

with col_right:
    st.subheader("📋 第二步：结构化分析报告")
    
    if analyze_btn:
        if not news_input:
            st.error("请输入内容后再点击分析")
        elif not user_key:
            st.error("请在左侧设置有效的 API Key")
        else:
            try:
                # 配置 DeepSeek 接口
                client = openai.OpenAI(api_key=user_key, base_url="https://api.deepseek.com")
                
                with st.spinner('AI 正在穿透市场噪音，请稍候...'):
                    prompt = """
                    你是一名顶级华尔街分析师。请分析以下新闻，并以 JSON 格式输出：
                    {
                        "subject": ["受影响主体1", "主体2"],
                        "sentiment": "看多/看空/中性",
                        "logic": "100字以内的深度逻辑分析",
                        "impact_score": 7,
                        "risk_tip": "一句话风险提示"
                    }
                    新闻内容： """ + news_input

                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "user", "content": prompt}],
                        response_format={ "type": "json_object" }
                    )
                    result = json.loads(response.choices[0].message.content)
                    
                    # --- 漂亮的展示部分 ---
                    
                    # 1. 顶部指标栏
                    m1, m2 = st.columns(2)
                    with m1:
                        # 情绪视觉化提示
                        color_emoji = "🔴" if "空" in result.get('sentiment') else "🟢"
                        st.metric("核心情绪评级", f"{color_emoji} {result.get('sentiment')}")
                    with m2:
                        st.metric("市场影响力指数", f"{result.get('impact_score')} / 10")
                    
                    st.divider()

                    # 2. 受影响主体 (以卡片形式展示)
                    st.markdown("**🎯 受影响标的/领域：**")
                    subjects = result.get('subject', [])
                    if subjects:
                        cols = st.columns(len(subjects))
                        for i, s in enumerate(subjects):
                            cols[i].info(f"**{s}**")

                    # 3. 深度逻辑
                    st.markdown("**💡 深度逻辑透视：**")
                    st.success(result.get('logic'))

                    # 4. 风险提示
                    st.markdown("**⚠️ 风险提示：**")
                    st.warning(result.get('risk_tip', '市场有风险，投资需谨慎'))

            except Exception as e:
                st.error(f"分析出错: {str(e)}")
    else:
        st.info("💡 准备就绪。请在左侧输入数据，分析结果将在此处以专业报告形式呈现。")
