import streamlit as st
from difflib import SequenceMatcher

# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------

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

# --------------------------------------------------
# KNOWLEDGE BASE
# --------------------------------------------------

faq_data = [

    # 1. Comprehensive vs Essential
    {
        "topic": "Comprehensive vs Essential",
        "keywords": [
            "comprehensive", "essential", "difference", "compare",
            "区别", "差别", "有什么不同",
            "perbezaan", "banding"
        ],

        "English":
            "Medibank offers different OSHC cover options such as Essential and "
            "Comprehensive OSHC. Comprehensive OSHC generally provides additional "
            "support and benefits compared with a more basic level of cover. "
            "Students should check the current official Cover Summary before choosing.",

        "简体中文":
            "Medibank 提供不同等级的 OSHC，例如 Essential 和 Comprehensive。"
            "Comprehensive OSHC 通常会比基础等级提供更多保障或额外服务。"
            "具体保障内容可能更新，因此选择前应查看最新的官方 Cover Summary。",

        "Bahasa Melayu":
            "Medibank menawarkan beberapa tahap OSHC seperti Essential dan Comprehensive. "
            "Comprehensive biasanya menyediakan manfaat atau sokongan tambahan berbanding "
            "pelan yang lebih asas. Sila semak Cover Summary terkini untuk maklumat tepat."
    },


    # 2. Dental
    {
        "topic": "Dental",
        "keywords": [
            "dental", "dentist", "teeth",
            "牙医", "牙齿", "牙科",
            "gigi", "doktor gigi"
        ],

        "English":
            "Dental treatment is generally not included under standard OSHC. "
            "Additional Extras cover may be required. Check your individual policy "
            "before receiving treatment.",

        "简体中文":
            "一般的 OSHC 通常不包括牙科治疗。你可能需要额外的 Extras 保险。"
            "接受治疗前建议先查看自己的保单。",

        "Bahasa Melayu":
            "Rawatan pergigian biasanya tidak termasuk dalam OSHC standard. "
            "Anda mungkin memerlukan perlindungan Extras tambahan."
    },


    # 3. GP
    {
        "topic": "GP",
        "keywords": [
            "gp", "doctor", "general practitioner", "sick",
            "医生", "看医生", "生病", "全科医生",
            "doktor", "sakit"
        ],

        "English":
            "A GP, or General Practitioner, is usually the first healthcare professional "
            "you see when you are sick or need general medical advice. "
            "Some GP clinics may offer direct billing arrangements for OSHC members.",

        "简体中文":
            "GP 是 General Practitioner，也就是全科医生。"
            "在澳洲身体不舒服或需要一般医疗建议时，通常可以先预约 GP。"
            "部分诊所可能提供 OSHC direct billing。",

        "Bahasa Melayu":
            "GP bermaksud General Practitioner. Biasanya anda boleh berjumpa GP "
            "terlebih dahulu apabila anda sakit atau memerlukan nasihat perubatan."
    },


    # 4. Claims
    {
        "topic": "Claims",
        "keywords": [
            "claim", "claims", "refund", "reimburse", "receipt",
            "报销", "索赔", "claim钱", "退款",
            "tuntutan", "bayaran balik"
        ],

        "English":
            "OSHC claims can usually be submitted through your insurer's digital services "
            "or member account. Keep your receipt and invoice from the healthcare provider. "
            "The amount you receive depends on your policy and the service provided.",

        "简体中文":
            "OSHC 报销通常可以通过保险公司的线上服务或会员账户提交。"
            "记得保留医生或医疗机构提供的收据和发票。"
            "实际可报销金额取决于你的保单和医疗服务类型。",

        "Bahasa Melayu":
            "Tuntutan OSHC biasanya boleh dihantar melalui perkhidmatan digital atau akaun ahli. "
            "Simpan resit dan invois daripada penyedia kesihatan."
    },


    # 5. Hospital
    {
        "topic": "Hospital",
        "keywords": [
            "hospital", "hospital treatment", "admission",
            "医院", "住院", "入院",
            "hospital", "masuk hospital"
        ],

        "English":
            "Eligible hospital treatment may be covered under OSHC, depending on the "
            "type of treatment and your specific policy. For planned treatment, "
            "check your cover before admission.",

        "简体中文":
            "符合条件的医院治疗可能由 OSHC 承担，但具体取决于治疗类型和你的保单。"
            "如果是非紧急的计划治疗，建议入院前先确认保障范围。",

        "Bahasa Melayu":
            "Rawatan hospital yang layak mungkin dilindungi oleh OSHC, bergantung pada "
            "jenis rawatan dan polisi anda."
    },


    # 6. Ambulance
    {
        "topic": "Ambulance",
        "keywords": [
            "ambulance", "救护车", "救護車",
            "ambulans"
        ],

        "English":
            "OSHC may provide benefits for eligible ambulance services. "
            "Coverage conditions can vary, so check your policy for the exact rules.",

        "简体中文":
            "OSHC 可能会保障符合条件的救护车服务。"
            "具体条件可能因保单而异，因此建议查看你的保险条款。",

        "Bahasa Melayu":
            "OSHC mungkin menyediakan manfaat untuk perkhidmatan ambulans yang layak. "
            "Sila semak polisi anda untuk syarat khusus."
    },


    # 7. Prescription medicines
    {
        "topic": "Medicines",
        "keywords": [
            "medicine", "medication", "pharmacy", "prescription", "drug",
            "药", "药房", "处方药", "买药",
            "ubat", "farmasi"
        ],

        "English":
            "OSHC may provide benefits toward eligible prescription medicines. "
            "Limits and out-of-pocket costs may apply depending on your cover.",

        "简体中文":
            "OSHC 可能会为符合条件的处方药提供部分保障。"
            "具体上限和自付金额取决于你的保险计划。",

        "Bahasa Melayu":
            "OSHC mungkin memberikan manfaat untuk ubat preskripsi yang layak. "
            "Had dan kos sendiri mungkin dikenakan."
    },


    # 8. Interpreter / language
    {
        "topic": "Language Support",
        "keywords": [
            "interpreter", "translation", "language", "multilingual",
            "翻译", "语言", "中文", "华语",
            "bahasa", "terjemahan"
        ],

        "English":
            "Multilingual and interpreter support can help international students "
            "understand healthcare services, insurance information and claims. "
            "Check Medibank's current support channels for available language services.",

        "简体中文":
            "多语言及翻译服务可以帮助国际学生理解澳洲医疗、保险和报销流程。"
            "你可以查看 Medibank 当前提供的语言支持渠道。",

        "Bahasa Melayu":
            "Sokongan pelbagai bahasa dan jurubahasa boleh membantu pelajar antarabangsa "
            "memahami perkhidmatan kesihatan, insurans dan tuntutan."
    },


    # 9. Emergency
    {
        "topic": "Emergency",
        "keywords": [
            "emergency", "urgent", "000", "accident",
            "紧急", "急诊", "意外",
            "kecemasan"
        ],

        "English":
            "If you are experiencing a medical emergency in Australia, call 000 immediately.",

        "简体中文":
            "如果你在澳洲遇到医疗紧急情况，请立即拨打 000。",

        "Bahasa Melayu":
            "Jika anda mengalami kecemasan perubatan di Australia, hubungi 000 dengan segera."
    },


    # 10. Waiting period
    {
        "topic": "Waiting Period",
        "keywords": [
            "waiting period", "wait", "waiting",
            "等待期", "多久才能", "等多久",
            "tempoh menunggu"
        ],

        "English":
            "Some treatments or services may have waiting periods. "
            "The applicable waiting period depends on the service and policy. "
            "Check the official policy documents before arranging treatment.",

        "简体中文":
            "部分治疗或服务可能设有等待期。"
            "具体等待时间取决于医疗服务和保险条款，接受治疗前应查看正式保单。",

        "Bahasa Melayu":
            "Sesetengah rawatan mungkin mempunyai tempoh menunggu. "
            "Tempoh tersebut bergantung kepada jenis rawatan dan polisi anda."
    }
]


