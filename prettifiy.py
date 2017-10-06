import os, ctypes, sys
# USE only for debug
import pdb

KEYWORDS_TAB_MAP = {
    'Feature:': 0,
    'Scenario:': 1,
    'Scenario': 1,
    'Given': 2,
    'When': 2,
    'Then': 2,
    'And': 3,
    'Examples:': 2
}
TAG_KEYWORD = "@"
TAB_KEYWORD = "|"
COMMENT_KEYWORD = "#"
# Add "Examples:" to the list to get extra blank line between last step and Examples section.
#EXTRA_BLANK_LINE_KEYWORD = "Examples:"
EXTRA_BLANK_LINE_KEYWORD = ""
DOUBLE_EXTRA_BLANK_LINE_KEYWORD = "Feature:"
EXTRA_TAB_KEYWORDS = ['Given', 'When', 'Then', 'And', 'Examples:']
TAB_SIGN = " "
TAB_DISTANCE_SIGN = " "
BLANK_LINE = "\n"
WORDS_SEPARATOR = ";"
TAB_SIZE = 2
TEMP_FILE_NAME = "temp.feature"

def formatter(lines, last_keywords, temp_file, lines_numbers_map=None, tables_lines_numbers=list(), tables_count=0,
              tables=None):
    if lines_numbers_map is None:
        lines_numbers_map = dict()
    lines_count = len(lines)-1
    last_line = ""
    additional_tab = ""
    keywords = list()
    if lines_count >= 0:
        keywords = last_keywords
        words = lines[lines_count].split()
        if len(words) > 0:
            if words[0] in KEYWORDS_TAB_MAP.keys():
                if TAG_KEYWORD in words[0]:
                    keywords.append(TAG_KEYWORD)
                else:
                    keywords.append(words[0])
                lines_numbers_map[lines_count] = len(keywords)
            elif words[0][0] in [COMMENT_KEYWORD, TAG_KEYWORD]:
                keywords.append(words[0][0])
                lines_numbers_map[lines_count] = len(keywords)
            elif words[0][0] == TAB_KEYWORD:
                keywords.append(TAB_KEYWORD)
                lines_numbers_map[lines_count] = len(keywords)
                table_number = str(tables_count)
                tables_lines_count = len(tables_lines_numbers)
                if tables_lines_count != 0:
                    if int(tables_lines_numbers[tables_lines_count-1])-1 != lines_count:
                        tables_count += 1
                        table_number = str(tables_count)
                elif tables_lines_count == 0:
                    tables_count += 1
                    table_number = str(tables_count)

                if tables is None:
                    tables = {table_number: {'longest_words_lengths': {}}}
                elif table_number not in tables.keys():
                    tables[table_number] = {'longest_words_lengths': {}}

                words = lines[lines_count].split(TAB_KEYWORD)[1:-1]
                line_number = str(lines_count-1)
                for word in words:
                    stripped_word = word.strip()
                    if line_number not in tables[table_number].keys():
                        tables[table_number][line_number] = dict()
                        tables[table_number][line_number]['words'] = stripped_word
                    else:
                        tables[table_number][line_number]['words'] = \
                            "".join([tables[table_number][line_number]['words'], WORDS_SEPARATOR, stripped_word])

                    column_index = words.index(word)+1
                    if column_index not in tables[table_number]['longest_words_lengths'].keys():
                        tables[table_number]['longest_words_lengths'][column_index] = 0

                    word_length = len(stripped_word)
                    if word_length > tables[table_number]['longest_words_lengths'][column_index]:
                        tables[table_number]['longest_words_lengths'][column_index] = word_length

                tables_lines_numbers.append(lines_count)
            else:
                lines_numbers_map[lines_count] = len(keywords)

        last_line = lines.pop(lines_count)
        line, last_keywords, last_tables_count, last_tables, last_tab = \
            formatter(lines, keywords, temp_file, lines_numbers_map, tables_lines_numbers, tables_count, tables)
        line_words = line.split()

        if len(line_words) != 0:
            if lines_count-1 not in tables_lines_numbers:
                keyword_index = lines_numbers_map[lines_count-1]-1

                tab = ""
                if last_keywords[keyword_index] in KEYWORDS_TAB_MAP.keys():
                    tab = KEYWORDS_TAB_MAP[last_keywords[keyword_index]] * TAB_SIZE * TAB_SIGN

                extra_blank_lines = ""

                if last_keywords[keyword_index] == DOUBLE_EXTRA_BLANK_LINE_KEYWORD:
                    extra_blank_lines = "".join([BLANK_LINE, BLANK_LINE])
                elif keyword_index-1 < len(keywords) and keywords[keyword_index-1] == EXTRA_BLANK_LINE_KEYWORD:
                    extra_blank_lines = BLANK_LINE
                temp_file.writelines([tab, " ".join(line_words), BLANK_LINE, extra_blank_lines])
            else:
                keyword_index = lines_numbers_map[lines_count-1]-1
                split_row_words = last_tables[str(last_tables_count)][str(lines_count-2)]['words'].split(WORDS_SEPARATOR)

                table_row = ""
                word_column_index = 1
                for word_in_row in split_row_words:
                    longest_world_in_row_length = \
                        last_tables[str(last_tables_count)]['longest_words_lengths'][word_column_index]
                    word_column_index += 1
                    distance = longest_world_in_row_length - len(word_in_row)

                    if last_keywords[keyword_index+1] in EXTRA_TAB_KEYWORDS:
                        additional_tab = ((KEYWORDS_TAB_MAP[last_keywords[keyword_index+1]])+1) * TAB_SIZE * TAB_SIGN
                    elif last_keywords[keyword_index+1] == TAB_KEYWORD:
                        additional_tab = last_tab

                    if table_row == "":
                        table_row = "".join([table_row, TAB_KEYWORD, TAB_DISTANCE_SIGN, word_in_row,
                                             TAB_SIGN * distance])
                    else:
                        table_row = "".join([table_row, TAB_DISTANCE_SIGN, TAB_KEYWORD, TAB_DISTANCE_SIGN,
                                             word_in_row, TAB_SIGN * distance])
                table_row = "".join([additional_tab, table_row, TAB_DISTANCE_SIGN, TAB_KEYWORD])
                temp_file.writelines([table_row, BLANK_LINE])

                if last_keywords[keyword_index-1] == TAG_KEYWORD:
                    temp_file.writelines([BLANK_LINE, BLANK_LINE])
    return last_line, keywords, tables_count, tables, additional_tab


def prettify(arguments):
    try:
        if len(arguments) > 1:
            file_name = arguments[1]
            if os.path.exists(file_name):

                with open(file_name, 'r') as opened_file:
                    lines = opened_file.readlines()
                    if lines[len(lines)-1] != BLANK_LINE:

                        with open(file_name, 'a') as opened_file_for_append:
                            opened_file_for_append.write("".join([BLANK_LINE, BLANK_LINE]))

                with open(TEMP_FILE_NAME, 'w') as temp_file:
                    with open(file_name, 'r') as opened_file:
                        lines = opened_file.readlines()
                        formatter(lines, [], temp_file, {}, tables_lines_numbers=list(), tables_count=0, tables=None)

                os.remove(file_name)
                os.rename(TEMP_FILE_NAME, file_name)
                print "".join(["FILE: ", file_name, " PRETTIFIED."])
            else:
                print "PROVIDED FILE DOES NOT EXIST."
        else:
            print "FILE NAME NOT PROVIDED."
    except IOError:
        params = ' '.join([os.path.abspath(sys.argv[0])] + sys.argv[1:])
        if ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(params), None, 0) != 42:
            print "NO PERMISSION TO RUN THIS SCRIPT"


prettify(sys.argv)