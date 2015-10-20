# coding: utf-8
__author__ = 'liza'

import os, re
from xml.etree import ElementTree as et
from create_features import features
from sklearn.svm import LinearSVC
#from sklearn.linear_model import LogisticRegression
#clf2 = LogisticRegression()
#from sklearn.linear_model import SGDClassifier
#clf3 = SGDClassifier()
#from sklearn.neighbors import NeighborsClassifier

# TODO: baseline!! To compare
# from sklearn.naive_bayes import GaussianNB

# directory with files
#DIRNAME = u'/home/liza/Документы/data/opinion_2015/rssnewx_0811'
DIRNAME = u'/home/liza/Документы/data/opinion_2015/news_test'

# table with features for gold standard
TABLE = 'features.csv'

# token markers
END_OF_FILE = ' EOF '
END_OF_PARAGRAPH = ' EOP '
END_OF_SENTENCE = 'EOS'

# token categories
OPEN = 1
CLOSE = 2
OTHER = 0

NEWLINE = re.compile('(\n|\r)+')

def replace_newlines(string):
    """
    Merge newlines and replace with END_OF_PARAGRAPH marker
    :type string: str
    :type return: str
    """
    return re.sub(NEWLINE, END_OF_PARAGRAPH, string)

# Parsing the table
def parse_gold(TABLE):
    features_gold = []
    labels = []
    with open(TABLE) as t:
        for line in t[1:]:
            data = line.strip().split('\t')
            labels.append(data[2])
            # TODO: cut the feature with quotes to avoid over-training
            features_gold.append(data[3:])
    return features_gold, labels


clf1 = LinearSVC()
# fitting the classifier to our goldset data
features_gold, labels = parse_gold(TABLE)
clf1.fit(features_gold, labels)

#dir_path = os.path.join(os.getcwd(), DIRNAME)
# iterate through data folder
for filename in os.listdir(DIRNAME):
    if filename.endswith('.xml'):
        print(filename)
        # open file
        new_file = open(os.path.join(DIRNAME, filename[:-4] + '_parsed.txt'))
        with open(os.path.join('analyzed', filename)) as f:

            # get content
            contents = et.fromstring(f.read())
            text = END_OF_FILE.join([replace_newlines(node.text) for node in contents.findall('.//text')])

            # tokenize text
            data = features(text)

            for token in data:
                token_features = data.split('\t')[2:]
                category = clf1.predict(token_features)
                if category == OPEN:
                    new_file.write('<UYUYGU>' + token + ' ')
                elif category == CLOSE:
                    new_file.write(token + '</UYUYGU> ')
                else:
                    new_file.write(token + ' ')
        new_file.close()