#!/bin/python
# coding: utf-8

import sys,codecs,os

def extractor(text):
    results = []
    speech = []
    author = []
    state = 'None'
    for line in text:
	if line.strip().endswith('Fz 1'):
	    continue
	res = line.strip().split()
	if len(res) == 4:
	    (token,lemma,tagset,prob) = res
	else:
	    print 'Error!'
	    print line,len(res)
	    break
	#print token.encode('utf-8'),state.encode('utf-8')
	if state == 'speech' and tagset != 'Frc' and tagset != 'Fe':
	    speech.append(token)
	if state == 'afterspeech' or state == 'author':
	    if tagset.startswith('NC') and token.istitle():
		state = "author"
		author.append(token)
	if state == 'author' and not token.istitle():
	    state = 'None'
	    if len(speech) > 3:
		author = ' '.join(author)
		results.append((author,' '.join(speech).replace(' , ',', ').replace(' . ','. ')))
	    speech = []
	    author = []
	if tagset == 'Fra':
	    speech = []
	    state = 'speech'
	if tagset == 'Frc':
	    state = 'afterspeech'
	if tagset == 'Fe':
	    if state == 'speech':
		state = 'afterspeech'
	    else:
		speech = []
		state = 'speech'
	if tagset == 'Fp' and state != 'speech':
	    state = 'None'
	    speech = []
	    author = []
    return results

files2check = [f for f in os.listdir('.') if f.endswith('parsed')]

for f in files2check:
    print f
    text = codecs.open(f,'r','utf-8').readlines()
    output = codecs.open('speech/'+f,'w','utf-8')
    for pair in extractor(text):
	output.write(pair[0]+'\t'+pair[1]+'\n')
    output.close()