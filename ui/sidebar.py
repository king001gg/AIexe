import streamlit as st

from config.settings import AppSettings, PersonalityConfig
from models.conversation import ConversationManager
from services.usage import get_tracker
from tools.catalog import TOOL_CATALOG


def _render_navigation():
    current_index = 0 if st.session_state.view == "chat" else 1
    view = st.radio(
        "导航",
        ["💬 对话", "📚 知识库"],
        index=current_index,
        horizontal=True,
        key="nav_view",
    )
    st.session_state.view = "chat" if view == "💬 对话" else "knowledge"


def _render_conversations(conv_manager: ConversationManager, all_conversations: dict):
    st.markdown(
        '<div class="sidebar-header">'
        '<span class="sidebar-header-icon">💬</span>'
        '会话管理'
        '</div>',
        unsafe_allow_html=True
    )

    if st.button("➕ 新建对话", use_container_width=True):
        new_id = conv_manager.create(
            user_name=st.session_state.user_name,
            ai_name=st.session_state.ai_name,
            ai_personality=st.session_state.ai_personality,
        )
        st.session_state.current_conv_id = new_id
        st.rerun()

    sorted_convs = conv_manager.get_sorted(all_conversations)

    conv_list_html = '<div class="conv-list-container">'
    for conv in sorted_convs:
        is_active = conv["id"] == st.session_state.current_conv_id
        active_class = "conv-item-active" if is_active else ""
        msg_count = len(conv.get("messages", []))
        updated = conv.get("updated_at", "")
        title = conv.get("title", "新对话")
        conv_list_html += (
            f'<div class="conv-item {active_class}">'
            f'<div class="conv-item-info">'
            f'<div class="conv-item-title">{title}</div>'
            f'<div class="conv-item-meta">{updated} · {msg_count}条消息</div>'
            f'</div>'
            f'</div>'
        )
    conv_list_html += '</div>'
    st.markdown(conv_list_html, unsafe_allow_html=True)

    conv_options = {conv["id"]: conv.get("title", "新对话") for conv in sorted_convs}
    if conv_options:
        current_idx = (
            list(conv_options.keys()).index(st.session_state.current_conv_id)
            if st.session_state.current_conv_id in conv_options else 0
        )
        selected_conv = st.selectbox(
            "切换会话",
            options=list(conv_options.keys()),
            format_func=lambda x: conv_options[x],
            index=current_idx,
            key="conv_switcher"
        )
        if selected_conv != st.session_state.current_conv_id:
            st.session_state.current_conv_id = selected_conv
            st.rerun()

    col_rename, col_delete = st.columns(2)
    with col_rename:
        if st.button("✏️ 重命名", use_container_width=True):
            st.session_state.rename_conv_id = st.session_state.current_conv_id
    with col_delete:
        if st.button("🗑️ 删除", use_container_width=True):
            if st.session_state.current_conv_id:
                conv_manager.delete(st.session_state.current_conv_id)
                remaining = conv_manager.load_all()
                if remaining:
                    st.session_state.current_conv_id = conv_manager.get_latest_id(remaining)
                else:
                    new_id = conv_manager.create(
                        user_name=st.session_state.user_name,
                        ai_name=st.session_state.ai_name,
                        ai_personality=st.session_state.ai_personality,
                    )
                    st.session_state.current_conv_id = new_id
                st.rerun()

    if st.session_state.rename_conv_id:
        new_title = st.text_input(
            "新名称",
            value=all_conversations.get(st.session_state.rename_conv_id, {}).get("title", "新对话"),
            key="rename_input"
        )
        col_c, col_s = st.columns(2)
        with col_c:
            if st.button("取消", key="cancel_rename"):
                st.session_state.rename_conv_id = None
                st.rerun()
        with col_s:
            if st.button("确认", key="confirm_rename"):
                if st.session_state.rename_conv_id in all_conversations:
                    all_conversations[st.session_state.rename_conv_id]["title"] = new_title
                    conv_manager.save(all_conversations[st.session_state.rename_conv_id])
                st.session_state.rename_conv_id = None
                st.rerun()


