__author__ = 'Sereni'
import subprocess
import os

import crude_tagger
import result_mapper

PATH_TO_TOMITA = os.path.join('.', os.getcwd(), 'tomita-parser')

# call opinion tagger
crude_tagger.main()

# create fact file
open('facts.txt', 'w').close()
subprocess.call([PATH_TO_TOMITA, 'config.proto'])
result_mapper.main()

# clean fact file for the next launch
os.remove(os.path.join(os.getcwd(), 'facts.txt'))