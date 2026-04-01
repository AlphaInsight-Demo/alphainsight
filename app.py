import streamlit as st
import openai
import json
from duckduckgo_search import DDGS

# 页面配置
st.set_page_config(page_title="AlphaInsight Intelligence", layout="wide", page_icon="🌐")

# 1. 从 Secrets 读取 Key
if "DEEPSEEK_API_KEY" in st.secrets:
    default_api_key = st.secrets["DEEPSEEK_API_KEY"]
else:
    default_api_key = ""

# --- 核心功能函数：联网搜索 ---
def fetch_latest_news(keyword):
    """通过 DuckDuckGo 搜索最近的财经新闻"""
    with DDGS() as ddgs:
        # 搜索最近一天的相关财经信息，取前5条
        results = [r for r in ddgs.news(keyword, region="cn-zh", safesearch="off", timelimit="d", max_results=5)]
    
    if not results:
        return "未搜寻到相关近期新闻。"
    
    # 将搜索结果组合成一段文本供 AI 分析
    news_context = ""
    for i, r in enumerate(results):
        news_context += f"新闻{i+1}: {r['title']}\n摘要: {r['body']}\n来源: {r['source']}\n\n"
    return news_context

# 页面标题
st.title("🚀 AlphaInsight Pro: 全球情报实时分析")
st.markdown("---")

# 侧边栏
with st.sidebar:
    st.header("⚙️ 系统设置")
    user_key = st.text_input("DeepSeek API Key", value=default_api_key, type="password")
    st.divider()
    st.markdown("### 常用追踪词")
    hot_key = st.selectbox("快速选择关键词", ["", "半导体板块异动", "美联储降息预期", "黄金价格走势", "新能源车出海", "比特币链上异动"])

# 主界面布局
col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.subheader("📥 第一步：获取分析素材")
    
    tab1, tab2, tab3 = st.tabs(["🔍 自动采集", "📄 手动粘贴", "🖼️ 图片识别"])
    
    with tab1:
        search_keyword = st.text_input("输入关键词 (如：公司名、板块、宏观事件)", value=hot_key)
        analyze_search_btn = st.button("全网搜寻并分析", type="primary", use_container_width=True)
    
    with tab2:
        news_input = st.text_area("在此粘贴原始文本：", height=250)
        analyze_text_btn = st.button("直接分析上方文本", use_container_width=True)
    
    with tab3:
        st.info("注：DeepSeek-V3 暂不支持直接图片识别，建议在此上传后手动提取文字，或切换至 GPT-4o 模型。")
        uploaded_file = st.file_uploader("上传截图", type=["jpg", "png"])

# 统一分析逻辑
final_context = ""
trigger = False

if analyze_search_btn and search_keyword:
    with st.spinner(f'正在全网搜索关于 "{search_keyword}" 的最新情报...'):
        final_context = fetch_latest_news(search_keyword)
        st.write("✅ 已采集到最新 5 条相关情报")
        with st.expander("点击查看采集到的原始内容"):
            st.write(final_context)
    trigger = True
elif analyze_text_btn and news_input:
    final_context = news_input
    trigger = True

with col_right:
    st.subheader("📋 第二步：结构化分析报告")
    
    if trigger:
        if not user_key:
            st.error("请在左侧设置有效的 API Key")
        else:
            try:
                client = openai.OpenAI(api_key=user_key, base_url="https://api.deepseek.com")
                
                with st.spinner('AI 正在深度研判情报逻辑...'):
                    prompt = f"""
                    你是一名顶级金融分析师。请分析以下搜集到的新闻情报，并以 JSON 格式输出深度报告。
                    注意：如果有多条新闻，请综合研判它们之间的内在关联。
                    输出格式：
                    {{
                        "subject": ["受影响主体1", "主体2"],
                        "sentiment": "看多/看空/中性",
                        "logic": "基于最新搜集到的情报，进行穿透式逻辑分析",
                        "impact_score": 7,
                        "risk_tip": "一句话风险提示"
                    }}
                    情报内容： {final_context}
                    """

                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "user", "content": prompt}],
                        response_format={ "type": "json_object" }
                    )
                    result = json.loads(response.choices[0].message.content)
                    
                    # 漂亮的展示
                    m1, m2 = st.columns(2)
                    with m1:
                        color_emoji = "🔴" if "空" in result.get('sentiment') else "🟢"
                        st.metric("综合情绪评级", f"{color_emoji} {result.get('sentiment')}")
                    with m2:
                        st.metric("市场影响力", f"{result.get('impact_score')} / 10")
                    
                    st.divider()
                    st.markdown("**🎯 受影响标的/领域：**")
                    subjects = result.get('subject', [])
                    cols = st.columns(len(subjects) if subjects else 1)
                    for i, s in enumerate(subjects):
                        cols[i].info(f"**{s}**")

                    st.markdown("**💡 深度逻辑透视：**")
                    st.success(result.get('logic'))
                    st.markdown("**⚠️ 风险提示：**")
                    st.warning(result.get('risk_tip', '市场有风险，投资需谨慎'))
            except Exception as e:
                st.error(f"分析出错: {str(e)}")
    else:
        st.info("请在左侧选择采集方式。建议尝试『自动采集』以获取实时市场动态。")
