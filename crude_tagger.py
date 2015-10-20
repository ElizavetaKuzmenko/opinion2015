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


def find_comma(array):
    """
    Finds a comma in a given list of tokens. Returns index or None.
    Used to see if we hadn't missed a comma while not looking, and suddenly deciding to look again.
    """
    for i in range(len(array)):
        if array[i][0] == ',':
            return i
    return None

def categorize_indirect(tokens):

    categorized = []

    mark_commas = True  # set if in search for the next phrase; false if searching for limits of current phrase
    seen_comma = None  # None or an index of the last good comma (ask me for definition of good)
    last_EOS = -1  # marks last seen end of sentence marker
    in_quotes = False
    searching_for_next_comma = False  # when found a verb and only need the next comma

    for i in range(len(tokens)):

        current_token = tokens[i]  # for debugging
        categorized.append(tokens[i])  # transfer token unchanged first

        if not in_quotes:

            if tokens[i][0] == ',' and mark_commas:

                if searching_for_next_comma:

                    searching_for_next_comma = False
                    mark_commas = False  # from here on, look for exit markers and do not remember any commas

                seen_comma = i

            elif tokens[i][0] == END_OF_SENTENCE:
                last_EOS = i

            elif tokens[i][1] == 1:
                in_quotes = True  # if we got inside direct speech, don't do anything until it's over

                # we've been searching for an end of speech and stumbled into direct speech
                # means we've gone too far, and let's chop it off at the previous sentence
                if not mark_commas:
                    categorized[seen_comma+1] = (categorized[seen_comma+1][0], OPEN)  # start
                    categorized[last_EOS-1] = (categorized[last_EOS-1][0], CLOSE)  # end
                    mark_commas = True
                    seen_comma = find_comma(tokens[last_EOS: i])

                else:
                    seen_comma = None

            elif tokens[i][0] in VERBS:

                current_verb = (tokens[i], i)  # for debugging

                if seen_comma:

                    if not mark_commas:  # found a verb when looking for speech end; chop speech off at last EOS
                        categorized[seen_comma+1] = (categorized[seen_comma+1][0], OPEN)  # start
                        categorized[last_EOS-1] = (categorized[last_EOS-1][0], CLOSE)  # end
                        mark_commas = True
                        seen_comma = find_comma(tokens[last_EOS: i])

                    # an actual good match, define phrase
                    else:
                        # find limits and set them to start and end
                        categorized[last_EOS+1] = (categorized[last_EOS+1][0], OPEN)  # start
                        categorized[seen_comma-1] = (categorized[seen_comma-1][0], CLOSE)  # end
                        seen_comma = None

                else:
                    searching_for_next_comma = True  # set a marker to let the next comma know it's the last

            # exit markers

            elif tokens[i][0] == END_OF_PARAGRAPH.strip() or tokens[i][0] == END_OF_FILE.strip():

                if seen_comma:
                    categorized[seen_comma+1] = (categorized[seen_comma+1][0], OPEN)
                    categorized[i] = (categorized[i-2][0], CLOSE)  # -2 because before EOF/EOP there's normally an EOS
                    seen_comma = None
                    mark_commas = True

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
                contents = et.fromstring(f.read())
                text = END_OF_FILE.join([replace_newlines(node.text) for node in contents.findall('.//text')])

                # tokenize text
                tokenized_text = tokenize(text)

                # categorize_direct tokens
                tokens = categorize_direct(tokenized_text)
                categorized = categorize_indirect(tokens)

                # write output
                for (token, category) in categorized:
                    output.write('%s\t%s\t%s\n' % (filename, token, category))

    output.close()