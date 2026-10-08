import streamlit as st
import streamlit.components.v1 as components
import requests
from bs4 import BeautifulSoup
import re
import html
from difflib import SequenceMatcher

# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------

st.set_page_config(
    page_title="Medibank OSHC Assistant",
    page_icon="💬",
    layout="centered"
)

# --------------------------------------------------
# BRAND-INSPIRED APPEARANCE
# --------------------------------------------------

st.markdown("""
<style>
    .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        background: linear-gradient(135deg, #d71920 0%, #ef3340 58%, #ff6b6b 100%);
        padding: 28px 30px;
        border-radius: 22px;
        margin-bottom: 22px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }

    .hero-kicker {
        color: rgba(255,255,255,0.82);
        font-size: 0.86rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .hero-title {
        color: white;
        font-size: 2.15rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        color: rgba(255,255,255,0.92);
        font-size: 1rem;
        margin: 0;
    }

    .trust-row {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin: 4px 0 22px 0;
    }

    .trust-pill {
        border: 1px solid rgba(128,128,128,0.28);
        border-radius: 999px;
        padding: 7px 12px;
        font-size: 0.84rem;
        opacity: 0.9;
    }

    div.stButton > button {
        border-radius: 12px;
        min-height: 46px;
        font-weight: 650;
        border: 1px solid rgba(128,128,128,0.30);
        transition: 0.15s ease;
    }

    div.stButton > button:hover {
        border-color: #ef3340;
        transform: translateY(-1px);
    }

    [data-testid="stChatMessage"] {
        border-radius: 16px;
    }

    .section-label {
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0.05em;
        opacity: 0.72;
        text-transform: uppercase;
        margin: 12px 0 8px 0;
    }

    .source-note {
        font-size: 0.82rem;
        opacity: 0.72;
        margin-top: 6px;
    }

    .prototype-note {
        border-left: 4px solid #ef3340;
        padding: 10px 14px;
        border-radius: 8px;
        background: rgba(239,51,64,0.08);
        margin-top: 18px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="hero-kicker">Student concept prototype</div>
    <div class="hero-title">Medibank OSHC Assistant</div>
    <p class="hero-subtitle">
        Quick, multilingual guidance using selected official Medibank OSHC information.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="trust-row">
    <span class="trust-pill">✓ Official-source retrieval</span>
    <span class="trust-pill">✓ No API cost</span>
    <span class="trust-pill">✓ Multilingual support</span>
    <span class="trust-pill">✓ Source links included</span>
</div>
""", unsafe_allow_html=True)

language = st.selectbox(
    "Choose your preferred language",
    ["English", "简体中文", "Bahasa Melayu"]
)

reset_col, info_col = st.columns([1, 3])
with reset_col:
    if st.button("↻ New chat"):
        st.session_state.messages = []
        st.rerun()

with info_col:
    st.caption("Tip: use the quick questions below for the smoothest demo experience.")

# --------------------------------------------------
# SUGGESTED QUESTIONS
# --------------------------------------------------

