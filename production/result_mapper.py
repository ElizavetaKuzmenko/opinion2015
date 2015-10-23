__author__ = 'Sereni'
import re
import os


def fill_gaps(t):
    # if there's no author from one ~ to another ^, insert a dummy somewhere
    output = ''
    searching = False
    for i in range(len(t)):

        output += t[i]

        if t[i] == '~':
            searching = True
        elif t[i] == '{':
            searching = False
        elif t[i] == "^" and searching:
            searching = False
            output += 'Author {Name = котик} '

    return output


def main():
    factfile = open('facts.txt', 'r')

    if not os.path.exists('result'):
        os.makedirs(os.path.join(os.getcwd(), 'result'))

    # get first filename
    filename = os.path.basename(sorted(os.listdir('markup'))[0])
    output = open('result/'+filename, 'w')
    speechfile = open('markup/'+filename, 'r')

    author_pattern = re.compile('Name = (\w+)')
    speech_pattern = re.compile('\^(.+?)~')

    text = ''
    first = True

    for line in factfile:

        if first:
            first = False
            continue

        # new file
        if line.startswith('\\'):

            # process what we've got
            text = fill_gaps(text)

            authors = re.findall(author_pattern, text)
            phrases = re.findall(speech_pattern, speechfile.read())

            for author, phrase in zip(authors, phrases):
                output.write('%s\t%s\n' % (author, phrase.strip('^" ~')))

            text = ''

            # open new files
            filename = line.strip('\\').strip()
            output.close()
            output = open('result/'+filename, 'w')
            speechfile.close()
            speechfile = open('markup/'+filename, 'r')

        text += line

    text = fill_gaps(text)
    authors = re.findall(author_pattern, text)
    phrases = re.findall(speech_pattern, speechfile.read())

    for author, phrase in zip(authors, phrases):
        output.write('%s\t%s\n' % (author, phrase.strip('^" ~')))
    speechfile.close()
    output.close()