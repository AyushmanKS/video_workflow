import re

HI_0_99 = ("शून्य एक दो तीन चार पाँच छह सात आठ नौ दस ग्यारह बारह तेरह चौदह पंद्रह सोलह सत्रह अठारह उन्नीस "
           "बीस इक्कीस बाईस तेईस चौबीस पच्चीस छब्बीस सत्ताईस अट्ठाईस उनतीस तीस इकतीस बत्तीस तैंतीस चौंतीस पैंतीस "
           "छत्तीस सैंतीस अड़तीस उनतालीस चालीस इकतालीस बयालीस तैंतालीस चवालीस पैंतालीस छियालीस सैंतालीस अड़तालीस "
           "उनचास पचास इक्यावन बावन तिरपन चौवन पचपन छप्पन सत्तावन अट्ठावन उनसठ साठ इकसठ बासठ तिरसठ चौंसठ पैंसठ "
           "छियासठ सड़सठ अड़सठ उनहत्तर सत्तर इकहत्तर बहत्तर तिहत्तर चौहत्तर पचहत्तर छिहत्तर सतहत्तर अठहत्तर उन्यासी "
           "अस्सी इक्यासी बयासी तिरासी चौरासी पचासी छियासी सत्तासी अट्ठासी नवासी नब्बे इक्यानबे बानबे तिरानबे चौरानबे "
           "पंचानबे छियानबे सत्तानबे अट्ठानबे निन्यानबे").split()
EN_ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
EN_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def hi_words(n):
    if n < 100:
        return HI_0_99[n]
    for value, word in ((10 ** 7, "करोड़"), (10 ** 5, "लाख"), (1000, "हज़ार"), (100, "सौ")):
        if n >= value:
            head, rest = divmod(n, value)
            return f"{hi_words(head)} {word}" + (f" {hi_words(rest)}" if rest else "")
    return str(n)


def en_words(n):
    if n < 20:
        return EN_ONES[n]
    if n < 100:
        t, o = divmod(n, 10)
        return EN_TENS[t] + (f"-{EN_ONES[o]}" if o else "")
    for value, word in ((10 ** 9, "billion"), (10 ** 6, "million"), (1000, "thousand"), (100, "hundred")):
        if n >= value:
            head, rest = divmod(n, value)
            return f"{en_words(head)} {word}" + (f" {en_words(rest)}" if rest else "")
    return str(n)


def spell_numbers(text, language):
    conv = hi_words if language in ("hi", "mr") else en_words
    def repl(m):
        digits = m.group(0).replace(",", "")
        return conv(int(digits)) if digits.isdigit() and len(digits) <= 9 else m.group(0)
    text = text.translate(str.maketrans("०१२३४५६७८९", "0123456789"))
    return re.sub(r"\d[\d,]*", repl, text)
