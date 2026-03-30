import streamlit as st
import openai
import json

# 页面配置
st.set_page_config(page_title="AlphaInsight", layout="wide")

# --- 核心：从 Secrets 读取 Key ---
# 如果在本地运行或没设 Secret，会报错，这里做个保护
if "DEEPSEEK_API_KEY" in st.secrets:
    default_api_key = st.secrets["DEEPSEEK_API_KEY"]
else:
    default_api_key = ""

st.title("🚀 AlphaInsight: 金融超额收益分析系统")

# 侧边栏
with st.sidebar:
    st.header("系统设置")
    # 如果 Secrets 有 Key，就默认使用它，用户不需要手动输入
    user_key = st.text_input("API Key (已自动加载)", value=default_api_key, type="password")
    st.info("💡 提示：本应用已预设 DeepSeek 算力支持。")

# 主界面
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("第1步：输入财经新闻/研报")
    news_input = st.text_area("在此粘贴原始文本：", height=300)
    analyze_btn = st.button("开始 AI 逻辑穿透", type="primary")

with col2:
    st.subheader("第2步：AI 结构化信号")
    if analyze_btn:
        if not user_key:
            st.error("未发现有效 API Key")
        else:
            try:
                # 注意：这里配置了 DeepSeek 的地址
                client = openai.OpenAI(api_key=user_key, base_url="https://api.deepseek.com")
                
                with st.spinner('AI 正在深度思考...'):
                    prompt = "你是一名资深量化分析师，分析以下新闻，输出JSON格式：subject(受影响主体), sentiment(看多/看空/中性), logic(投资逻辑), impact_score(1-10)。新闻： " + news_input
                    
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "user", "content": prompt}],
                        response_format={ "type": "json_object" }
                    )
                    result = json.loads(response.choices[0].message.content)
                    
                    st.success("分析完成！")
                    st.json(result)
                    st.metric("核心情绪", result.get('sentiment'))
                    st.write(f"**深度逻辑：** {result.get('logic')}")
            except Exception as e:
                st.error(f"分析出错: {str(e)}")
