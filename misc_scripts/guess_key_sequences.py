# This program allows you to specify a part of a key, and a section number.
# It then applies the key shift on every [key_length] length consecutive runes
# from the specified section, and prints the shifted runes (with whitespace)
# and the position where the key was applied, and the shift direction (forward or backward).
#
# Usage: python3 guess_key_sequences.py <key_sequence> <section_number>
#
# The key is specified in english as a command line argument, and so is the section number.
# The key is then translated in runes by the program to apply the shifts.
# Output is stored in folder key_phrases/, and the file name corresponds
# to the key phrase followed by underscore and section number.

import sys
import re
import rune_manipulation as rmanip

def numbers_to_runes(sequence):
    return [rmanip.table[n][0] for n in sequence]

if len(sys.argv) < 3:
    print("Usage: python3 %s <key_sequence> <section_number>"%sys.argv[0])
    quit()

sequence = eval(sys.argv[1])	# I like to live dangerously...
SECTION_NUM = int(sys.argv[2])

rune_ansatz = numbers_to_runes(sequence)
liber_primus = rmanip.get_liber_primus()
section = liber_primus[SECTION_NUM]
section = re.sub("[:.,\']", "", section)

f = open('kerry/' + str(sequence) + '_' + str(SECTION_NUM) + '.txt', 'a')
f.write('------- BEGIN KEY \"' + str(sequence) + '\" -------\n')
f.write('SECTION ' + str(SECTION_NUM) + '\n\n')

# Apply the key shift on every consecutive string of same length as the key.
# Both forwards and backwards.
for i in range(len(section) - len(rune_ansatz)):
    f.write("Pos: " + "%-6s"%str(i) + " Forward :\t" + rmanip.runes_to_english(rmanip.runekey_shift(section[i:], rune_ansatz, 0)) + '\n')
    f.write("Pos: " + "%-6s"%str(i) + " Backward:\t" + rmanip.runes_to_english(rmanip.runekey_shift(section[i:], rune_ansatz, 1)) + '\n')

f.write('------- END KEY \"' + str(sequence) + '\" -------\n')
f.close()
