__author__ = 'Sereni'
import re


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
            output += 'Author {Name = кто-то} '

    return output


factfile = open('facts.txt', 'r')

filename = '1big_ru_DF07BDC7_0811T031348.xml'
output = open('result/'+filename, 'w')
speechfile = open('markup/'+filename, 'r')

author_pattern = re.compile('Name = (\w+)')
speech_pattern = re.compile('\^(.+?)~')

text = ''

for line in factfile:

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