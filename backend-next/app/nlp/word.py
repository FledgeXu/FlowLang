from spacy.tokens.token import Token


def lemma_of_word(token: Token, language: str):
    match language:
        case "en" | "ja":
            return token.lemma_
        case "zh-cn":
            return token.text.strip()
        case _:
            raise RuntimeError("Unrachable")
