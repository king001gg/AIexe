import streamlit as st

from config.settings import AppSettings, PersonalityConfig
from models.conversation import ConversationManager
from services.agent import Agent
from services.deepseek import DeepSeekService
from services.usage import get_tracker


def render_chat(conv_manager: ConversationManager, current_conv: dict, messages: list, tool_instances: dict):
    for message in messages:
        role = message["role"]
        avatar = AppSettings.USER_AVATAR if role == "user" else AppSettings.AI_AVATAR
        with st.chat_message(role, avatar=avatar):
            st.markdown(message["content"])

    if prompt := st.chat_input(f"和 {st.session_state.ai_name} 对话..."):
        system_prompt = PersonalityConfig.build_system_prompt(
            ai_name=st.session_state.ai_name,
            personality=st.session_state.ai_personality,
            user_name=st.session_state.user_name,
        )

        messages.append({"role": "user", "content": prompt})

        if current_conv:
            conv_manager.auto_title(current_conv)
            conv_manager.touch(current_conv)
            conv_manager.save(current_conv)

        with st.chat_message("user", avatar=AppSettings.USER_AVATAR):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=AppSettings.AI_AVATAR):
            if not st.session_state.deepseek_api_key:
                st.error("⚠️ 请先在侧边栏配置 DeepSeek API Key（或在 .env 中设置 DEEPSEEK_API_KEY）")
                messages.pop()
                if current_conv:
                    conv_manager.save(current_conv)
                return

            try:
                service = DeepSeekService(
                    api_key=st.session_state.deepseek_api_key,
                    model=st.session_state.deepseek_model,
                )

                # 仅保留系统提示 + 历史对话 + 当前输入
                api_messages = [{"role": "system", "content": system_prompt}] + [
                    {"role": m["role"], "content": m["content"]} for m in messages
                ]

                enabled = [
                    tool
                    for name, tool in tool_instances.items()
                    if st.session_state.get(f"tool_{name}", True)
                ]
                agent = Agent(service, tools=enabled)

                with st.spinner("思考中..."):
                    result = agent.run(api_messages)

                if result.tool_steps:
                    with st.status("🔧 工具调用过程", expanded=False) as status:
                        for step in result.tool_steps:
                            status.write(f"**`{step.name}`** 参数：{step.arguments}")
                            status.write(f"结果：{step.output[:300]}")
                        status.update(label="✅ 工具执行完成", state="complete")

                answer = result.answer or "（未生成回答）"
                st.markdown(answer)
                messages.append({"role": "assistant", "content": answer})
                if current_conv:
                    conv_manager.touch(current_conv)
                    conv_manager.save(current_conv)

                get_tracker().record(
                    model=st.session_state.deepseek_model,
                    prompt_tokens=result.usage.get("prompt_tokens", 0),
                    completion_tokens=result.usage.get("completion_tokens", 0),
                )
            except Exception as exc:
                st.error(f"❌ API 调用失败：{exc}")
                if current_conv:
                    conv_manager.save(current_conv)
