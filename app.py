import streamlit as st

st.set_page_config(
    page_title="OSHC Student Assistant",
    page_icon="💬",
    layout="centered"
)

st.title("💬 OSHC Student Assistant")
st.caption("Multilingual support for international students")

language = st.selectbox(
    "Choose your preferred language",
    ["English", "简体中文", "Bahasa Melayu"]
)

# -------------------------
# Pre-written responses
# -------------------------

responses = {
    "English": {
        "dental":
            "Dental treatment is generally not included in standard OSHC. "
            "You may need additional Extras cover. Please check your specific policy.",

        "claim":
            "You can usually submit an OSHC claim through your insurer's app "
            "or online account. Keep your receipt and invoice from the healthcare provider.",

        "gp":
            "A GP (General Practitioner) is usually the first healthcare professional "
            "to see if you are sick or need medical advice.",

        "hospital":
            "OSHC may cover eligible hospital treatment depending on your policy. "
            "Please check your cover before non-emergency treatment.",

        "emergency":
            "If you are experiencing a medical emergency in Australia, call 000 immediately.",

        "interpreter":
            "Interpreter and multilingual support may be available to help international "
            "students understand healthcare and insurance services.",

        "default":
            "I'm not completely sure about that. Please check your official OSHC policy "
            "or contact your insurer for confirmation."
    },

    "简体中文": {
        "dental":
            "普通 OSHC 通常不包含牙科治疗。你可能需要额外购买 Extras 保险。"
            "建议查看你自己的保险条款确认。",

        "claim":
            "通常可以通过保险公司的 App 或网上账户提交 OSHC 报销。"
            "记得保留诊所提供的收据和发票。",

        "gp":
            "GP 是 General Practitioner，也就是全科医生。"
            "在澳洲身体不舒服时，通常可以先预约 GP。",

        "hospital":
            "OSHC 可能承担符合条件的医院治疗费用，"
            "具体保障范围取决于你的保险计划。",

        "emergency":
            "如果在澳洲遇到医疗紧急情况，请立即拨打 000。",

        "interpreter":
            "部分 OSHC 服务提供翻译及多语言支持，"
            "帮助国际学生理解澳洲医疗和保险服务。",

        "default":
            "我目前不能确定这个问题。建议查看你的正式 OSHC 保单，"
            "或直接联系保险公司确认。"
    },

    "Bahasa Melayu": {
        "dental":
            "Rawatan pergigian biasanya tidak termasuk dalam OSHC standard. "
            "Anda mungkin memerlukan perlindungan Extras tambahan.",

        "claim":
            "Anda biasanya boleh membuat tuntutan melalui aplikasi atau akaun "
            "dalam talian syarikat insurans anda. Simpan resit dan invois.",

        "gp":
            "GP bermaksud General Practitioner. Biasanya anda boleh berjumpa GP "
            "terlebih dahulu apabila anda sakit.",

        "hospital":
            "OSHC mungkin melindungi rawatan hospital yang layak, bergantung kepada polisi anda.",

        "emergency":
            "Jika anda mengalami kecemasan perubatan di Australia, hubungi 000 dengan segera.",

        "interpreter":
            "Sokongan jurubahasa dan pelbagai bahasa mungkin tersedia untuk membantu "
            "pelajar antarabangsa memahami sistem kesihatan.",

        "default":
            "Saya tidak pasti tentang perkara itu. Sila semak polisi OSHC rasmi anda "
            "atau hubungi syarikat insurans anda."
    }
}

# -------------------------
# Chat history
# -------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

question = st.chat_input("Ask me about your OSHC...")

if question:

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.write(question)

    q = question.lower()

    if any(word in q for word in ["dental", "dentist", "牙", "gigi"]):
        answer = responses[language]["dental"]

    elif any(word in q for word in ["claim", "refund", "报销", "tuntutan"]):
        answer = responses[language]["claim"]

    elif any(word in q for word in ["gp", "doctor", "医生", "doktor"]):
        answer = responses[language]["gp"]

    elif any(word in q for word in ["hospital", "医院", "hospital"]):
        answer = responses[language]["hospital"]

    elif any(word in q for word in ["emergency", "000", "紧急", "kecemasan"]):
        answer = responses[language]["emergency"]

    elif any(word in q for word in ["interpreter", "language", "翻译", "语言", "bahasa"]):
        answer = responses[language]["interpreter"]

    else:
        answer = responses[language]["default"]

    with st.chat_message("assistant"):
        st.write(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })