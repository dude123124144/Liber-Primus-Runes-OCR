from scipy import misc
import os
import sys

PATH = ""

skip_pixels_i = 1
skip_pixels_j = 1
left_limit = 600 / skip_pixels_j
right_limit = 1800 / skip_pixels_j
top_limit = 666 / skip_pixels_i
bottom_limit = 2900 / skip_pixels_i

def reduce_image(image):
    return image[::skip_pixels_i, ::skip_pixels_j]

def binarise(image):
    threshold = 150
    binary_map = []

    for row in image:
        r = []

        for pixel in row:
            if pixel < threshold:
                r.append(1)
            else:
                r.append(0)

        binary_map.append(r)

    return binary_map

def get_lines(bmap):
    is_text_line = []
    text_lines = []

    for row in bmap:
        count = 0
        prev = 0

        for bit in row:
            if bit == 1 and prev == 0:
                count += 1
            
            prev = bit

        if count > 5:
            is_text_line.append(1)
        else:
            is_text_line.append(0)

    prev = 0
    start = 0
    end = 0
    for val in is_text_line:
        if val == 0 and prev == 0:
            start += 1
            end += 1
        elif val == 1 and prev == 0:
            end += 1
        elif val == 1 and prev == 1:
            end += 1
        elif val == 0 and prev == 1:
            text_lines.append([start, end])
            start = end + 1
            end = start

        prev = val

    return text_lines

def get_char_lines_per_line(line_bmap):
    is_char_line = []
    char_lines = []

    for c in range(len(line_bmap[0])):
        count = 0

        for r in range(len(line_bmap)):
            if line_bmap[r][c] == 1:
                count += 1

        if count > 2:
            is_char_line.append(1)
        else:
            is_char_line.append(0)

    prev = 0
    start = 0
    end = 0
    for val in is_char_line:
        if val == 0 and prev == 0:
            start += 1
            end += 1
        elif val == 1 and prev == 0:
            end += 1
        elif val == 1 and prev == 1:
            end += 1
        elif val == 0 and prev == 1:
            char_lines.append([start, end])
            start = end + 1
            end = start

        prev = val

    return char_lines

def get_chars(bmap):
    text_lines = get_lines(bmap)
    line_bmaps = []
    char_lines = []
    char_bmaps = []

    for line in text_lines:
        line_bmaps.append(bmap[line[0]:(line[1]+1)])

    for line_bmap in line_bmaps:
        char_lines.append(get_char_lines_per_line(line_bmap))

    l = 0
    for line in text_lines:
        line_bmap = []

        for char in char_lines[l]:
            char_bmap = []
        
            for i in range(line[0], line[1] + 1):
                char_bmap.append(bmap[i][char[0]:(char[1] + 1)])

            line_bmap.append(char_bmap)
        char_bmaps.append(line_bmap)
        l += 1

    return char_bmaps

def crop_letter(letter_bmap):
    start_c = 0
    start_r = 0
    end_c = len(letter_bmap[0]) - 1
    end_r = len(letter_bmap) - 1
    cropped_char = []

    for line in letter_bmap:
        empty = 1
        for bit in line:
            if bit == 1:
                empty = 0
                break

        if empty == 1:
            start_r += 1
        else:
            break

    for line in reversed(letter_bmap):
        empty = 1
        for bit in line:
            if bit == 1:
                empty = 0
                break

        if empty == 1:
            end_r -= 1
        else:
            break

    for j in range(len(letter_bmap[0])):
        empty = 1
        for i in range(len(letter_bmap)):
            if letter_bmap[i][j] == 1:
                empty = 0
                break

        if empty == 1:
            start_c += 1
        else:
            break

    for j in reversed(range(len(letter_bmap[0]))):
        empty = 1
        for i in range(len(letter_bmap)):
            if letter_bmap[i][j] == 1:
                empty = 0
                break

        if empty == 1:
            end_c -= 1
        else:
            break

    for r in range(start_r, end_r + 1):
        cropped_char.append(letter_bmap[r][start_c:(end_c+1)])

    return cropped_char

def recognize_char(char_bmap, letters_bmaps):
    min_error = 100000000
    letter_index = 0
    l = 0
    
    for letter in letters_bmaps:
        the_letter = letter['data']
        error = 0

        min_i = min(len(the_letter), len(char_bmap))
        min_j = min(len(the_letter[0]), len(char_bmap[0]))
        max_i = max(len(the_letter), len(char_bmap))
        max_j = max(len(the_letter[0]), len(char_bmap[0]))
        max_i_image = the_letter
        max_j_image = the_letter

        if len(the_letter) == min_i:
             max_i_image = char_bmap

        if len(the_letter[0]) == min_j:
             max_j_image = char_bmap

        # The two image sizes may differ.
        # Assume the smaller image would have
        # contained 0's if it had same size.
        for i in range(min_i):
            for j in range(min_j):
                if the_letter[i][j] != char_bmap[i][j]:
                    error += 1
      
            for j in range(min_j + 1, max_j):
                if max_j_image[i][j] == 1:
                    error += 1
        
        for i in range(min_i + 1, max_i):
            for j in range(0, min_j):
                if max_i_image[i][j] == 1:
                    error += 1

            if max_i_image == max_j_image:
                for j in range(min_j + 1, max_j):
                    if max_i_image[i][j] == 1:
                        error += 1

        if error < min_error:
            min_error = error
            letter_index = l

        l += 1

    if float(min_error) / float(len(char_bmap) * len(char_bmap[0])) > 0.2:
        return 0, []

    return 1, letters_bmaps[letter_index]['name']

def get_text(char_bmaps):
    text = []
    letters = []

    for f in os.listdir(PATH+"letters"):
        letters.append({'name': f.strip(".bmp"), 'data': crop_letter(binarise(reduce_image(misc.imread(PATH+"letters/"+f, flatten=True))))})

    for line in char_bmaps:
        text_line = []

        c = 0
        while c < len(line):
            is_valid_char, value = recognize_char(crop_letter(line[c]), letters)

            if is_valid_char == 1:
                if value == "DOT":
                    if c == len(line) - 1:
                        text_line.append("  ")
                    else:
                        is_valid_char, value = recognize_char(line[c+1], letters)

                        if is_valid_char == 1 and value == "TWO_DOTS":
                            text_line.append(".  ")
                            c += 2
                        else:
                            text_line.append("  ")
                elif value == "TWO_DOTS":
                    text_line.append(",  ")
                elif value == "THREE_DOTS":
                    text_line.append(":  ")
                    c += 2
                elif value == "FIVE_DOTS":
                    text_line.append(":  ")
                    c += 1
                elif value == "QUOTE":
                    text_line.append("\'")
                else:
                    text_line.append(value + " ")
            else:
                pass

            c += 1

        text.append(text_line)
        
    return text

if len(sys.argv) < 2:
    print "Usage: python rune_translate <input_file>"
    sys.exit()

rune_image = misc.imread(sys.argv[1], flatten=True)
image = reduce_image(rune_image)
bmap = binarise(image)
#bmap = [[bmap[r][c] for c in range(600,1801)] for r in range(666,2901)]
#bmap = [[bmap[r][c] for c in range(190, 610)] for r in range(220, 980)]
bmap = [[bmap[r][c] for c in range(left_limit, right_limit + 1)] for r in range(top_limit, bottom_limit + 1)]

char_bmaps = get_chars(bmap)
text = get_text(char_bmaps)

for line in text:
    string = ""
    for char in line:
        string += "%s"%char

    print string
