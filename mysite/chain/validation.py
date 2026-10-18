import re
import unicodedata

from langchain_core.runnables import RunnableLambda

BLOCKED_WORDS = [
    "бомб",
    "наркотик",
    "взрывчат",
    "bomb",
    "narcotic",
]



class InputRejected(ValueError):
    pass


def normalize_text(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).split())


def check_length(text: str) -> str:
    if not text:
        raise InputRejected("Сообщение не должно быть пустым")
    if len(text) > 3000 or len(text.split()) > 200:
        raise InputRejected("Максимум 200 слов и 3000 символов")
    return text


def check_blocked_words(text: str) -> str:
    lower_text = text.lower()

    for word in BLOCKED_WORDS:
        if word in lower_text:
            raise InputRejected("Сообщение содержит запрещённые слова")

    return text

input_chain = (
    RunnableLambda(normalize_text)
    | RunnableLambda(check_length)
    | RunnableLambda(check_blocked_words)
)
