import streamlit as st

from config.logging_config import setup_logging
from config.settings import AppSettings
from models.conversation import ConversationManager
from models.memory import get_memory_store
from services.rag.knowledge_base import get_knowledge_base
from tools.builtin import (
    CALCULATOR_TOOL,
    DATETIME_TOOL,
    make_knowledge_search_tool,
    make_memory_tools,
)
from ui.chat import render_chat
from ui.header import render_header
from ui.knowledge import render_knowledge
from ui.sidebar import render_sidebar
from ui.styles import render_styles


def init_session_state():
    defaults = {
        "current_conv_id": None,
        "user_name": AppSettings.DEFAULT_USER_NAME,
        "ai_name": AppSettings.DEFAULT_AI_NAME,
        "ai_personality": AppSettings.DEFAULT_PERSONALITY,
        "deepseek_api_key": AppSettings.DEEPSEEK_API_KEY,
        "deepseek_model": AppSettings.DEFAULT_MODEL,
        "rename_conv_id": None,
        "view": "chat",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def build_tool_instances() -> dict:
    """构建全部内置工具实例（绑定单例知识库与记忆库）。"""
    kb = get_knowledge_base()
    memory = get_memory_store()
    mem_save, mem_search = make_memory_tools(memory)
    return {
        "calculator": CALCULATOR_TOOL,
        "get_datetime": DATETIME_TOOL,
        "knowledge_search": make_knowledge_search_tool(kb),
        "memory_save": mem_save,
        "memory_search": mem_search,
    }


def main():
    setup_logging()
    st.set_page_config(
        page_title=AppSettings.PAGE_TITLE,
        page_icon=AppSettings.PAGE_ICON,
        layout=AppSettings.LAYOUT,
        initial_sidebar_state=AppSettings.INITIAL_SIDEBAR_STATE,
    )

    AppSettings.ensure_dirs()
    init_session_state()
    render_styles()

    conv_manager = ConversationManager()
    all_conversations = conv_manager.load_all()

    if not st.session_state.current_conv_id or st.session_state.current_conv_id not in all_conversations:
        if all_conversations:
            st.session_state.current_conv_id = conv_manager.get_latest_id(all_conversations)
        else:
            new_id = conv_manager.create(
                user_name=st.session_state.user_name,
                ai_name=st.session_state.ai_name,
                ai_personality=st.session_state.ai_personality,
            )
            st.session_state.current_conv_id = new_id
            all_conversations = conv_manager.load_all()

    current_conv = all_conversations.get(st.session_state.current_conv_id)
    messages = current_conv["messages"] if current_conv else []

    render_sidebar(conv_manager, all_conversations, current_conv)

    if st.session_state.view == "knowledge":
        render_knowledge()
    else:
        render_header(all_conversations, messages)
        render_chat(conv_manager, current_conv, messages, build_tool_instances())


if __name__ == "__main__":
    main()
