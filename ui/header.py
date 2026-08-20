import time

import streamlit as st

from config.settings import AppSettings, PersonalityConfig
from services.usage import get_tracker


def render_header(all_conversations: dict, messages: list):
    st.markdown(
        f'<div class="tech-header">'
        f'<div class="tech-logo">✨</div>'
        f'<div class="tech-title-group">'
        f'<div class="tech-title">{st.session_state.ai_name}</div>'
        f'<div class="tech-subtitle">{AppSettings.APP_SUBTITLE}</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    persona_tag = PersonalityConfig.get_tag(st.session_state.ai_personality)
    current_time = time.strftime("%H:%M")
    conv_count = len(all_conversations)
    msg_count = len(messages)
    summary = get_tracker().summary()

    st.markdown(
        f'<div class="status-bar">'
        f'<div class="status-item">'
        f'<div class="status-dot"></div>'
        f'<span class="status-label">状态</span>'
        f'<span class="status-value">在线</span>'
        f'</div>'
        f'<div class="status-divider"></div>'
        f'<div class="status-item">'
        f'<span class="status-label">模式</span>'
        f'<span class="status-value">{persona_tag}</span>'
        f'</div>'
        f'<div class="status-divider"></div>'
        f'<div class="status-item">'
        f'<span class="status-label">模型</span>'
        f'<span class="status-value">{st.session_state.deepseek_model}</span>'
        f'</div>'
        f'<div class="status-divider"></div>'
        f'<div class="status-item">'
        f'<span class="status-label">会话</span>'
        f'<span class="status-value">{conv_count}</span>'
        f'</div>'
        f'<div class="status-divider"></div>'
        f'<div class="status-item">'
        f'<span class="status-label">消息</span>'
        f'<span class="status-value">{msg_count}</span>'
        f'</div>'
        f'<div class="status-divider"></div>'
        f'<div class="status-item">'
        f'<span class="status-label">Token</span>'
        f'<span class="status-value">{summary["total_tokens"]}</span>'
        f'</div>'
        f'<div class="status-divider"></div>'
        f'<div class="status-item">'
        f'<span class="status-label">成本</span>'
        f'<span class="status-value">¥{summary["cost"]:.4f}</span>'
        f'</div>'
        f'<div class="status-divider"></div>'
        f'<div class="status-item">'
        f'<span class="status-label">时间</span>'
        f'<span class="status-value">{current_time}</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    if not messages:
        st.markdown(
            '<div class="empty-state">'
            '<div class="empty-state-icon">✨</div>'
            '<div class="empty-state-text">'
            '开始与你的 AI 伴侣对话吧<br>'
            '在下方输入框中发送消息'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
