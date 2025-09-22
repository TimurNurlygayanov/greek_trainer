# Greek words:
# https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Modern_Greek/5K_Wordlist
# https://1000mostcommonwords.com/1000-most-common-greek-words/
#

import time

from deep_translator import GoogleTranslator

# === Таблицы ===

# Ударные гласные
accented_vowels = {
    "ά": "á", "έ": "é", "ή": "í", "ί": "í", "ό": "ó", "ύ": "í", "ώ": "ó",
}

# Многобуквенные сочетания (до одиночных букв)
multi_rules = {
    "αι": "э",
    "ει": "и",
    "οι": "и",
    "υι": "и",
    "ου": "у",
    "αυ": "ав",   # потом правим на "аф"
    "ευ": "эв",   # потом правим на "эф"
    "ηυ": "ив",   # потом правим на "иф"
    "γγ": "нг",
    "γκ": "нг",
    "μπ": "б",
    "ντ": "д",
    "τσ": "ц",
    "τζ": "дж",
}

# Одиночные буквы
single_rules = {
    'α': 'а', 'β': 'в', 'γ': 'г', 'δ': 'д', 'ε': 'э', 'ζ': 'з',
    'η': 'и', 'θ': 'т', 'ι': 'и', 'κ': 'к', 'λ': 'л', 'μ': 'м',
    'ν': 'н', 'ξ': 'кс', 'ο': 'о', 'π': 'п', 'ρ': 'р', 'σ': 'с',
    'ς': 'с', 'τ': 'т', 'υ': 'и', 'φ': 'ф', 'χ': 'х', 'ψ': 'пс',
    'ω': 'о',
}

# Согласные, после которых αυ/ευ/ηυ читаются как "ф"
voiceless_cons = "κπτξψχσθφ"

# === Функции ===


def greek_to_russian_pron(word):
    w = word.lower()
    result = ""
    i = 0
    while i < len(w):
        # 1. Ударные гласные
        if w[i] in accented_vowels:
            result += accented_vowels[w[i]]
            i += 1
            continue
        # 2. Многобуквенные сочетания
        matched = False
        for combo, rus in multi_rules.items():
            if w.startswith(combo, i):
                result += rus
                i += len(combo)
                matched = True
                break
        if matched:
            continue
        # 3. Одиночные буквы
        ch = w[i]
        result += single_rules.get(ch, ch)
        i += 1

    # === Постобработка: αυ/ευ/ηυ перед глухими согласными ===
    for vowel in ["ав", "эв", "ив"]:
        for c in voiceless_cons:
            result = result.replace(vowel + c, vowel[0] + "ф" + c)

    return result


def main():
    with open("words/greek_verbs_top228_only.txt", mode="r") as f:
        greek_words = f.readlines()

    greek_words = [w.strip() for w in greek_words if w.strip()]

    translator = GoogleTranslator(source="el", target="ru")

    for w in greek_words:
        pron = greek_to_russian_pron(w)
        tr = translator.translate(w)
        print('{greek: "' + w + '", pron: "' + pron + '", rus: "' + tr + '"},')
        time.sleep(0.1)


if __name__ == "__main__":
    main()
