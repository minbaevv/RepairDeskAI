import pytest

from mysite.chain.validation import InputRejected, input_chain


def test_normalize():
    assert input_chain.invoke("  Починить   ноутбук  ") == "Починить ноутбук"


@pytest.mark.parametrize("text", ["", "  ", "слово " * 201, "а" * 3001])
def test_invalid_length(text):
    with pytest.raises(InputRejected):
        input_chain.invoke(text)


@pytest.mark.parametrize("text", ["бомба", "НАРКОТИКИ", "взрывчатка", "bomb"])
def test_blocked_words(text):
    with pytest.raises(InputRejected):
        input_chain.invoke(text)


def test_allowed_word():
    assert input_chain.invoke("Сломалась кнопка") == "Сломалась кнопка"
