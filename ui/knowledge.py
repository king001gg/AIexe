import streamlit as st

from services.rag.knowledge_base import get_knowledge_base


def render_knowledge():
    kb = get_knowledge_base()

    st.markdown(
        '<div class="tech-header">'
        '<div class="tech-logo">📚</div>'
        '<div class="tech-title-group">'
        '<div class="tech-title">知识库</div>'
        '<div class="tech-subtitle">上传私有文档，让 AI 基于你的知识回答问题</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("### 上传文档")
    uploaded = st.file_uploader("支持 .txt / .md", type=["txt", "md"])
    if uploaded is not None:
        title = uploaded.name.rsplit(".", 1)[0]
        content = uploaded.read().decode("utf-8", errors="ignore")
        if st.button("📥 导入到知识库", type="primary"):
            if not content.strip():
                st.warning("文档内容为空，未导入。")
            else:
                doc_id = kb.add_document(title, content)
                if doc_id:
                    st.success(f"已导入《{title}》")
                else:
                    st.warning("导入失败。")

    st.markdown("### 已导入文档")
    docs = kb.list_documents()
    if not docs:
        st.info("还没有文档，上传一个试试吧。")
        return

    for doc in docs:
        col_info, col_action = st.columns([4, 1])
        with col_info:
            st.markdown(
                f"**{doc['title']}**  ·  {doc['chunk_count']} 块 ·  {doc['created_at']}"
            )
        with col_action:
            if st.button("🗑️ 删除", key=f"del_{doc['id']}"):
                kb.delete(doc["id"])
                st.rerun()
