#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, json, codecs, os, re
##f_out = codecs.open('f_out.txt','a', 'utf-8')
##verbs = [u'сказать',u'рассказать',u'добавить',u'заявить',u'цитировать', u'полагать', u'размещать']
files = os.listdir(os.path.dirname(os.path.abspath('prog_slide-0.py')))
for i in files:
    if os.path.splitext(i)[-1]==".json":
        f_in = codecs.open(i, 'r', 'utf-8')
        for line in f_in:
            line = re.sub(u'–', u'—', line)
            line = re.sub(u'-', u'—', line)
            line = re.sub(u'\n', u'', line)
            line = line / 2
            print line

            a = json.loads(line.strip())
            for h in xrange(len(a)):
                key = a[h]
                if key["text"] == u'\", — ' or key["text"] == u'\" — ' or key["text"] == u'», — ' or key["text"] == u'» — ':
                    text = ''
                    for j in xrange(h-1,-1,-1):
                        if a[j]["text"] == u'\"' or a[j]["text"] == u'«':
                            text = ''.join([k["text"] for k in a[j + 1 : h]])
                            break                             
                    for j in xrange(h + 1, len(a)):
                        cur_key = a[j]
                        if 'analysis' in cur_key and len(cur_key["analysis"]) > 0 and ('S,f,anim' in cur_key["analysis"][0]["gr"] or 'S,m,anim' in cur_key["analysis"][0]["gr"] or 'famn' in cur_key["analysis"][0]["gr"] or 'persn' in cur_key["analysis"][0]["gr"] or 'geo' in cur_key["analysis"][0]["gr"]):
                            person = cur_key["text"]
                            break
##                    print person + '\t' + text + '\n'
                    names = str(i).split('.txt.json')
                    for w in names:
                        with codecs.open(w + '_result.txt', 'a', 'utf-8') as f_out:
                            f_out.write(person + '\t' + text + '\n')
                    
                if key["text"] == u': \"' or key["text"] == u': «':
                    text = ''
                    for j in xrange(h-1, len(a)):
                        if a[j]["text"] == u'\"' or a[j]["text"] == u'»':
                            text = ''.join([k["text"] for k in a[h+1 : j]])
                            break
                    for j in xrange(h-1, -1,-1):
                        cur_key = a[j]
                        if 'analysis' in cur_key and len(cur_key["analysis"]) > 0 and ('S,f,anim' in cur_key["analysis"][0]["gr"] or 'S,m,anim' in cur_key["analysis"][0]["gr"] or 'famn' in cur_key["analysis"][0]["gr"] or 'persn' in cur_key["analysis"][0]["gr"] or 'geo' in cur_key["analysis"][0]["gr"]):
                            person = cur_key["text"]
                            break

                    names = str(i).split('.txt.json')
                    for w in names:
                        with codecs.open(w + '_result.txt', 'a', 'utf-8') as f_out:
                            f_out.write(person + '\t' + text + '\n')
                 
f_out.close()

           

