import streamlit as st
import openai
import json

# 页面配置
st.set_page_config(page_title="AlphaInsight AI 投研看板", layout="wide")

st.title("🚀 AlphaInsight: 金融超额收益分析系统")
st.caption("利用大语言模型穿透市场噪音，提取核心投资逻辑")

# 侧边栏配置 API Key
with st.sidebar:
    st.header("设置")
    api_key = st.text_input("输入 OpenAI API Key", type="password")
    model_choice = st.selectbox("选择模型", ["gpt-4o", "gpt-3.5-turbo"])

# 主界面布局
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("第1步：输入财经新闻/研报")
    news_input = st.text_area("在此粘贴原始文本：", height=300, placeholder="例如：某公司发布了财报，利润超预期...")
    analyze_btn = st.button("开始 AI 逻辑穿透", type="primary")

with col2:
    st.subheader("第2步：AI 结构化信号")
    if analyze_btn:
        if not api_key:
            st.error("请在左侧侧边栏输入 API Key！")
        else:
            try:
                client = openai.OpenAI(api_key=api_key)
                with st.spinner('AI 正在深度思考中...'):
                    prompt = f"你是一名资深量化分析师，分析以下新闻，输出JSON格式结果：subject(受影响主体), sentiment(看多/看空/中性), logic(一句话投资逻辑), impact_score(影响力1-10)。新闻内容：{news_input}"
                    
                    response = client.chat.completions.create(
                        model=model_choice,
                        messages=[{"role": "user", "content": prompt}],
                        response_format={ "type": "json_object" }
                    )
                    result = json.loads(response.choices[0].message.content)
                    
                    st.success("分析完成！")
                    st.json(result)
                    
                    st.metric("情绪评级", result.get('sentiment'))
                    st.info(f"**投资逻辑：** {result.get('logic')}")
            except Exception as e:
                st.error(f"发生错误: {str(e)}")
