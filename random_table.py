# coding: utf-8
__author__ = 'liza'

import codecs, random

# token categories
OPEN = 1
CLOSE = 2
OTHER = 0

instances = 1000
i = 1

filename = 'some_file.xml'
categories = [OPEN, CLOSE, OTHER]
table = codecs.open('table_template.csv', 'a', 'utf-8')
token = 'token'
POS = ['N', 'V', 'A', 'P', 'D', 'R']

while i < instances:
    value_list = [filename, token + str(i), random.choice(categories), random.choice(['0', '1']), random.choice(['0', '1']),
                  random.choice(['0', '1']), random.choice(POS), random.choice(POS), random.choice(POS), random.choice(POS),
                  random.choice(POS), random.choice(POS), random.choice(POS), str(random.randint(0, 27)),
                  str(random.randint(0, 27)), random.choice(['0', '1']), random.choice(['0', '1'])]
    line = '\t'.join(str(v) for v in value_list) + '\n'
    table.write(line)
    i += 1

table.close()