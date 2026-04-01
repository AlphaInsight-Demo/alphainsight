import streamlit as st
import openai
import json
from tavily import TavilyClient

# --- 1. 页面配置与自定义样式 ---
st.set_page_config(page_title="AlphaInsight Pro", layout="wide", page_icon="🚀")

# 自定义 CSS：解决字号和背景问题
st.markdown("""
    <style>
    /* 逻辑分析框的背景样式 */
    .logic-container {
        background-color: #f0f7ff;
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid #1e88e5;
        color: #1a1a1a;
        line-height: 1.7;
    }
    /* 受影响标的的文字样式 */
    .target-tag {
        display: inline-block;
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 6px 15px;
        border-radius: 20px;
        font-size: 20px !important; /* 这里调大字号 */
        font-weight: bold;
        margin-right: 10px;
        margin-bottom: 10px;
        border: 1px solid #c8e6c9;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 密钥读取 ---
deepseek_key = st.secrets.get("DEEPSEEK_API_KEY", "")
tavily_key = st.secrets.get("TAVILY_API_KEY", "")

def fetch_latest_news_pro(keyword):
    if not tavily_key: return "ERROR_NO_KEY"
    try:
        tavily = TavilyClient(api_key=tavily_key)
        response = tavily.search(query=keyword, search_depth="basic", max_results=3)
        results = response.get('results', [])
        if not results: return "未搜寻到相关近期新闻。"
        context = ""
        for i, r in enumerate(results):
            context += f"【情报{i+1}】: {r['title']}\n内容: {r['content']}\n\n"
        return context
    except Exception as e:
        return f"搜索出错: {str(e)}"

# --- 3. UI 布局 ---
st.title("🚀 AlphaInsight Pro: 全球情报实时分析")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ 系统设置")
    user_key = st.text_input("DeepSeek API Key", value=deepseek_key, type="password")

col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.subheader("📥 获取分析素材")
    tab1, tab2 = st.tabs(["🔍 自动采集", "📄 手动粘贴"])
    with tab1:
        search_keyword = st.text_input("输入关键词", placeholder="例如：美伊战争、英伟达财报...")
        analyze_search_btn = st.button("全网搜寻并分析", type="primary", use_container_width=True)
    with tab2:
        news_input = st.text_area("在此粘贴文本：", height=300)
        analyze_text_btn = st.button("直接分析上方文本", use_container_width=True)

# 触发逻辑
final_context = ""
if analyze_search_btn and search_keyword:
    with st.status("🚀 正在采集情报...", expanded=False) as status:
        final_context = fetch_latest_news_pro(search_keyword)
        status.update(label="采集完成！", state="complete")
elif analyze_text_btn and news_input:
    final_context = news_input

with col_right:
    st.subheader("📋 结构化分析报告")
    
    if final_context:
        try:
            client = openai.OpenAI(api_key=user_key, base_url="https://api.deepseek.com")
            
            # 1. 先让 AI 提取标的（不流式，直接出，为了大字号排版）
            with st.spinner('提取核心标的...'):
                tag_res = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": f"请从以下内容提取受影响的具体资产或主体名称，仅返回名称，逗号分隔：{final_context}"}]
                )
                tags = tag_res.choices[0].message.content.split(',')
                
                st.markdown("**🎯 核心受影响标的：**")
                tag_html = ""
                for t in tags:
                    tag_html += f'<span class="target-tag">{t.strip()}</span>'
                st.markdown(tag_html, unsafe_allow_html=True)
            
            st.divider()

            # 2. 流式生成深度逻辑（带背景色）
            st.markdown("**💡 深度逻辑透视：**")
            logic_placeholder = st.empty()
            
            prompt = f"你是一名资深金融分析师。请针对以下内容，直接输出专业深度分析。要求分段、使用1.2.3.序号。情报内容：{final_context}"
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    # 动态包裹在带背景的 div 中
                    logic_placeholder.markdown(f'<div class="logic-container">{full_response}▌</div>', unsafe_allow_html=True)
            
            # 最终渲染（去掉光标）
            logic_placeholder.markdown(f'<div class="logic-container">{full_response}</div>', unsafe_allow_html=True)
            st.success("✅ 研判任务已执行完毕")

        except Exception as e:
            st.error(f"分析出错: {str(e)}")
    else:
        st.info("💡 等待数据输入...")