st.markdown('<div class="section-label">Popular questions</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.button("Compare Comprehensive & Essentials"):
        st.session_state.suggested_question = (
            "What is the difference between Comprehensive and Essentials OSHC?"
        )

    if st.button("Does OSHC cover dental?"):
        st.session_state.suggested_question = (
            "Does OSHC cover dental treatment?"
        )

    if st.button("How do I make a claim?"):
        st.session_state.suggested_question = (
            "How do I make an OSHC claim?"
        )

with col2:
    if st.button("Can I get an interpreter?"):
        st.session_state.suggested_question = (
            "Can I get an interpreter?"
        )

    if st.button("What happens in an emergency?"):
        st.session_state.suggested_question = (
            "What should I do in a medical emergency?"
        )

    if st.button("Does OSHC cover prescription medicine?"):
        st.session_state.suggested_question = (
            "Does OSHC cover prescription medicine?"
        )

# --------------------------------------------------
# OFFICIAL MEDIBANK SOURCES
# --------------------------------------------------

SOURCES = {
    "OSHC Overview":
        "https://www.medibank.com.au/overseas-health-insurance/oshc/",

    "Comprehensive OSHC":
        "https://www.medibank.com.au/overseas-health-insurance/oshc/comprehensive-oshc/",

    "Essentials OSHC":
        "https://www.medibank.com.au/overseas-health-insurance/oshc/essentials-oshc/",

    "OSHC FAQ":
        "https://www.medibank.com.au/overseas-health-insurance/guides/for-students/faq/"
}

# --------------------------------------------------
# KNOWN FACT PATTERNS / SAFE RESPONSE TEMPLATES
# These are used only when the retrieved Medibank text supports the topic.
# --------------------------------------------------

TEMPLATES = {
    "claim": {
        "keywords": ["claim", "claims", "submit claims", "app"],
        "English": (
            "You can submit eligible OSHC claims through the Medibank OSHC App. "
            "The app also lets you view your cover details and find health service providers."
        ),
        "简体中文": (
            "你可以通过 Medibank OSHC App 提交符合条件的报销申请。"
            "这个 App 也可以查看你的保障详情，并寻找医疗服务提供者。"
        ),
        "Bahasa Melayu": (
            "Anda boleh menghantar tuntutan OSHC yang layak melalui aplikasi Medibank OSHC. "
            "Aplikasi itu juga membolehkan anda melihat butiran perlindungan dan mencari penyedia kesihatan."
        ),
    },
    "interpreter": {
        "keywords": ["interpreter", "24/7 student health and support line", "student health and support line"],
        "English": (
            "Yes. Medibank OSHC members can access interpreter support through the "
            "24/7 Student Health and Support Line."
        ),
        "简体中文": (
            "可以。Medibank OSHC 会员可以通过 24/7 Student Health and Support Line 使用翻译服务。"
        ),
        "Bahasa Melayu": (
            "Ya. Ahli Medibank OSHC boleh mendapatkan sokongan jurubahasa melalui "
            "24/7 Student Health and Support Line."
        ),
    },
    "emergency": {
        "keywords": ["emergency ambulance", "unlimited emergency ambulance", "ambulance"],
        "English": (
            "Medibank OSHC includes eligible emergency ambulance cover Australia-wide. "
            "For a medical emergency, call 000."
        ),
        "简体中文": (
            "Medibank OSHC 包括符合条件的澳洲境内紧急救护车保障。"
            "如果发生医疗紧急情况，请拨打 000。"
        ),
        "Bahasa Melayu": (
            "Medibank OSHC merangkumi perlindungan ambulans kecemasan yang layak di seluruh Australia. "
            "Jika berlaku kecemasan perubatan, hubungi 000."
        ),
    },
    "dental": {
        "keywords": ["dental", "dentist", "extras"],
        "English": (
            "Dental treatment is generally not part of standard OSHC hospital and medical cover. "
            "Check whether you need separate Extras cover."
        ),
        "简体中文": (
            "牙科治疗通常不属于标准 OSHC 的医院和医疗保障范围。"
            "你可能需要另外购买 Extras 保障，建议查看你的具体保单。"
        ),
        "Bahasa Melayu": (
            "Rawatan pergigian biasanya tidak termasuk dalam perlindungan hospital dan perubatan OSHC standard. "
            "Anda mungkin memerlukan perlindungan Extras yang berasingan."
        ),
    },
    "medicine": {
        "keywords": ["prescription", "pharmacy", "pharmaceutical", "medicine"],
        "English": (
            "OSHC may provide benefits for eligible prescription medicines, subject to your cover limits and conditions."
        ),
        "简体中文": (
            "OSHC 可能会为符合条件的处方药提供一定保障，具体取决于你的保单限额和条件。"
        ),
        "Bahasa Melayu": (
            "OSHC mungkin memberi manfaat untuk ubat preskripsi yang layak, tertakluk pada had dan syarat perlindungan anda."
        ),
    },
    "compare": {
        "keywords": ["comprehensive", "essentials"],
        "English": (
            "Comprehensive OSHC and Essentials OSHC are different Medibank cover options. "
            "Comprehensive generally provides broader support or additional benefits, while Essentials is the more basic option. "
            "The exact inclusions should be checked against the current official cover summaries."
        ),
        "简体中文": (
            "Comprehensive OSHC 和 Essentials OSHC 是 Medibank 的不同保障等级。"
            "一般来说，Comprehensive 提供更广的支持或额外福利，而 Essentials 属于较基础的选择。"
            "具体差异仍应以最新官方 Cover Summary 为准。"
        ),
        "Bahasa Melayu": (
            "Comprehensive OSHC dan Essentials OSHC ialah dua pilihan perlindungan Medibank yang berbeza. "
            "Secara umum, Comprehensive menawarkan sokongan atau manfaat tambahan, manakala Essentials ialah pilihan yang lebih asas. "
            "Sila semak Cover Summary rasmi terkini untuk perbezaan tepat."
        ),
    },
}

# --------------------------------------------------
# TEXT CLEANING
# --------------------------------------------------

def clean_text(text):
    text = html.unescape(text)

    # Common mojibake replacements
    replacements = {
        "â€¢": "•",
        "â€“": "–",
        "â€”": "—",
        "â€™": "'",
        "â€œ": '"',
        "â€": '"',
        "â€¦": "...",
        "Â": "",
        "\xa0": " ",
        "�": "",
        "â„¢": "™",
        "â‚¬": "€",
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    # Remove remaining suspicious mojibake fragments
    text = re.sub(r"â\S?", "", text)

    # Normalize bullets into sentence separators so extraction is cleaner
    text = text.replace("•", ". ")

    # Remove control chars and collapse whitespace
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()

# --------------------------------------------------
# DOWNLOAD WEBSITE TEXT
# --------------------------------------------------

@st.cache_data(ttl=3600)
def get_page_text(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; StudentProjectPrototype/1.0)"
    }

    try:
        response = requests.get(url, headers=headers, timeout=12)
        response.raise_for_status()
        response.encoding = "utf-8"

        soup = BeautifulSoup(response.text, "html.parser")

        for element in soup([
            "script", "style", "nav", "footer", "header",
            "noscript", "svg", "form"
        ]):
            element.decompose()

        text = soup.get_text(separator=" ", strip=True)
        return clean_text(text)

    except Exception:
        return ""

# --------------------------------------------------
# SPLIT INTO SENTENCES / CHUNKS
# --------------------------------------------------

def split_sentences(text):
    text = clean_text(text)
    sentences = re.split(r"(?<=[.!?])\s+", text)

    return [
        s.strip()
        for s in sentences
        if 30 <= len(s.strip()) <= 500
    ]


def split_text(text, chunk_size=520):
    sentences = split_sentences(text)
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= chunk_size:
            current += (" " if current else "") + sentence
        else:
            if current.strip():
                chunks.append(current.strip())
            current = sentence

    if current.strip():
        chunks.append(current.strip())

    return chunks

# --------------------------------------------------
# QUESTION NORMALISATION
# --------------------------------------------------

QUESTION_TRANSLATIONS = {
    "简体中文": {
        "报销": "claim",
        "索赔": "claim",
        "退款": "claim",
        "牙": "dental",
        "牙科": "dental",
        "牙医": "dentist",
        "医生": "doctor",
        "看医生": "doctor",
        "救护车": "ambulance",
        "紧急": "emergency",
        "翻译": "interpreter",
        "口译": "interpreter",
        "语言": "language",
        "处方药": "prescription medicine",
        "药": "medicine",
        "区别": "difference",
        "差别": "difference",
        "比较": "compare",
        "综合": "comprehensive",
        "基础": "essentials",
    },
    "Bahasa Melayu": {
        "tuntutan": "claim",
        "bayaran balik": "claim",
        "gigi": "dental",
        "doktor": "doctor",
        "ambulans": "ambulance",
        "kecemasan": "emergency",
        "jurubahasa": "interpreter",
        "terjemahan": "interpreter",
        "ubat": "medicine",
        "preskripsi": "prescription",
        "perbezaan": "difference",
        "banding": "compare",
    }
}


def normalize_question(question, language):
    q = question.lower()

    for native, english in QUESTION_TRANSLATIONS.get(language, {}).items():
        q = q.replace(native, f" {english} ")

    return q


def clean_words(text):
    stop_words = {
        "what", "is", "are", "the", "a", "an", "does", "do",
        "my", "me", "i", "can", "how", "to", "of", "for",
        "and", "in", "with", "oshc", "medibank", "please",
        "tell", "about", "your", "between", "will", "it"
    }

    words = re.findall(r"[a-zA-Z]+", text.lower())

    return [
        word for word in words
        if word not in stop_words and len(word) > 2
    ]

# --------------------------------------------------
# SYNONYMS
# --------------------------------------------------

SYNONYMS = {
    "dentist": ["dental"],
    "teeth": ["dental"],
    "doctor": ["gp", "general practitioner"],
    "sick": ["gp", "general practitioner"],
    "medicine": ["pharmacy", "prescription", "pharmaceutical"],
    "medication": ["pharmacy", "prescription", "pharmaceutical"],
    "drug": ["pharmacy", "prescription", "pharmaceutical"],
    "refund": ["claim", "claims"],
    "reimburse": ["claim", "claims"],
    "emergency": ["ambulance", "emergency"],
    "urgent": ["emergency"],
    "compare": ["comprehensive", "essentials"],
    "difference": ["comprehensive", "essentials"],
    "interpreter": ["language", "interpreter"],
    "translation": ["language", "interpreter"],
    "psychologist": ["mental health", "psychology"],
    "mental": ["mental health"],
    "pregnancy": ["pregnancy", "maternity"],
    "physio": ["physiotherapy"],
    "physiotherapist": ["physiotherapy"],
}

# --------------------------------------------------
# SCORE CHUNKS
# --------------------------------------------------

def score_chunk(question, chunk, language):
    normalized_question = normalize_question(question, language)
    question_lower = normalized_question.lower()
    chunk_lower = chunk.lower()
    keywords = clean_words(normalized_question)

    score = 0

    for word in keywords:
        if re.search(rf"\b{re.escape(word)}\b", chunk_lower):
            score += 5

        if word in SYNONYMS:
            for synonym in SYNONYMS[word]:
                if synonym in chunk_lower:
                    score += 3

    if question_lower in chunk_lower:
        score += 8

    similarity = SequenceMatcher(
        None,
        question_lower,
        chunk_lower[:350]
    ).ratio()

    score += similarity * 2
    return score

# --------------------------------------------------
# BUILD DATABASE
# --------------------------------------------------

@st.cache_data(ttl=3600)
def build_database():
    database = []

    for source_name, url in SOURCES.items():
        text = get_page_text(url)

        if not text:
            continue

        for chunk in split_text(text):
            database.append({
                "source": source_name,
                "url": url,
                "text": chunk
            })

    return database

# --------------------------------------------------
# SEARCH
# --------------------------------------------------

def search_medibank(question, language):
    database = build_database()
    results = []

    for item in database:
        score = score_chunk(question, item["text"], language)

        if score > 0:
            results.append({
                **item,
                "score": score
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:5]

# --------------------------------------------------
# ANSWER HELPERS
# --------------------------------------------------

def detect_topic(question, results, language):
    q = normalize_question(question, language).lower()
    joined = " ".join(item["text"].lower() for item in results[:3])

    if any(x in q for x in ["difference", "compare", "comprehensive", "essentials"]):
        if "comprehensive" in joined and "essentials" in joined:
            return "compare"

    topic_map = [
        ("interpreter", ["interpreter", "translation", "language"]),
        ("claim", ["claim", "refund", "reimburse"]),
        ("emergency", ["emergency", "ambulance", "urgent"]),
        ("dental", ["dental", "dentist", "teeth"]),
        ("medicine", ["medicine", "medication", "drug", "pharmacy", "prescription"]),
    ]

    for topic, words in topic_map:
        if any(word in q for word in words):
            return topic

    return None


def evidence_supports(topic, results):
    if not topic or topic not in TEMPLATES:
        return False

    evidence = " ".join(item["text"].lower() for item in results[:3])

    matches = 0
    for keyword in TEMPLATES[topic]["keywords"]:
        if keyword.lower() in evidence:
            matches += 1

    if topic == "compare":
        return "comprehensive" in evidence and "essentials" in evidence

    return matches >= 1


def sentence_score(question, sentence, language):
    normalized_question = normalize_question(question, language)
    question_words = clean_words(normalized_question)
    s = sentence.lower()
    score = 0

    for word in question_words:
        if re.search(rf"\b{re.escape(word)}\b", s):
            score += 5

        if word in SYNONYMS:
            for synonym in SYNONYMS[word]:
                if synonym in s:
                    score += 3

    score += SequenceMatcher(
        None,
        normalized_question.lower(),
        s
    ).ratio() * 2

    return score


def fallback_extract_answer(question, results, language):
    candidates = []

    for result in results[:3]:
        for sentence in split_sentences(result["text"]):
            if any(noise in sentence.lower() for noise in [
                "cookie", "privacy", "terms and conditions",
                "student rewards", "find out more", "learn more"
            ]):
                continue

            candidates.append({
                "sentence": clean_text(sentence),
                "score": sentence_score(question, sentence, language),
            })

    candidates.sort(key=lambda x: x["score"], reverse=True)

    selected = []
    seen = set()

    for item in candidates:
        sentence = item["sentence"]

        if len(sentence) > 260:
            sentence = sentence[:260].rsplit(" ", 1)[0] + "..."

        normalized = sentence.lower()

        if normalized in seen:
            continue

        seen.add(normalized)
        selected.append(sentence)

        if len(selected) == 2:
            break

    if not selected:
        return {
            "English":
                "I couldn't find enough reliable information on the selected Medibank pages. "
                "Please use the source links below to check the official policy details.",
            "简体中文":
                "我在所选的 Medibank 官方页面中没有找到足够可靠的信息。"
                "请使用下方来源链接查看最新官方保单详情。",
            "Bahasa Melayu":
                "Saya tidak menemui maklumat yang mencukupi pada halaman Medibank yang dipilih. "
                "Sila gunakan pautan sumber di bawah untuk menyemak butiran polisi rasmi terkini."
        }[language]

    # For unknown topics, preserve official wording rather than inventing a translation.
    if language == "English":
        return "Relevant Medibank information:\n\n" + " ".join(selected)

    if language == "简体中文":
        return (
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
            st.markdown("**Official sources**")
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

    # Anchor used for automatic scrolling to the newest answer
    st.markdown('<div id="latest-answer"></div>', unsafe_allow_html=True)

    with st.chat_message("assistant"):
        st.write(answer)

        if sources:
            st.markdown("**Official sources**")
            for source in sources:
                st.markdown(
                    f"- [{source['source']}]({source['url']})"
                )

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })

    # Automatically scroll the page to the newest answer
    components.html(
        """
        <script>
            setTimeout(function() {
                const target = window.parent.document.getElementById("latest-answer");
                if (target) {
                    target.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });
                }
            }, 250);
        </script>
        """,
        height=0,
    )

# --------------------------------------------------
# DISCLAIMER
# --------------------------------------------------

st.divider()

st.markdown("""
<div class="prototype-note">
<strong>Concept prototype only.</strong><br>
This is a student project and is not an official Medibank service. Information is retrieved
from selected publicly available Medibank OSHC pages and should be confirmed against current
official policy documents.
</div>
""", unsafe_allow_html=True)
