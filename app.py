import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from difflib import SequenceMatcher
import html
from google import genai

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

st.set_page_config(
    page_title="Medibank OSHC Assistant",
    page_icon="💬",
    layout="centered"
)

st.title("💬 Medibank OSHC Assistant")
st.caption("Searches official Medibank OSHC pages for relevant information")

# language selector

language = st.selectbox(
    "Choose your preferred language",
    ["English", "简体中文"]
)

# clickable suggested question

st.markdown("### Try asking:")

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
# TEXT CLEANING
# --------------------------------------------------

def clean_text(text):

    # Decode HTML entities
    text = html.unescape(text)

    # Try to repair common UTF-8 mojibake
    try:
        text = text.encode("latin1").decode("utf-8")
    except:
        pass

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
        "â‚¬": "€"
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    text = re.sub(r"\s+", " ", text)

    text = re.sub(
        r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]",
        "",
        text
    )

    return text.strip()


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

        # Force correct encoding if needed
        response.encoding = "utf-8"

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Remove noise
        for element in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "noscript"
        ]):
            element.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        return clean_text(text)

    except Exception:
        return ""


# --------------------------------------------------
# SPLIT INTO SENTENCES / CHUNKS
# --------------------------------------------------

def split_sentences(text):

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    return [
        s.strip()
        for s in sentences
        if len(s.strip()) > 30
    ]


def split_text(text, chunk_size=500):

    sentences = split_sentences(text)

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
        "oshc", "medibank",
        "please", "tell", "about"
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
# SYNONYMS
# --------------------------------------------------

SYNONYMS = {
    "dentist": ["dental"],
    "teeth": ["dental"],

    "doctor": ["gp", "general practitioner"],
    "sick": ["gp", "general practitioner"],

    "medicine": ["pharmacy", "prescription"],
    "medication": ["pharmacy", "prescription"],
    "drug": ["pharmacy", "prescription"],

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
    "physiotherapist": ["physiotherapy"]
}


# --------------------------------------------------
# SCORE CHUNK
# --------------------------------------------------

def score_chunk(question, chunk):

    question_lower = question.lower()
    chunk_lower = chunk.lower()

    keywords = clean_words(question)

    score = 0

    # direct keywords
    for word in keywords:

        if word in chunk_lower:
            score += 5

    # synonym matches
    for word in keywords:

        if word in SYNONYMS:

            for synonym in SYNONYMS[word]:

                if synonym in chunk_lower:
                    score += 3

    # phrase bonus
    if question_lower in chunk_lower:
        score += 8

    # fuzzy similarity
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

        chunks = split_text(text)

        for chunk in chunks:

            database.append({
                "source": source_name,
                "url": url,
                "text": chunk
            })

    return database


# --------------------------------------------------
# SEARCH TOP RESULTS
# --------------------------------------------------

def search_medibank(question):

    database = build_database()

    results = []

    for item in database:

        score = score_chunk(
            question,
            item["text"]
        )

        if score > 0:
            results.append({
                **item,
                "score": score
            })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results[:3]

def generate_ai_answer(question, results, language):

    if not results:
        return "I couldn't find enough information from the Medibank website."

    context = ""

    for result in results[:3]:
        context += f"""
Source: {result['source']}
Information:
{result['text']}

"""

    prompt = f"""
You are a Medibank OSHC information assistant.

Answer the user's question using ONLY the official Medibank
information provided below.

User question:
{question}

Official Medibank information:
{context}

Preferred language:
{language}

Rules:
- Answer in the user's preferred language.
- Use natural and easy-to-understand language.
- Keep the answer concise.
- Do not invent insurance benefits or policy details.
- If the provided information is insufficient, clearly say so.
- Do not provide medical diagnosis.
- Do not mention that you are Gemini.
- Do not say "according to the context".
- Answer directly like a helpful customer support assistant.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text
        
# --------------------------------------------------
# SCORE INDIVIDUAL SENTENCES
# --------------------------------------------------

def score_sentence(question, sentence):

    question_words = clean_words(question)
    sentence_lower = sentence.lower()

    score = 0

    for word in question_words:

        if word in sentence_lower:
            score += 5

        if word in SYNONYMS:

            for synonym in SYNONYMS[word]:

                if synonym in sentence_lower:
                    score += 3

    similarity = SequenceMatcher(
        None,
        question.lower(),
        sentence_lower
    ).ratio()

    score += similarity * 2

    return score


# --------------------------------------------------
# CREATE CONCISE ANSWER FROM TOP 3 CHUNKS
# --------------------------------------------------

def create_concise_answer(question, results, language):

    candidate_sentences = []

    for result in results:

        sentences = split_sentences(
            result["text"]
        )

        for sentence in sentences:

            score = score_sentence(
                question,
                sentence
            )

            candidate_sentences.append({
                "sentence": sentence,
                "score": score,
                "source": result["source"],
                "url": result["url"]
            })

    # Highest scoring first
    candidate_sentences.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    selected = []
    seen = set()

    for item in candidate_sentences:

        sentence = clean_text(
            item["sentence"]
        )

        if len(sentence) > 280:
            sentence = sentence[:280].rsplit(" ", 1)[0] + "..."

        # Avoid duplicates
        normalized = sentence.lower()

        if normalized in seen:
            continue

        # Avoid useless navigation fragments
        if len(sentence) < 35:
            continue

        seen.add(normalized)
        selected.append(item)

        if len(selected) == 2:
            break

    if not selected:
        return None, []

    answer_text = " ".join(
        item["sentence"]
        for item in selected
    )

    if language == "简体中文":
        answer = (
            "我从 Medibank 官方资料中找到以下最相关的信息：\n\n"
            + answer_text
            + "\n\n"
            + "这个免费 prototype 目前不会自动进行完整中文翻译，"
              "但会优先抽取与你问题最相关的官方内容。"
        )
    else:
        answer = (
            "Based on Medibank's official information:\n\n"
            + answer_text
        )

    return answer, selected


# --------------------------------------------------
# CHAT HISTORY
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])

        if "sources" in message:

            st.markdown("**Sources:**")

            for source in message["sources"]:

                st.markdown(
                    f"- [{source['source']}]"
                    f"({source['url']})"
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

    with st.spinner(
        "Searching Medibank official information..."
    ):

        results = search_medibank(question)

        answer = generate_ai_answer(
            question,
            results,
            language
        )

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
                    f"- [{source['source']}]"
                    f"({source['url']})"
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
    "Student prototype only. "
    "Information is retrieved from selected publicly available "
    "Medibank OSHC webpages and should be confirmed against "
    "current official policy documents."
)
