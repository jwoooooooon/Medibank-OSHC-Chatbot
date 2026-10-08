            "我找到以下最相关的 Medibank 官方内容，但这个免费版本不会在资料不足时自行翻译或推测：\n\n"
            + " ".join(selected)
        )

    return (
        "Saya menemui kandungan rasmi Medibank yang paling berkaitan di bawah. "
        "Versi percuma ini tidak akan menterjemah atau membuat andaian jika maklumat tidak mencukupi:\n\n"
        + " ".join(selected)
    )


def create_answer(question, results, language):
    if not results:
        return {
            "English": "I couldn't retrieve enough information from the selected Medibank pages.",
            "简体中文": "我暂时无法从所选的 Medibank 页面获取足够的信息。",
            "Bahasa Melayu": "Saya tidak dapat mendapatkan maklumat yang mencukupi daripada halaman Medibank yang dipilih."
        }[language]

    topic = detect_topic(question, results, language)

    if evidence_supports(topic, results):
        return TEMPLATES[topic][language]

    return fallback_extract_answer(question, results, language)

# --------------------------------------------------
# CHAT HISTORY
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

        if "sources" in message and message["sources"]:
            st.markdown("**Sources:**")
            for source in message["sources"]:
                st.markdown(
                    f"- [{source['source']}]({source['url']})"
                )

# --------------------------------------------------
# USER INPUT
# --------------------------------------------------

typed_question = st.chat_input(
    "Ask about Medibank OSHC..."
)

question = typed_question

if "suggested_question" in st.session_state:
    question = st.session_state.suggested_question
    del st.session_state.suggested_question

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.write(question)

    with st.spinner("Searching Medibank official information..."):
        results = search_medibank(question, language)
        answer = create_answer(question, results, language)

    sources = []
    used_urls = set()

    for item in results[:3]:
        if item["url"] not in used_urls:
            used_urls.add(item["url"])
            sources.append({
                "source": item["source"],
                "url": item["url"]
            })

    with st.chat_message("assistant"):
        st.write(answer)

        if sources:
            st.markdown("**Sources:**")
            for source in sources:
                st.markdown(
                    f"- [{source['source']}]({source['url']})"
                )

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })

# --------------------------------------------------
# DISCLAIMER
# --------------------------------------------------

st.divider()

st.caption(
    "Student prototype only. Information is retrieved from selected publicly available "
    "Medibank OSHC webpages and should be confirmed against current official policy documents."
)