def _render_settings(current_conv: dict):
    st.markdown(
        '<div class="sidebar-header">'
        '<span class="sidebar-header-icon">⚙</span>'
        '设置'
        '</div>',
        unsafe_allow_html=True
    )

    with st.expander("🔑 DeepSeek API", expanded=True):
        st.session_state.deepseek_api_key = st.text_input(
            "API Key",
            value=st.session_state.deepseek_api_key,
            type="password",
            help="在 platform.deepseek.com 获取；也可在 .env 中配置 DEEPSEEK_API_KEY"
        )
        models = AppSettings.DEEPSEEK_MODELS
        current_model = st.session_state.deepseek_model
        model_index = models.index(current_model) if current_model in models else 0
        st.session_state.deepseek_model = st.selectbox(
            "模型",
            models,
            index=model_index,
            help="deepseek-chat 通用对话 | deepseek-reasoner 深度推理"
        )
        if st.session_state.deepseek_api_key:
            st.success("✅ 已连接")
        else:
            st.warning("⚠️ 请配置 API Key")

    st.markdown('<hr class="gradient-divider">', unsafe_allow_html=True)

    st.session_state.user_name = st.text_input("昵称", value=st.session_state.user_name)
    st.session_state.ai_name = st.text_input("AI 名称", value=st.session_state.ai_name)
    st.session_state.ai_personality = st.selectbox(
        "性格模式",
        PersonalityConfig.OPTIONS,
        index=PersonalityConfig.OPTIONS.index(st.session_state.ai_personality)
    )

    if current_conv:
        current_conv["user_name"] = st.session_state.user_name
        current_conv["ai_name"] = st.session_state.ai_name
        current_conv["ai_personality"] = st.session_state.ai_personality


def _render_tools():
    st.markdown(
        '<div class="sidebar-header">'
        '<span class="sidebar-header-icon">🧰</span>'
        'Agent 工具'
        '</div>',
        unsafe_allow_html=True
    )
    for name, label, desc in TOOL_CATALOG:
        st.checkbox(
            label,
            value=True,
            key=f"tool_{name}",
            help=desc,
        )


def _render_usage():
    st.markdown('<hr class="gradient-divider">', unsafe_allow_html=True)
    summary = get_tracker().summary()
    st.markdown(
        f'<div class="status-bar" style="margin-bottom:8px;">'
        f'<div class="status-item"><span class="status-label">Token</span> '
        f'<span class="status-value">{summary["total_tokens"]}</span></div>'
        f'<div class="status-divider"></div>'
        f'<div class="status-item"><span class="status-label">调用</span> '
        f'<span class="status-value">{summary["calls"]}</span></div>'
        f'<div class="status-divider"></div>'
        f'<div class="status-item"><span class="status-label">成本</span> '
        f'<span class="status-value">¥{summary["cost"]:.4f}</span></div>'
        f'</div>',
        unsafe_allow_html=True
    )


def render_sidebar(conv_manager: ConversationManager, all_conversations: dict, current_conv: dict):
    with st.sidebar:
        _render_navigation()
        st.markdown('<hr class="gradient-divider">', unsafe_allow_html=True)

        _render_conversations(conv_manager, all_conversations)
        st.markdown('<hr class="gradient-divider">', unsafe_allow_html=True)

        _render_settings(current_conv)
        st.markdown('<hr class="gradient-divider">', unsafe_allow_html=True)

        _render_tools()
        _render_usage()

        st.markdown('<hr class="gradient-divider">', unsafe_allow_html=True)

        if st.button("🗑  清空当前对话", use_container_width=True):
            if st.session_state.current_conv_id and st.session_state.current_conv_id in all_conversations:
                all_conversations[st.session_state.current_conv_id]["messages"] = []
                conv_manager.save(all_conversations[st.session_state.current_conv_id])
            st.rerun()

        st.markdown(
            f'<div class="tech-footer">'
            f'<span class="version">{AppSettings.APP_NAME}</span> v{AppSettings.APP_VERSION}<br>'
            f'Powered by DeepSeek'
            f'</div>',
            unsafe_allow_html=True
        )
