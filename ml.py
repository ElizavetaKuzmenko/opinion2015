# coding: utf-8
__author__ = 'liza'

import os
from xml.etree import ElementTree as et
from crude_tagger import replace_newlines, tokenize
from sklearn.svm import LinearSVC
clf1 = LinearSVC()
#from sklearn.linear_model import LogisticRegression
#clf2 = LogisticRegression()
#from sklearn.linear_model import SGDClassifier
#clf3 = SGDClassifier()
#from sklearn.neighbors import NeighborsClassifier

# TODO: baseline!! To compare
# from sklearn.naive_bayes import GaussianNB

# directory with files
DIRNAME = u'/home/liza/Документы/data/opinion_2015/rssnewx_0811'

# table with features for gold standard
TABLE = 'table_template.csv'

# token markers
END_OF_FILE = ' EOF '
END_OF_PARAGRAPH = ' EOP '
END_OF_SENTENCE = 'EOS'

# token categories
OPEN = 1
CLOSE = 2
OTHER = 0

features = []
labels = []

# Parsing the table
with open(TABLE) as t:
    for line in t[1:]:
        data = line.strip().split('\t')
        labels.append(data[2])
        # TODO: cut the feature with quotes to avoid over-training
        features.append(data[3:])

# fitting the classifier to our goldset data
clf1.fit(features, labels)

#dir_path = os.path.join(os.getcwd(), DIRNAME)
# iterate through data folder
for filename in os.listdir(DIRNAME):
    if filename.endswith('.xml'):
        # open file
        new_file = open(os.path.join(DIRNAME, filename[:-4] + '_parsed.txt'))
        with open(os.path.join('analyzed', filename)) as f:

            # get content
            contents = et.fromstring(f.read())
            text = END_OF_FILE.join([replace_newlines(node.text) for node in contents.findall('.//text')])

            # tokenize text
            tokenized_text = tokenize(text)

            for token in tokenized_text:
                # Короче к этому моменту надо как-то заполучить фичи для токена и скормить их машинке
                # TODO: here I need to incorporate a function that makes features for the token!!
                token_features = some_function(token)
                category = clf1.predict(token_features)
                if category == OPEN:
                    new_file.write('<UYUYGU>' + token + ' ')
                elif category == CLOSE:
                    new_file.write(token + '</UYUYGU> ')
                else:
                    new_file.write(token + ' ')
        new_file.close()