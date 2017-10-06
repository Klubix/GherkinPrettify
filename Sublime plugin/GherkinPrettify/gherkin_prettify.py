import sublime, sublime_plugin, os, ctypes, sys

# Known issues with that solution:
## Tabs in multi line comment (#)
## Cell width while table row is a comment

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
TABLE_KEYWORD = "|"
COMMENT_KEYWORD = "#"
# Add "Examples:" to the list to get extra blank line between last step and Examples section.
#EXTRA_BLANK_LINE_KEYWORD = "Examples:"
EXTRA_BLANK_LINE_KEYWORD = ""
DOUBLE_EXTRA_BLANK_LINES_KEYWORDS = ['Feature:']
EXTRA_TAB_KEYWORDS = ['Given', 'When', 'Then', 'And', 'Examples:']
TAB_SIGN = " "
TAB_DISTANCE_SIGN = " "
BLANK_LINE = "\n"
WORDS_SEPARATOR = "?"
TAB_SIZE = 2


class GherkinPrettify():

	def _formatter(self, lines, last_keywords, file_content, lines_numbers_map=None, tables_lines_numbers=list(), tables_count=0,
				   tables=None, empty_lines_list=list()):
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
				first_word = words[0]
				if first_word in KEYWORDS_TAB_MAP.keys():
					if TAG_KEYWORD in first_word:
						keywords.append(TAG_KEYWORD)
					else:
						keywords.append(first_word)
				elif first_word[0] in [COMMENT_KEYWORD, TAG_KEYWORD]:
					keywords.append(first_word[0])
				elif first_word[0] == TABLE_KEYWORD:
					keywords.append(TABLE_KEYWORD)
					table_number = str(tables_count)
					tables_lines_count = len(tables_lines_numbers)

					if tables_lines_count != 0:
						if int(tables_lines_numbers[tables_lines_count-1])-1 != lines_count:
							if keywords[len(keywords)-2] == TAG_KEYWORD \
							or (lines_count+1 not in empty_lines_list \
							and keywords[len(keywords)-2] != COMMENT_KEYWORD) \
							or (lines_count+1 not in empty_lines_list \
							and keywords[len(keywords)-2] == COMMENT_KEYWORD \
							and lines_count+2 not in tables_lines_numbers) \
							or lines_count+1 in empty_lines_list \
							and keywords[len(keywords)-2] != TABLE_KEYWORD:
								tables_count += 1
								table_number = str(tables_count)
					elif tables_lines_count == 0:
						tables_count += 1
						table_number = str(tables_count)

					if tables is None:
						tables = {table_number: {'longest_words_lengths': {}}}
					elif table_number not in tables.keys():
						tables[table_number] = {'longest_words_lengths': {}}
					words = lines[lines_count].split(TABLE_KEYWORD)[1:-1]
					line_number = str(lines_count-1)
					column_index = 1

					for word in words:
						stripped_word = word.strip()
						if line_number not in tables[table_number].keys():
							tables[table_number][line_number] = dict()
							tables[table_number][line_number]['words'] = stripped_word
						else:
							tables[table_number][line_number]['words'] = \
								"".join([tables[table_number][line_number]['words'], WORDS_SEPARATOR, stripped_word])

						word_length = len(stripped_word)
						
						if column_index not in tables[table_number]['longest_words_lengths'].keys():
							tables[table_number]['longest_words_lengths'][column_index] = word_length

						if word_length > tables[table_number]['longest_words_lengths'][column_index]:
							tables[table_number]['longest_words_lengths'][column_index] = word_length

						column_index += 1

					tables_lines_numbers.append(lines_count)
				lines_numbers_map[lines_count] = len(keywords)
			else:
				empty_lines_list.append(lines_count)
					

			last_line = lines.pop(lines_count)
			file_content, line, last_keywords, last_tables_count, last_tables, last_tab = \
				self._formatter(lines, keywords, file_content, lines_numbers_map, tables_lines_numbers, tables_count, tables, empty_lines_list)
			line_words = line.split()

			if len(line_words) != 0:
				if lines_count-1 not in tables_lines_numbers:
					keyword_index = lines_numbers_map[lines_count-1]-1

					additional_tab = ""

					if last_keywords[keyword_index] in KEYWORDS_TAB_MAP.keys():
						additional_tab = KEYWORDS_TAB_MAP[last_keywords[keyword_index]] * TAB_SIZE * TAB_SIGN
					elif last_keywords[keyword_index] == COMMENT_KEYWORD:
						if last_keywords[keyword_index-1] not in [TABLE_KEYWORD, COMMENT_KEYWORD]:
							print ("?ASASASSA")
							print(last_keywords[keyword_index-1])
							if last_keywords[keyword_index-1] in EXTRA_TAB_KEYWORDS:
								additional_tab = KEYWORDS_TAB_MAP[last_keywords[keyword_index-1]] * TAB_SIZE * TAB_SIGN
						elif last_keywords[keyword_index-1] == TABLE_KEYWORD:
							if last_keywords[keyword_index-1] in EXTRA_TAB_KEYWORDS:
								additional_tab = last_tab
							elif last_keywords[keyword_index+1] in ['Given', 'When', 'Then', 'Examples:']:
								additional_tab = KEYWORDS_TAB_MAP['And'] * TAB_SIZE * TAB_SIGN
							elif last_keywords[keyword_index+1] == 'And':
								additional_tab = KEYWORDS_TAB_MAP['And'] * TAB_SIZE * TAB_SIGN
							else:
								additional_tab = last_tab
						else:
							additional_tab = last_tab

					extra_blank_lines = ""

					if keywords[keyword_index-1] == COMMENT_KEYWORD \
					and keywords[keyword_index-2] == TAG_KEYWORD:
						extra_blank_lines = "".join([BLANK_LINE, BLANK_LINE])
					elif keywords[keyword_index] in DOUBLE_EXTRA_BLANK_LINES_KEYWORDS \
					and keywords[keyword_index-1] != COMMENT_KEYWORD:
						extra_blank_lines = "".join([BLANK_LINE, BLANK_LINE])
					elif keywords[keyword_index-1] == TAG_KEYWORD \
					and keywords[keyword_index] != COMMENT_KEYWORD:
						extra_blank_lines = "".join([BLANK_LINE, BLANK_LINE])
					elif keyword_index-1 < len(keywords) and keywords[keyword_index-1] == EXTRA_BLANK_LINE_KEYWORD:
						extra_blank_lines = BLANK_LINE

					file_content += "".join([additional_tab, " ".join(line_words), BLANK_LINE, extra_blank_lines])
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
						else:
							additional_tab = last_tab


						if table_row == "":
							table_row = "".join([table_row, TABLE_KEYWORD, TAB_DISTANCE_SIGN, word_in_row,
												TAB_SIGN * distance])
						else:
							table_row = "".join([table_row, TAB_DISTANCE_SIGN, TABLE_KEYWORD, TAB_DISTANCE_SIGN,
												 word_in_row, TAB_SIGN * distance])
					table_row = "".join([additional_tab, table_row, TAB_DISTANCE_SIGN, TABLE_KEYWORD])
					file_content += "".join([table_row, BLANK_LINE])


					if last_keywords[keyword_index-1] == TAG_KEYWORD:
						file_content += "".join([BLANK_LINE, BLANK_LINE])
					elif keywords[keyword_index-1] == COMMENT_KEYWORD and keywords[keyword_index-2] in [BLANK_LINE, TAG_KEYWORD]:
						file_content += "".join([BLANK_LINE, BLANK_LINE])
			else:
				additional_tab = last_tab			
		return file_content, last_line, keywords, tables_count, tables, additional_tab


	def prettify(self, file_content):

		if file_content[len(file_content)-1] != "\n":
			file_content.append("\n")
		prettify_file_content, last_line, keywords, tables_count, tables, additional_tab = \
			self._formatter(file_content, [], "", {}, tables_lines_numbers=list(), tables_count=0, tables=None, empty_lines_list=list())
		return prettify_file_content


class GherkinPrettifyCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		all_content = sublime.Region(0, self.view.size())

		prettify_file_content = GherkinPrettify().prettify(self.view.substr(all_content).split("\n"))

		self.view.replace(edit, all_content, prettify_file_content)
		print("FILE PRETTIFIED.")
