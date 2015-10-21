# coding: utf-8
__author__ = 'Sereni'
"""
A module that creates gold standard by crudely marking direct speech borders
"""
import os
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from xml.etree import ElementTree as et

# output text as marked up for Tomita?
MARKUP = True
MARKUP_PATH = os.path.join(os.getcwd(), 'markup')

# directory with files
DIRNAME = 'golden'
VERB_PATH = 'verbs_with_tenses.txt'
PARENTH_PATH = 'parenthesis.txt'

# token markers
END_OF_FILE = ' EOF '
END_OF_PARAGRAPH = ' EOP '
END_OF_SENTENCE = 'EOS'

# token categories
OPEN = 1
CLOSE = 2
OTHER = 0

# how many words allowed inside the quotes? I've seen 4-word names, so suppose 5
FRAGMENT_LENGTH = 5

NEWLINE = re.compile('(\n|\r)+')
QUOTES = {'"', "&quot", "&laquo", "&raquo", '``', "''"}
VERBS = set([])

PUNCT = {',', '.', ':', ';', '!', '?', '"', ')'}


def markup_text(token_array, name):
    """
    Join tokens to form a text, and insert appropriate tags for found opinions
    """
    with open(os.path.join(MARKUP_PATH, name), 'w') as marked_file:
        for word, tag in token_array:
            if word in QUOTES:
                word = '"'
                if word == '``':
                    word = ' '+word
            if tag == OPEN:
                word = "^ " + word
            elif tag == CLOSE:
                word += " ~"

            if word == END_OF_PARAGRAPH.strip() or word == END_OF_FILE.strip() or word == END_OF_SENTENCE:
                continue

            if word not in PUNCT:
                word = ' ' + word
            marked_file.write(word)


def load_verbs():
    """
    Loads verbs from the file specified in VERB_PATH
    Loads parentheses as well. For the purpose of dumb search we don't tell the difference
    In parentheses, neglects "по" so I don't have to concatenate tokens
    """
    global VERBS
    VERBS = set(open(os.path.join(os.getcwd(), VERB_PATH), 'r').read().split('\n'))
    VERBS.update(
        set([word.split()[1] for word in open(os.path.join(os.getcwd(), PARENTH_PATH), 'r').read().split('\n')]))


def categorize_direct(tokens):
    """
    :param tokens: a list of tokens
    :return a list of (token, category) tuples
    """
    categorized_tokens = []

    open_pointer = None
    close_pointer = None
    for i in range(len(tokens)):

        # if a quotechar, set pointers
        if tokens[i] in QUOTES:
            if open_pointer:
                # close pointers, set categories
                close_pointer = i

                # if a fragment is long enough, reassign categories to adjacent tokens
                if close_pointer - open_pointer > FRAGMENT_LENGTH:
                    categorized_tokens[open_pointer + 1] = (categorized_tokens[open_pointer + 1][0], OPEN)
                    categorized_tokens[close_pointer - 1] = (categorized_tokens[close_pointer - 1][0], CLOSE)

                open_pointer = None
                close_pointer = None

            else:
                open_pointer = i

        elif tokens[i] == END_OF_FILE.strip() or tokens[i] == END_OF_PARAGRAPH.strip():  # and, like, what next?
            open_pointer = None
            close_pointer = None

        categorized_tokens.append((tokens[i], OTHER))

    return categorized_tokens


def find_comma(array, start=0):
    """
    Finds a comma in a given list of tokens. Returns index or None.
    If index found, convert relative to absolute by adding to start index.
    Used to see if we hadn't missed a comma while not looking, and suddenly deciding to look again.
    """
    for i in range(len(array)):
        if array[i][0] == ',':
            return i + start
    return None


def mark_fragment(array, start, end):
    if end-start > FRAGMENT_LENGTH:
        array[start] = (array[start][0], OPEN)
        array[end] = (array[end][0], CLOSE)


