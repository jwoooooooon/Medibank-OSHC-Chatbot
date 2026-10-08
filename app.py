import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from difflib import SequenceMatcher

st.set_page_config(
    page_title="Medibank OSHC Assistant",
    page_icon="💬",
    layout="centered"
)

st.title("💬 Medibank OSHC Assistant")
st.caption("Searches official Medibank OSHC pages for relevant information")

language = st.selectbox(
    "Choose your preferred language",
    ["English", "简体中文"]
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
# DOWNLOAD WEBSITE TEXT
# --------------------------------------------------

@st.cache_data(ttl=3600)
def get_page_text(url):

    headers = {
        "User-Agent":
            "Mozilla/5.0 (compatible; StudentProjectBot/1.0)"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Remove scripts/style/navigation noise
        for element in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header"
        ]):
            element.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text

    except Exception:
        return ""


# --------------------------------------------------
# SPLIT TEXT INTO SEARCHABLE CHUNKS
# --------------------------------------------------

def split_text(text, chunk_size=450):

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    chunks = []
    current = ""

    for sentence in sentences:

        if len(current) + len(sentence) < chunk_size:
            current += " " + sentence

        else:
            if current.strip():
                chunks.append(current.strip())

            current = sentence

    if current.strip():
        chunks.append(current.strip())

    return chunks


# --------------------------------------------------
# QUESTION KEYWORDS
# --------------------------------------------------

def clean_words(text):

    stop_words = {
        "what", "is", "are", "the", "a",
        "an", "does", "do", "my", "me",
        "i", "can", "how", "to", "of",
        "for", "and", "in", "with",
        "oshc", "medibank"
    }

    words = re.findall(
        r"[a-zA-Z]+",
        text.lower()
    )

    return [
        word
        for word in words
        if word not in stop_words
        and len(word) > 2
    ]


# --------------------------------------------------
# SCORE RELEVANCE
# --------------------------------------------------

def score_chunk(question, chunk):

    question_lower = question.lower()
    chunk_lower = chunk.lower()

    keywords = clean_words(question)

    score = 0

    # keyword matching
    for word in keywords:

        if word in chunk_lower:
            score += 4

    # useful topic synonyms
    synonyms = {
        "dentist": ["dental"],
        "teeth": ["dental"],
        "doctor": ["gp", "general practitioner"],
        "medicine": ["pharmacy", "prescription"],
        "drug": ["pharmacy", "prescription"],
        "refund": ["claim"],
        "reimburse": ["claim"],
        "emergency": ["ambulance", "emergency"],
        "compare": ["comprehensive", "essentials"],
        "difference": ["comprehensive", "essentials"],
        "interpreter": ["language", "interpreter"]
    }

    for word in keywords:

        if word in synonyms:

            for synonym in synonyms[word]:

                if synonym in chunk_lower:
                    score += 3

    # rough fuzzy similarity
    similarity = SequenceMatcher(
        None,
        question_lower,
        chunk_lower[:300]
    ).ratio()

    score += similarity

    return score


# --------------------------------------------------
# SEARCH MEDIBANK
# --------------------------------------------------

@st.cache_data(ttl=3600)
def build_database():

    database = []

    for source_name, url in SOURCES.items():

        text = get_page_text(url)

        if not text:
            continue

        chunks = split_text(text)

        for chunk in chunks:

            database.append({
                "source": source_name,
                "url": url,
                "text": chunk
            })

    return database


def search_medibank(question):

    database = build_database()

    results = []

    for item in database:

        score = score_chunk(
            question,
            item["text"]
        )

        results.append({
            **item,
            "score": score
        })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results[:3]


# --------------------------------------------------
# SIMPLE LANGUAGE OUTPUT
# --------------------------------------------------

def simplify_answer(result, language):

    text = result["text"]

    if language == "简体中文":

        return (
            "我从 Medibank 官方资料找到以下相关内容：\n\n"
            + text +
            "\n\n由于这是免费 prototype，"
            "目前不会自动把英文完整翻译成中文。"
            "建议查看下面的官方来源确认。"
        )

    return (
        "According to Medibank's official information:\n\n"
        + text
    )


# --------------------------------------------------
# CHAT HISTORY
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])

        if "source" in message:

            st.markdown(
                f"[Source: {message['source']}]"
                f"({message['url']})"
            )


# --------------------------------------------------
# USER INPUT
# --------------------------------------------------

question = st.chat_input(
    "Ask about Medibank OSHC..."
)

if question:

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.write(question)


    with st.spinner(
        "Searching Medibank official information..."
    ):

        results = search_medibank(question)


    if (
        not results
        or results[0]["score"] < 1
    ):

        answer = (
            "I couldn't find a reliable answer "
            "from the selected Medibank pages."
        )

        source = None
        url = None

    else:

        best = results[0]

        answer = simplify_answer(
            best,
            language
        )

        source = best["source"]
        url = best["url"]


    with st.chat_message("assistant"):

        st.write(answer)

        if source:

            st.markdown(
                f"**Official source:** "
                f"[{source}]({url})"
            )


    message = {
        "role": "assistant",
        "content": answer
    }

    if source:

        message["source"] = source
        message["url"] = url


    st.session_state.messages.append(
        message
    )


# --------------------------------------------------
# DISCLAIMER
# --------------------------------------------------

st.divider()

st.caption(
    "Student prototype only. "
    "Information is retrieved from selected publicly available "
    "Medibank OSHC webpages and should be confirmed against "
    "current official policy documents."
)
