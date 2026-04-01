import streamlit as st
import openai
import json
from tavily import TavilyClient

# 页面配置
st.set_page_config(page_title="AlphaInsight Pro", layout="wide", page_icon="🌐")

# 1. 从 Secrets 读取 Key
deepseek_key = st.secrets.get("DEEPSEEK_API_KEY", "")
tavily_key = st.secrets.get("TAVILY_API_KEY", "")

# --- 核心功能函数：专业级联网搜索 ---
def fetch_latest_news_pro(keyword):
    """通过 Tavily 搜索专业财经情报"""
    if not tavily_key:
        return "ERROR_NO_KEY: 请在 Secrets 中配置 TAVILY_API_KEY"
    
    try:
        tavily = TavilyClient(api_key=tavily_key)
        # search_depth="advanced" 可以搜得更深，针对金融分析非常有用
        response = tavily.search(query=keyword, search_depth="advanced", max_results=5)
        
        results = response.get('results', [])
        if not results:
            return "未搜寻到相关近期新闻。"
        
        news_context = ""
        for i, r in enumerate(results):
            # Tavily 会自动提取网页摘要 (content)
            news_context += f"情报{i+1}: {r['title']}\n摘要: {r['content']}\n\n"
        return news_context
    except Exception as e:
        return f"搜索出错: {str(e)}"

# 页面标题
st.title("🚀 AlphaInsight Pro: 全球情报实时分析")
st.markdown("---")

# 侧边栏
with st.sidebar:
    st.header("⚙️ 系统设置")
    user_key = st.text_input("DeepSeek API Key", value=deepseek_key, type="password")
    st.info("💡 当前已启用专业级 Tavily 搜索接口，稳定性提升 100%。")

# 主界面布局
col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.subheader("📥 第一步：获取分析素材")
    tab1, tab2 = st.tabs(["🔍 自动采集", "📄 手动粘贴"])
    
    with tab1:
        search_keyword = st.text_input("输入关键词 (如：公司名、板块、宏观事件)", placeholder="例如：美伊战争、英伟达财报...")
        analyze_search_btn = st.button("全网搜寻并分析", type="primary", use_container_width=True)
    
    with tab2:
        news_input = st.text_area("在此粘贴原始文本：", height=300, placeholder="粘贴新闻文本...")
        analyze_text_btn = st.button("直接分析上方文本", use_container_width=True)

# 统一分析逻辑
final_context = ""
trigger = False

if analyze_search_btn and search_keyword:
    with st.spinner(f'🚀 正在调用全球情报网搜寻 "{search_keyword}"...'):
        res = fetch_latest_news_pro(search_keyword)
        if "ERROR_NO_KEY" in res:
            st.error("❌ 尚未配置 TAVILY_API_KEY，请检查 Secrets。")
        elif "搜索出错" in res:
            st.error(f"❌ {res}")
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
                prompt = f"""
                你是一名顶级金融分析师。请分析以下新闻情报，并以 JSON 格式输出报告。
                要求：
                1. 'logic' 字段必须使用 Markdown 格式，必须包含换行符(\\n\\n)分段。
                2. 重要结论请使用 **加粗**。
                
                输出格式示例：
                {{
                    "subject": ["主体1", "主体2"],
                    "sentiment": "看多/看空/中性",
                    "logic": "**1. 核心影响因素**\\n\\n具体描述...\\n\\n**2. 产业链传导**\\n\\n具体描述...",
                    "impact_score": 8,
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
                
                # --- 漂亮的展示部分 ---
                m1, m2 = st.columns(2)
                with m1:
                    color = "🔴" if "空" in result.get('sentiment', '') else "🟢"
                    st.metric("综合情绪", f"{color} {result.get('sentiment')}")
                with m2:
                    st.metric("影响力评分", f"{result.get('impact_score')} / 10")
                
                st.divider()
                st.markdown("**🎯 受影响标的：**")
                st.write(", ".join([f"`{s}`" for s in result.get('subject', [])]))

                st.markdown("**💡 深度逻辑透视：**")
                st.markdown(result.get('logic', ''))

                st.divider()
                st.markdown("**⚠️ 风险提示：**")
                st.warning(result.get('risk_tip', '谨慎操作'))
                
        except Exception as e:
            st.error(f"分析出错: {str(e)}")
    else:
        st.info("💡 建议使用『自动采集』获取全球最新情报。")
