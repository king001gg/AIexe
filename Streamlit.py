import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="AI 智能伴侣",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_name" not in st.session_state:
    st.session_state.user_name = "用户"
if "ai_name" not in st.session_state:
    st.session_state.ai_name = "小智"
if "ai_personality" not in st.session_state:
    st.session_state.ai_personality = "温柔体贴"
if "theme" not in st.session_state:
    st.session_state.theme = "明亮"
if "deepseek_api_key" not in st.session_state:
    st.session_state.deepseek_api_key = ""
if "deepseek_model" not in st.session_state:
    st.session_state.deepseek_model = "deepseek-chat"

PERSONALITY_PROMPTS = {
    "温柔体贴": "你是一个温柔体贴的AI伴侣，总是关心用户的感受，用温暖的语气回应，善于倾听和安慰。",
    "幽默风趣": "你是一个幽默风趣的AI伴侣，喜欢用轻松搞笑的方式交流，总能逗用户开心，但也会在需要时给出认真建议。",
    "理性冷静": "你是一个理性冷静的AI伴侣，善于分析问题，给出客观理性的建议，逻辑清晰，不感情用事。",
    "活泼可爱": "你是一个活泼可爱的AI伴侣，充满活力，喜欢用可爱的表情和语气交流，让对话充满乐趣。",
    "知性优雅": "你是一个知性优雅的AI伴侣，谈吐优雅，知识渊博，善于用优美的语言表达观点。"
}

with st.sidebar:
    st.title("⚙️ 设置")

    with st.expander("🔑 DeepSeek API", expanded=True):
        st.session_state.deepseek_api_key = st.text_input(
            "API Key",
            value=st.session_state.deepseek_api_key,
            type="password",
            help="在 platform.deepseek.com 获取你的 API Key"
        )
        st.session_state.deepseek_model = st.selectbox(
            "模型",
            ["deepseek-chat", "deepseek-reasoner"],
            index=["deepseek-chat", "deepseek-reasoner"].index(st.session_state.deepseek_model),
            help="deepseek-chat 为通用对话模型，deepseek-reasoner 为深度推理模型"
        )
        if st.session_state.deepseek_api_key:
            st.success("✅ API Key 已配置")
        else:
            st.warning("⚠️ 请先配置 API Key")

    st.session_state.user_name = st.text_input("你的昵称", value=st.session_state.user_name)
    st.session_state.ai_name = st.text_input("AI 名字", value=st.session_state.ai_name)
    st.session_state.ai_personality = st.selectbox(
        "AI 性格",
        ["温柔体贴", "幽默风趣", "理性冷静", "活泼可爱", "知性优雅"],
        index=["温柔体贴", "幽默风趣", "理性冷静", "活泼可爱", "知性优雅"].index(st.session_state.ai_personality)
    )
    st.session_state.theme = st.radio("主题风格", ["明亮", "暗黑"], index=["明亮", "暗黑"].index(st.session_state.theme))

    st.divider()
    if st.button("🗑️ 清空对话", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption("💡 AI 智能伴侣 v1.0 · Powered by DeepSeek")

st.title(f"🤖 {st.session_state.ai_name} — 你的 AI 智能伴侣")
st.caption(f"当前性格：{st.session_state.ai_personality} | 模型：{st.session_state.deepseek_model}")

for message in st.session_state.messages:
    role = message["role"]
    avatar = "🧑" if role == "user" else "🤖"
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input(f"和 {st.session_state.ai_name} 说点什么吧..."):
    personality_desc = PERSONALITY_PROMPTS.get(st.session_state.ai_personality, PERSONALITY_PROMPTS["温柔体贴"])
    system_prompt = (
        f"你是{st.session_state.ai_name}，一个{st.session_state.ai_personality}的AI智能伴侣。"
        f"{personality_desc}"
        f"用户的名字叫{st.session_state.user_name}。请用自然、亲切的方式与用户对话。"
    )

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        if not st.session_state.deepseek_api_key:
            st.error("⚠️ 请先在侧边栏配置 DeepSeek API Key！")
            st.session_state.messages.pop()
        else:
            try:
                client = OpenAI(
                    api_key=st.session_state.deepseek_api_key,
                    base_url="https://api.deepseek.com"
                )
                api_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages
                stream = client.chat.completions.create(
                    model=st.session_state.deepseek_model,
                    messages=api_messages,
                    stream=True
                )
                response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"❌ 调用 DeepSeek API 失败：{e}")
                st.session_state.messages.pop()