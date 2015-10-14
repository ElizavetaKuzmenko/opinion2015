#!/usr/bin/python
# coding: utf-8

import os, codecs, re, random


def parse_phrase(regexp, text, keys):
    output = u''
    results = re.finditer(regexp.format(**keys), text, flags=re.IGNORECASE)
    for res in results:
        src = res.group('src')
        info = res.group('info')

        output += u'{}\t{}\n\n'.format(src, info)
    return output


def parse_text(text):
    output = u''
    keys = {'verb': ur'((сообщил|(от|за)метил|(рас|вы)?сказал|написал|добавил|поведал|передал|признал|выразил|высказывал|(про)?комментировал|обратил|(за|объ)явил)[аи]?|(сообща[ею]т|(от|за)меча[ею]т|говор[ия]т|пиш[еу]т|выража[ею]т|(вы|рас)сказыва[ею]т|(про)?комментиру[ею]т|обраща[ею]т|переда[еёю]т|заявля[ею]т))(ся)?( (нам|журналистам|людям|народу))?( в( сво[её][йм])? (интервью|книге|статье))?',
            'sent_start': ur'(\r?\n|\. |, )',
            'src': ur'(в )?(?P<src>[^,]+?)',
            'info': ur'(?P<info>[«“\"].+[»”\"]?|.+?)',
           }

    output += parse_phrase(ur'{sent_start}{info}, ?[–—\-]? {verb} {src}\.\r?\n', text, keys)
    output += parse_phrase(ur'{sent_start}как {verb} (в )?{src}, {info}\.', text, keys)
    output += parse_phrase(ur'{sent_start}по (мнению|словам) {src}, {info}\.', text, keys)
    output += parse_phrase(ur', в которо[мй] {src} {verb}(:|, что) {info}\.', text, keys)
    output += parse_phrase(ur'{sent_start}{src} {verb}(:|, что) {info}\.', text, keys)
    return output.strip()


if not os.path.exists('results'):
    os.mkdir('results')

files = os.listdir('news_txt')
files = [f for f in files if f.endswith('.txt')]
parsed = []

#while len(parsed) <= 30000:
for ff in files:
#    filename = random.choice(files)
    filename = ff
#    if filename in parsed:
#        continue
    print "Parsing {} (#{})".format(filename, len(parsed)+1)
    
    parsed.append(filename)
    full_filename = os.path.join('news_txt', filename)
    f = codecs.open(full_filename, 'r', 'utf-8')
    text = f.read()
    f.close()

    result = parse_text(text)
    f = codecs.open(os.path.join('results', '{}_results.txt'.format(filename.split('.')[0])), 'w', 'utf-8')
    f.write(result)
    f.close()