# --------------------------------------------------
# FIND BEST ANSWER
# --------------------------------------------------

def find_answer(question, language):

    question = question.lower()

    best_faq = None
    best_score = 0

    for faq in faq_data:

        score = 0

        for keyword in faq["keywords"]:

            keyword = keyword.lower()

            # Direct keyword match
            if keyword in question:
                score += 3

            # Fuzzy similarity
            similarity = SequenceMatcher(
                None,
                keyword,
                question
            ).ratio()

            if similarity > 0.6:
                score += similarity

        if score > best_score:
            best_score = score
            best_faq = faq


    # If good match found
    if best_faq and best_score >= 2:
        return best_faq[language], best_faq["topic"]


    # Default response
    default_answers = {

        "English":
            "I'm not completely sure about that yet. "
            "Please check your official Medibank OSHC policy or contact Medibank "
            "for confirmation.",

        "简体中文":
            "这个问题目前不在我的资料库中。"
            "建议查看你的 Medibank OSHC 正式保单，或直接联系 Medibank 确认。",

        "Bahasa Melayu":
            "Soalan ini belum terdapat dalam pangkalan maklumat saya. "
            "Sila semak polisi Medibank OSHC rasmi anda atau hubungi Medibank."
    }

    return default_answers[language], "Unknown"


# --------------------------------------------------
# CHAT HISTORY
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])


# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

question = st.chat_input(
    "Ask me about your OSHC..."
)


if question:

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.write(question)


    answer, topic = find_answer(
        question,
        language
    )


    with st.chat_message("assistant"):
        st.write(answer)


    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })


# --------------------------------------------------
# DISCLAIMER
# --------------------------------------------------

st.divider()

st.caption(
    "Prototype only — information provided by this assistant should be "
    "confirmed against current official Medibank OSHC policy documents."
)
