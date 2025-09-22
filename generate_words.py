# Greek words:
# https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Modern_Greek/5K_Wordlist
# https://1000mostcommonwords.com/1000-most-common-greek-words/
#

import time

from deep_translator import GoogleTranslator

# === Таблицы ===

# Ударные гласные (оставляю как было + добавил варианты с диерезисом)
accented_vowels = {
    "ά": "á", "έ": "é", "ή": "í", "ί": "í", "ό": "ó", "ύ": "í", "ώ": "ó",
    "ΐ": "í", "ΰ": "í",
}

# Сопоставление буквы без ударения (для сопоставления диграфов)
tonos_to_base = {
    "ά": "α", "έ": "ε", "ή": "η", "ί": "ι", "ό": "ο", "ύ": "υ", "ώ": "ω",
}
# Буквы с диерезисом: не должны образовывать дифтонги
diaeresis_letters = set(["ϊ", "ϋ", "ΐ", "ΰ"])

# Многобуквенные сочетания (порядок не важен — в коде сортируется по длине)
multi_rules = {
    "αι": "э",
    "ει": "и",
    "οι": "и",
    "υι": "и",
    "ου": "у",

    # лабиальные дифтонги — базовая форма, дальше в функции решаем v/f
    "αυ": "ав",
    "ευ": "эв",
    "ηυ": "ив",

    # носовые
    "γγ": "нг",
    "γκ": "нг",  # в начале слова будет 'г' (правим в функции)
    "γχ": "нх",
    "γξ": "нкс",

    # аффрикаты
    "μπ": "б",   # в середине слова будет 'мб' (правим в функции)
    "ντ": "д",   # в середине слова будет 'нд' (правим в функции)
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

    # диерезис → отдельная "и"
    'ϊ': 'и', 'ϋ': 'и', 'ΐ': 'í', 'ΰ': 'í',
}

# Согласные, после которых αυ/ευ/ηυ читаются как "ф" (+ конечный сигма)
voiceless_cons = "κπτξψχσθφς"

# === Функции ===

def greek_to_russian_pron(word):
    def char_matches(expected_base: str, actual: str) -> bool:
        """Сопоставление буквы шаблона без ударения с фактической буквой,
        учитывая варианты с τόνος, но исключая диерезис."""
        if actual == expected_base:
            return True
        if actual in tonos_to_base and tonos_to_base[actual] == expected_base:
            return True
        return False

    def is_voiceless(actual: str) -> bool:
        base = tonos_to_base.get(actual, actual)
        return base in voiceless_cons

    def has_diaeresis(ch: str) -> bool:
        return ch in diaeresis_letters

    w = word.lower()
    result = ""
    i = 0

    # подготовим список сочетаний от длинного к короткому (на будущее)
    combos = sorted(multi_rules.keys(), key=len, reverse=True)

    while i < len(w):
        matched = False

        # 1) Многобуквенные сочетания (учёт ударений внутри)
        for combo in combos:
            L = len(combo)
            if i + L > len(w):
                continue

            # не склеиваем, если внутри стоят буквы с диерезисом
            segment = w[i:i+L]
            if any(has_diaeresis(ch) for ch in segment):
                continue

            if all(char_matches(combo[k], segment[k]) for k in range(L)):
                rus = multi_rules[combo]

                # позиционные поправки
                if combo == "γκ":
                    rus = "г" if i == 0 else "нг"
                elif combo == "μπ":
                    rus = "б" if i == 0 else "мб"
                elif combo == "ντ":
                    rus = "д" if i == 0 else "нд"

                # контекст для αυ/ευ/ηυ → v/f
                if combo in ("αυ", "ευ", "ηυ"):
                    nxt = w[i+L] if i + L < len(w) else ""
                    if not nxt or is_voiceless(nxt):
                        rus = rus[0] + "ф"  # аф/эф/иф

                result += rus
                i += L
                matched = True
                break

        if matched:
            continue

        # 2) Ударные одиночные гласные
        ch = w[i]
        if ch in accented_vowels:
            result += accented_vowels[ch]
            i += 1
            continue

        # 3) Одиночные буквы
        result += single_rules.get(ch, ch)
        i += 1

    # Постобработка из исходного кода оставляю — теперь, по сути, идемпотентна.
    for vowel in ["ав", "эв", "ив"]:
        for c in voiceless_cons:
            result = result.replace(vowel + c, vowel[0] + "ф" + c)
        # конец слова
        if result.endswith(vowel):
            result = result[:-2] + (vowel[0] + "ф")

    return result



def main():
    with open("words/greek_A2_theme15_basic_verbs.txt", mode="r") as f:
        greek_words = f.readlines()

    greek_words = [w.strip() for w in greek_words if w.strip() and '#' not in w]

    translator = GoogleTranslator(source="el", target="ru")

    for w in greek_words:
        if '–' in w:
            w, tr = w.split('–')
        elif '—' in w:
            w, tr = w.split('—')
        else:
            tr = translator.translate(w)

        pron = greek_to_russian_pron(w)
        print('{greek: "' + w + '", pron: "' + pron + '", rus: "' + tr + '"},')
        time.sleep(0.1)


if __name__ == "__main__":
    main()