def categorize_indirect(tokens):
    categorized = []

    # define markers
    last_comma = None
    inside_speech = False
    looking_for_next_comma = False
    last_EOS = -1
    in_quotes = False

    for i in range(len(tokens)):

        current_token = tokens[i][0]  # for debugging
        categorized.append(tokens[i])  # transfer token unchanged first

        if not in_quotes:

            # если вижу, что началась прямая речь, я сбрасываю все пойнтеры и жду, пока она кончится
            if tokens[i][1] == OPEN:
                last_comma = None
                inside_speech = False
                looking_for_next_comma = False
                in_quotes = True  # todo what about last EOS?

            # если вижу запятую и мне нужны запятые, отмечаю запятую
            elif current_token == ',' and not inside_speech:
                last_comma = i

                # если я искала следующую запятую, я говорю, что больше не ищу её, и больше не ищу запятые
                if looking_for_next_comma:
                    inside_speech = True
                    looking_for_next_comma = False

            # если вижу конец предложения, записываю его
            elif current_token == END_OF_SENTENCE:
                last_EOS = i

            # если вижу конец параграфа / файла
            elif current_token == END_OF_FILE.strip() or current_token == END_OF_PARAGRAPH.strip():

                # если я искала, отмечаю свой фрагмент
                if inside_speech:
                    mark_fragment(categorized, last_comma+1, i-3)

                # в любом случае сбрасываю все пойнтеры
                last_comma = None
                inside_speech = False
                looking_for_next_comma = False
                last_EOS = i

            # если вижу глагол, то депендс
            elif current_token in VERBS:

                # если мне нужны запятые в это время
                if not inside_speech:

                    # если я видела запятую в этом предложении, делаю фрагмент от начала предложения до запятой и сбрасываю пойнтеры
                    if last_comma and last_EOS < last_comma:
                        mark_fragment(categorized, last_EOS+1, last_comma-1)
                        last_comma = None
                        looking_for_next_comma = False

                    # если я видела запятую в предыдущем предложении, то я ищу следующую запятую.
                    elif last_comma and last_EOS > last_comma:
                        looking_for_next_comma = True

                    # если я не видела запятую, я ищу следующую запятую.
                    elif not last_comma:
                        looking_for_next_comma = True  # I know it's redundant as hell, but readable's better

                # если мне не нужны запятые в это время, значит, произошла ошибка
                else:
                    # от последней запятой до последнего конца предложения я делаю фрагмент
                    mark_fragment(categorized, last_comma+1, last_EOS-2)

                    # от последнего конца предложения до глагола я ищу запятую
                    last_comma = find_comma(categorized[last_EOS:i], last_EOS)

                    if last_comma:
                        # если нашлась запятая, то делаю ещё фрагмент от начала предложения до этой запятой
                        mark_fragment(categorized, last_EOS+1, last_comma-1)
                        last_comma = None
                    # если не нашлась, то ищу следующую запятую.
                    else:
                        looking_for_next_comma = True

                    inside_speech = False
                    last_comma = None

        else:  # look if it's time to close the quotes and keep searching
            if tokens[i][1] == 2:
                in_quotes = False

    return categorized


def replace_newlines(string):
    """
    Merge newlines and replace with END_OF_PARAGRAPH marker
    :type string: str
    :type return: str
    """
    return re.sub(NEWLINE, END_OF_PARAGRAPH, string)


def tokenize(string):
    """
    Tokenize a string into sentences and tokens
    Returns a list of tokens with an extra END_OF_SENTENCE token at the end of each sentence
    """
    tokenized = [word_tokenize(word) for word in sent_tokenize(string)]
    flattened = []  # flatten sentences into a stream of tokens
    for sentence in tokenized:
        sentence.append(END_OF_SENTENCE)
        flattened += sentence
    return flattened


if __name__ == '__main__':

    dir_path = os.path.join(os.getcwd(), DIRNAME)
    output = open('categories.csv', 'w')
    load_verbs()
    # iterate through data folder
    for filename in os.listdir(dir_path):
        if filename.endswith('xml'):

            # open file
            with open(os.path.join(dir_path, filename)) as f:

                # get content
                contents = et.fromstring(f.read().replace('«', '"').replace('»', '"'))
                text = END_OF_FILE.join([replace_newlines(node.text) for node in contents.findall('.//text')])

                # tokenize text
                tokenized_text = tokenize(text)

                # categorize_direct tokens
                tokens = categorize_direct(tokenized_text)
                categorized = categorize_indirect(tokens)

                # write output
                if MARKUP:
                    if not os.path.exists(MARKUP_PATH):
                        os.makedirs(MARKUP_PATH)
                    markup_text(categorized, name=filename)

                for (token, category) in categorized:
                    output.write('%s\t%s\t%s\n' % (filename, token, category))

    output.close()