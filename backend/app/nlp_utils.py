import httpx
from jamdict import Jamdict
from spacy.tokens.token import Token

from app.core import SETTING


def lemma_of_word(token: Token, language: str):
    match language:
        case "en" | "ja":
            return token.lemma_
        case "zh-cn":
            return token.text.strip()
        case _:
            raise RuntimeError("Unrachable")


async def lookup_word(word: str, language: str) -> str:
    """
    Lookup word definition by language.
    Supported: English ("en"), Japanese ("ja")
    Returns definition as plain text, or empty string if not found.
    """

    match language:
        # ---------------------------
        # English dictionary lookup
        # ---------------------------
        case "en":
            return await __lookup_english_word(word)
        case "ja":
            return await __lookup_japanese_word(word)
        case _:
            raise RuntimeError("Unrachable")


async def __lookup_english_word(word: str) -> str:
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

    async with httpx.AsyncClient(timeout=SETTING.TIMEOUT_TIME) as client:
        try:
            resp = await client.get(url)
            if not resp.is_success:
                return ""

            data = resp.json()
        except Exception:
            return ""

    # Parse definitions
    results = []
    for entry in data:
        for meaning in entry.get("meanings", []):
            pos = meaning.get("partOfSpeech", "")
            for definition in meaning.get("definitions", []):
                text = definition.get("definition")
                if text:
                    results.append(f"{pos}: {text}")

    return "\n".join(results)


async def __lookup_japanese_word(word: str) -> str:
    jam = Jamdict()
    result = jam.lookup(word)
    return result.text()
