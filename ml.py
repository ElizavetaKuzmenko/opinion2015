# coding: utf-8
__author__ = 'liza'

import os, re, sys
from xml.etree import ElementTree as et
from create_features import features
from sklearn.svm import LinearSVC
#from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction import DictVectorizer
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

# preprocessing for categorical features -- POS
#enc = OneHotEncoder()
vec = DictVectorizer()
categorical_integers = {'NOUN': 0, 'ADJF': 1, 'ADJS': 2, 'COMP': 3, 'VERB': 4, 'INFN': 5, 'PRTF': 6, 'PRTS': 7, 'GRND': 8,
                        'NUMR': 9, 'ADVB': 10, 'NPRO': 11, 'PRED': 12, 'PREP': 13, 'CONJ': 14, 'PRCL': 15, 'INTJ': 16, 'UNK': 17}

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
    #categorical = []
    with open(TABLE) as t:
        for line in t:
            if '-' in line:
                continue
            data = line.strip().split('\t')
            labels.append(data[2])
            feature_vec = {}
            for i in range(len(data[3:])):
                feature_vec[i] = data[i]
            # TODO: cut the feature with quotes to avoid over-training
            #categorical_features = [categorical_integers[x] for x in data[6:13]]
            #categorical.append(categorical_features)
            #features_gold.append(data[3:6] + categorical_features + data[13:])
            features_gold.append(feature_vec)
    #enc.fit(categorical)
    #print(enc.transform([[13, 5, 4, 0, 0, 17, 17]]).toarray())
    #for i in range(len(features_gold)):
    #    features_gold[i] = [int(x) for x in features_gold[i][:3]] + enc.transform([features_gold[i][3:10]]) + [int(x) for x in features_gold[i][10:]]
    features_gold = vec.fit_transform(features_gold)
    return features_gold, labels

sys.stdout.write('Training classifier...')
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
        new_file = open(os.path.join('analyzed', filename[:-4] + '_parsed.txt'), 'w')
        with open(os.path.join(DIRNAME, filename)) as f:

            # get content
            contents = et.fromstring(f.read())
            text = END_OF_FILE.join([replace_newlines(node.text) for node in contents.findall('.//text')])

            # tokenize text
            data = features(text)

            for token in data:
                token_features = token.split('\t')[2:]
                token_vec = {}
                for i in range(len(token_features)):
                    token_vec[i] = token_features[i]
                token_features = vec.fit_transform(token_vec)
                #categorical_features = [categorical_integers[x] for x in token_features[6:13]]
                #token_features = [int(x) for x in token_features[:3]] + enc.transform([categorical_features]) + [int(x) for x in token_features[10:]]

                category = clf1.predict(token_features)
                if category == OPEN:
                    new_file.write('<UYUYGU>' + token + ' ')
                elif category == CLOSE:
                    new_file.write(token + '</UYUYGU> ')
                else:
                    new_file.write(token + ' ')
        new_file.close()