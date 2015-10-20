# coding: utf-8
__author__ = 'Sereni'
"""
A module that creates gold standard by crudely marking direct speech borders
"""
import os
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from xml.etree import ElementTree as et

# directory with files
DIRNAME = 'sample'
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


def load_verbs():
    """
    Loads verbs from the file specified in VERB_PATH
    Loads parentheses as well. For the purpose of dumb search we don't tell the difference
    In parentheses, neglects "по" so I don't have to concatenate tokens
    """
    global VERBS
    VERBS = set(open(os.path.join(os.getcwd(), VERB_PATH), 'r').read().split('\n'))
    VERBS.update(set([word.split()[1] for word in open(os.path.join(os.getcwd(), PARENTH_PATH), 'r').read().split('\n')]))


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
                    categorized_tokens[open_pointer+1] = (categorized_tokens[open_pointer+1][0], OPEN)
                    categorized_tokens[close_pointer-1] = (categorized_tokens[close_pointer-1][0], CLOSE)

                open_pointer = None
                close_pointer = None

            else:
                open_pointer = i

        elif tokens[i] == END_OF_FILE.strip() or tokens[i] == END_OF_PARAGRAPH.strip():  # and, like, what next?
            open_pointer = None
            close_pointer = None

        categorized_tokens.append((tokens[i], OTHER))

    return categorized_tokens


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
    # iterate through data folder
    for filename in os.listdir(dir_path):
        if filename.endswith('xml'):

            # open file
            with open(os.path.join(dir_path, filename)) as f:

                # get content
                contents = et.fromstring(f.read())
                text = END_OF_FILE.join([replace_newlines(node.text) for node in contents.findall('.//text')])

                # tokenize text
                tokenized_text = tokenize(text)

                # categorize_direct tokens
                categorized = categorize_direct(tokenized_text)

                # write output
                for (token, category) in categorized:
                    output.write('%s\t%s\t%s\n' % (filename, token, category))

    output.close()