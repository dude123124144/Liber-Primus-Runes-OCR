import re

table = [
    ["ᚠ", "F"], 
    ["ᚢ", "U"],
    ["ᚦ", "TH"],
    ["ᚩ", "O"],
    ["ᚱ", "R"],
    ["ᚳ", "C"],
    ["ᚷ", "G"],
    ["ᚹ", "W"],
    ["ᚻ", "H"],
    ["ᚾ", "N"],
    ["ᛁ", "I"],
    ["ᛂ", "J"],
    ["ᛇ", "EO"],
    ["ᛈ", "P"],
    ["ᛉ", "X"],
    ["ᛋ", "S"],
    ["ᛏ", "T"],
    ["ᛒ", "B"],
    ["ᛖ", "E"],
    ["ᛗ", "M"],
    ["ᛚ", "L"],
    ["ᛝ", "ING"],
    ["ᛟ", "OE"],
    ["ᛞ", "D"],
    ["ᚪ", "A"],
    ["ᚫ", "AE"],
    ["ᚣ", "Y"],
    ["ᛡ", "IA"],
    ["ᛠ", "EA"]
]

## Translate an english string in runes
## Tries to find the minimal rune representation of the string
##
## Thanks to Nem0 for the advice on how to do this!

## NOTE: crashdemons noticed problem when OEOEO for example.
## Greedy approach would translate as OE-OE-O, but since EO shows up before OE in the chars,
## the regex substitution will replace EO first, giving O-EO-EO.
def english_to_runes(string):
    runes = ["ᛝ", "ᚦ", "ᛇ", "ᛝ", "ᛟ", "ᚫ", "ᛡ", "ᛡ", "ᛠ", "ᚳᚹ", "ᚠ", "ᚢ", "ᚢ", "ᚩ", "ᚱ", "ᚳ", "ᚳ", "ᚳ", "ᚷ", "ᚹ", "ᚻ", "ᚾ", "ᛁ", "ᛂ", "ᛈ", "ᛉ", "ᛋ", "ᛋ", "ᛏ", "ᛒ", "ᛖ", "ᛗ", "ᛚ", "ᛞ", "ᚪ", "ᚣ"]
    chars = ["ING", "TH", "EO", "NG", "OE", "AE", "IA", "IO", "EA", "QU", "F", "U", "V", "O", "R", "C", "K", "Q", "G", "W", "H", "N", "I", "J", "P", "X", "S", "Z", "T", "B", "E", "M", "L", "D", "A", "Y"]

    string = string.upper()
    for char in chars:
        string = re.sub(char, runes[chars.index(char)], string)

    return string

def runes_to_english(runeword):
    dictable = {entry[0]:entry[1] for entry in table}
    dictable["•"] = " "
    dictable["'"] = ""
    res = ""

    for rune in runeword:
        res += dictable[rune]

    return res

def get_liber_primus():
    sections = []
    pages = []
    
    f = open('transcriptions.rne')
    contents = f.read()
    f.close()

    n = 0
    for page in contents.split('\n'):
        if n == 50:
            pages.append("")
            n += 1
            continue

        # should I also replace apostrophes?
        page = re.sub("[ A-Za-z0-9\"\n]", "", page)
        page = re.sub("[.:,]", "•", page)
        pages.append(page)
        n += 1

    sections.append("".join(pages[0:3]))
    sections.append("".join(pages[3:8]))
    sections.append("".join(pages[8:15]))
    sections.append("".join(pages[15:23]))
    sections.append("".join(pages[23:27]))
    sections.append("".join(pages[27:33]))
    sections.append("".join(pages[33:40]))
    sections.append("".join(pages[40:54]))
    sections.append("".join(pages[54:56]))
    sections.append("".join(pages[56]))
    sections.append("".join(pages[57]))
    return sections

def get_liber_primus_words():
    word_list = []

    f = open('liber_primus_words.rne', 'r')
    
    for line in f.readlines():
        word_list.append(line.strip())

    f.close()
    return word_list

def get_rune_pos(rune):
    for i in range(len(table)):
        if rune in table[i]:
            return i

    return None

def sequence_to_runekey(stream):
    return [table[n % 29][0] for n in stream]

# Runes to runes from a sequence key
def sequence_shift(text, stream, direction, ignore_F = 0):
    key = sequence_to_runekey(stream)

    return runekey_shift(text, key, direction, ignore_F)

# Runes to runes from a rune key
def runekey_shift(text, ansatz, direction, ignore_F = 0):
    shifted = ""

    i = 0
    j = 0
    while i < len(ansatz) and j < len(text):
        rune1 = text[j]
        rune2 = ansatz[i]
        
        if rune1 == "•":
            shifted += "•"
            j += 1
            continue

        pos1 = get_rune_pos(rune1)
        pos2 = get_rune_pos(rune2)

        new_pos = 0

        if direction == 0:
            new_pos = (pos1 + pos2) % 29
        else:
            new_pos = (pos1 - pos2) % 29
        
        # Optionally ignore F's
        if pos1 == 0 and ignore_F == 1:
            shifted += rune1
            j += 1
            continue
        else:
            shifted += table[new_pos][0]
        
        i += 1
        j += 1

    return shifted
