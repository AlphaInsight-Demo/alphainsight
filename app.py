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

# --- 核心功能函数：联网搜索 ---
def fetch_latest_news(keyword):
    """通过 DuckDuckGo 搜索最近的财经新闻"""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.news(keyword, region="cn-zh", safesearch="off", timelimit="d", max_results=5)]
        
        if not results:
            return "未搜寻到相关近期新闻。"
        
        news_context = ""
        for i, r in enumerate(results):
            news_context += f"新闻{i+1}: {r['title']}\n摘要: {r['body']}\n\n"
        return news_context
    except Exception as e:
        if "Ratelimit" in str(e):
            return "ERROR_LIMIT"
        return f"搜索出错: {str(e)}"

# 页面标题
st.title("🚀 AlphaInsight Pro: 全球情报实时分析")
st.markdown("---")

# 侧边栏
with st.sidebar:
    st.header("⚙️ 系统设置")
    user_key = st.text_input("DeepSeek API Key", value=default_api_key, type="password")
    st.info("💡 提示：如果自动采集失败，请尝试手动粘贴新闻文本。")

# 主界面布局
col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.subheader("📥 第一步：获取分析素材")
    tab1, tab2 = st.tabs(["🔍 自动采集", "📄 手动粘贴"])
    
    with tab1:
        search_keyword = st.text_input("输入关键词 (如：公司名、板块、宏观事件)", placeholder="例如：半导体、英伟达财报...")
        analyze_search_btn = st.button("全网搜寻并分析", type="primary", use_container_width=True)
    
    with tab2:
        news_input = st.text_area("在此粘贴原始文本：", height=300, placeholder="粘贴路透社、彭博社或其他新闻...")
        analyze_text_btn = st.button("直接分析上方文本", use_container_width=True)

# 统一分析逻辑
final_context = ""
trigger = False

if analyze_search_btn and search_keyword:
    with st.spinner(f'正在搜寻 "{search_keyword}" 的最新动态...'):
        res = fetch_latest_news(search_keyword)
        if res == "ERROR_LIMIT":
            st.error("⚠️ 搜索引擎流量过大，请1分钟后再试，或改用『手动粘贴』功能。")
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
            with st.spinner('AI 正在深度研判中...'):
                # 强化 Prompt，要求 AI 必须分段
                prompt = f"""
                你是一名资深金融分析师。请分析以下新闻情报，并以 JSON 格式输出。
                要求：
                1. 'logic' 字段必须使用 Markdown 格式，且必须包含换行符(\\n\\n)分段。
                2. 重要结论请使用 **加粗**。
                3. 请使用 1. 2. 3. 这种列表序号。
                
                输出格式示例：
                {{
                    "subject": ["标的1", "标的2"],
                    "sentiment": "看多/看空",
                    "logic": "1. **核心驱动**\\n\\n详细分析...\\n\\n2. **传导逻辑**\\n\\n详细分析...",
                    "impact_score": 8,
                    "risk_tip": "注意XX风险"
                }}
                新闻内容： {final_context}
                """

                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={ "type": "json_object" }
                )
                result = json.loads(response.choices[0].message.content)
                
                # --- 修复后的展示部分 ---
                m1, m2 = st.columns(2)
                with m1:
                    color = "🔴" if "空" in result.get('sentiment', '') else "🟢"
                    st.metric("综合情绪", f"{color} {result.get('sentiment')}")
                with m2:
                    # 修正了之前的语法错误行
                    st.metric("影响力评分", f"{result.get('impact_score')} / 10")
                
                st.divider()
                
                st.markdown("**🎯 受影响标的：**")
                subjects = result.get('subject', [])
                st.write(", ".join([f"`{s}`" for s in subjects]))

                st.markdown("**💡 深度逻辑透视：**")
                # 使用 markdown 呈现，AI 生成的 \n\n 会变成真正的换行
                st.markdown(result.get('logic', '无分析内容'))

                st.divider()
                st.markdown("**⚠️ 风险提示：**")
                st.warning(result.get('risk_tip', '谨慎操作'))
                
        except Exception as e:
            st.error(f"分析出错: {str(e)}")
    else:
        st.info("💡 请在左侧选择数据来源。建议尝试『自动采集』以获取实时情报。")
