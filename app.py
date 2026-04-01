import streamlit as st
import openai
import json
from duckduckgo_search import DDGS
import time

# 页面配置
st.set_page_config(page_title="AlphaInsight Intelligence", layout="wide", page_icon="🌐")

# 1. 从 Secrets 读取 Key
if "DEEPSEEK_API_KEY" in st.secrets:
    default_api_key = st.secrets["DEEPSEEK_API_KEY"]
else:
    default_api_key = ""

# --- 核心功能函数：联网搜索（增加重试和错误处理） ---
def fetch_latest_news(keyword):
    """通过 DuckDuckGo 搜索最近的财经新闻"""
    try:
        with DDGS() as ddgs:
            # 增加 region 参数尝试获取更精准的中文结果
            results = [r for r in ddgs.news(keyword, region="cn-zh", safesearch="off", timelimit="d", max_results=5)]
        
        if not results:
            return "未搜寻到相关近期新闻。"
        
        news_context = ""
        for i, r in enumerate(results):
            news_context += f"新闻{i+1}: {r['title']}\n摘要: {r['body']}\n\n"
        return news_context
    except Exception as e:
        if "Ratelimit" in str(e):
            return "ERROR_LIMIT: 搜索请求过于频繁，被搜索引擎暂时限流，请1分钟后再试，或改用手动粘贴功能。"
        return f"搜索出错: {str(e)}"

# 页面标题
st.title("🚀 AlphaInsight Pro: 全球情报实时分析")
st.markdown("---")

# 侧边栏
with st.sidebar:
    st.header("⚙️ 系统设置")
    user_key = st.text_input("DeepSeek API Key", value=default_api_key, type="password")

# 主界面布局
col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.subheader("📥 第一步：获取分析素材")
    tab1, tab2 = st.tabs(["🔍 自动采集", "📄 手动粘贴"])
    
    with tab1:
        search_keyword = st.text_input("输入关键词 (如：公司名、板块、宏观事件)", placeholder="例如：美伊战争、英伟达财报...")
        analyze_search_btn = st.button("全网搜寻并分析", type="primary", use_container_width=True)
    
    with tab2:
        news_input = st.text_area("在此粘贴原始文本：", height=250)
        analyze_text_btn = st.button("直接分析上方文本", use_container_width=True)

# 统一分析逻辑
final_context = ""
trigger = False

if analyze_search_btn and search_keyword:
    with st.spinner(f'正在搜寻 "{search_keyword}" 的最新动态...'):
        res = fetch_latest_news(search_keyword)
        if "ERROR_LIMIT" in res:
            st.error(res)
        else:
            final_context = res
            trigger = True
elif analyze_text_btn and news_input:
    final_context = news_input
    trigger = True

with col_right:
    st.subheader("📋 第二步：结构化分析报告")
    
    if trigger:
        try:
            client = openai.OpenAI(api_key=user_key, base_url="https://api.deepseek.com")
            with st.spinner('AI 正在深度研判...'):
                # 修改 Prompt，强制 AI 使用 Markdown 换行和排版
                prompt = f"""
                你是一名顶级金融分析师。请分析以下新闻，并以 JSON 格式输出报告。
                
                【要求】:
                1. logic 字段的内容必须使用 Markdown 格式。
                2. 必须使用加粗(**关键词**)和换行符(\\n\\n)来分段。
                3. 每条逻辑观点单独成段，不要挤在一起。
                
                输出 JSON 模板:
                {{
                    "subject": ["主体1", "主体2"],
                    "sentiment": "看多/看空/中性",
                    "logic": "**1. 核心影响因素**\\n\\n这里是详细描述...\\n\\n**2. 产业链传导**\\n\\n这里是描述...",
                    "impact_score": 7,
                    "risk_tip": "风险提示"
                }}
                
                情报内容： {final_context}
                """

                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={ "type": "json_object" }
                )
                result = json.loads(response.choices[0].message.content)
                
                # 展示区
                m1, m2 = st.columns(2)
                with m1:
                    color = "🔴" if "空" in result.get('sentiment') else "🟢"
                    st.metric("综合情绪", f"{color} {result.get('sentiment')}")
                with m2:
                    st.metric("影响力", f"{result.get('impact_score')} /
