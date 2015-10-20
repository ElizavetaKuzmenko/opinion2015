__author__ = 'elmira'

import os
import re
import pymorphy2
from crude_tagger import tokenize, replace_newlines, categorize
from xml.etree import ElementTree as et

# morphological parser
morph = pymorphy2.MorphAnalyzer()

# directory with files
DIRNAME = 'data_short'

# token markers
END_OF_FILE = ' EOF '
END_OF_PARAGRAPH = ' EOP '
END_OF_SENTENCE = 'EOS'

# token categories
OPEN = 1
CLOSE = 2
OTHER = 0

FRAGMENT_LENGTH = 5

NEWLINE = re.compile('(\n|\r)+')
QUOTES = {'"', "&quot", "&laquo", "&raquo", '``', "''"}
SPEECH_VERBS = []
with open('verbs_with_tenses.txt', 'r', encoding='utf-8') as verbs:
    SPEECH_VERBS += [i.strip() for i in verbs.readlines()]

SPEECH_PUNCT = []
with open('speech_punct.txt', 'r', encoding='utf-8') as verbs:
    SPEECH_PUNCT += [i.strip() for i in verbs.readlines()]


class Token(object):
    def __init__(self, token):
        self.token = token
        self.category = '0'
        self.next_token_is_end_of_para = '0'
        self.next_token_is_end_of_text = '0'
        self.begins_with_a_capital_letter = self.is_capital(token)
        self.pos_prev1 = '-'
        self.pos_prev2 = '-'
        self.pos_prev3 = '-'
        self.pos = self.part_of_speech()
        self.pos_next1 = '-'
        self.pos_next2 = '-'
        self.pos_next3 = '-'
        self.nearest_left_quote = 888
        self.nearest_right_quote = 888
        self.is_speech_word = False
        self.speech_word = '0'
        self.speech_punct = '0'

    def is_capital(self, token):
        if token == END_OF_FILE.strip() or token == END_OF_PARAGRAPH.strip():
            return '0'
        if token[0].isupper():
            return '1'
        return '0'

    def part_of_speech(self):
        if self.token == END_OF_FILE.strip() or self.token == END_OF_PARAGRAPH.strip():
            return '-'
        pos = morph.parse(self.token)[0].tag.POS
        if pos:
            return pos
        return 'UNK'

    def __str__(self):
        return '\t'.join([self.token, self.category, self.next_token_is_end_of_para,
                          self.next_token_is_end_of_text, self.begins_with_a_capital_letter,
                          self.pos_prev1, self.pos_prev2, self.pos_prev3,
                          self.pos, self.pos_next1, self.pos_next2, self.pos_next3,
                          str(self.nearest_left_quote), str(self.nearest_right_quote),
                          self.speech_word, self.speech_punct])


def analyze(tokens):
    analyzed_tokens = []
    for i in range(len(tokens)):
        current_token = Token(tokens[i])
        if current_token.token in QUOTES:
            # print(current_token.token)
            if i != 0 and analyzed_tokens[i-1].nearest_left_quote != 888:
                for counter in range(1, analyzed_tokens[i-1].nearest_left_quote + 1):
                    analyzed_tokens[i-counter].nearest_right_quote = counter
            current_token.nearest_left_quote = 0
            current_token.nearest_right_quote = 0

        if i > 0:
            if current_token.token not in QUOTES:
                if analyzed_tokens[i-1].nearest_left_quote != 888:
                    current_token.nearest_left_quote = analyzed_tokens[i-1].nearest_left_quote + 1
                    current_token.nearest_right_quote = 888
            analyzed_tokens[i-1].pos_next1 = current_token.pos
            current_token.pos_prev1 = analyzed_tokens[i-1].pos
            if current_token.token == END_OF_FILE.strip():
                analyzed_tokens[i-1].next_token_is_end_of_text = '1'
                current_token.nearest_left_quote = 888
                current_token.nearest_right_quote = 888
            if current_token.token == END_OF_PARAGRAPH.strip():
                analyzed_tokens[i-1].next_token_is_end_of_para = '1'
            if current_token.token in SPEECH_VERBS:
                current_token.is_speech_word = True
            if analyzed_tokens[i-1].is_speech_word:
                current_token.speech_word = '1'
        if i > 1:
            analyzed_tokens[i-2].pos_next2 = current_token.pos
            current_token.pos_prev2 = analyzed_tokens[i-2].pos
            if analyzed_tokens[i-2].is_speech_word:
                current_token.speech_word = '1'
        if i > 2:
            analyzed_tokens[i-3].pos_next3 = current_token.pos
            current_token.pos_prev3 = analyzed_tokens[i-3].pos
            if analyzed_tokens[i-3].is_speech_word:
                current_token.speech_word = '1'
        if i > 3:
            if analyzed_tokens[i-4].is_speech_word:
                current_token.speech_word = '1'
        if i > 4:
            if analyzed_tokens[i-5].is_speech_word:
                current_token.speech_word = '1'
        analyzed_tokens.append(current_token)
    return analyzed_tokens


def features(DIRNAME):
    dir_path = os.path.join(os.getcwd(), DIRNAME)
    output = open('features.csv', 'w', encoding='utf-8')

    # iterate through data folder
    for filename in sorted(os.listdir(dir_path)):
        if filename.endswith('xml'):
            print(filename)

            # open file
            with open(os.path.join(dir_path, filename), encoding='utf-8') as f:

                # get content
                contents = et.fromstring(f.read())
                text = END_OF_FILE.join([replace_newlines(node.text) for node in contents.findall('.//text')])

                # tokenize text
                tokenized_text = tokenize(text)

                # analyze tokens
                analyzed = analyze(tokenized_text)

                # categorize tokens
                categorized = categorize(tokenized_text)

                # write output
                for token, category_tuple in zip(analyzed, categorized):
                    token.category = str(category_tuple[1])
                    output.write('%s\t%s\n' % (filename, str(token)))

    output.close()