#coding:utf-8
import codecs, re, nltk, subprocess, json, time
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters

class Opinion:
    def __init__(self):
        self.result = []
        punkt_param = PunktParameters()
        punkt_param.abbrev_types = set(['г', 'гор', 'ул', 'кв', 'д', 'корп', 'эт', 'стр', 'пер', 'просп', 'тел', 'зам', 'каб', 'гос', 'мед'])
        self.sentence_splitter = PunktSentenceTokenizer(punkt_param)
        self.command = "./mystem -dig --eng-gr --format json < input.txt > mystem.json"
        self.verbs = [] #[u"отметил", u"сказал", u"подчеркнул", u"сообщил"]
        self.auxV_Author_reverse = [] #[u"[Пп]о .... словам", u"[Пп]о данным", u"[Пп]о сообщению", ]
        self.dividers = {}
        self.load_verbs()
        self.dividersF() #делаем разделители речи и автора
        self.dividersREG = []
        self.authID = 1
        self.mystem_authors = u""
        self.authors = {}
        self.start = time.clock()



    def reverse(self, sent):
        for i in self.auxV_Author_reverse:
            try:
                sent = re.sub(i + u"([^,]*?),", u"\\1 сказал, что", sent)
            except: pass

        #print sent
        return sent

    def dividersF(self):
        for i in self.verbs:
            i = i + u"а?"
            self.dividers[re.compile(u", ?[-–]? ?" + i)] = "left" #речь слева , - сказал
            self.dividers[re.compile(i + u", что ?")] = "right" #речь справа
            self.dividers[re.compile(i + u" ?[^»\"]?:(\n)?[-–] ")] = "right"
            self.dividers[re.compile(i + u": ?[«\"]")] = "right"
            self.dividers[re.compile(u"[»\"] ?– ?" + i)] = "left"



    def speech_refiner(self, speech):
        speech = speech.strip(u"\"«».")
        return speech

    def load_verbs(self, h = True):
        f = codecs.open(u"verbs.txt", "r", "utf-8")
        for line in f:
            if h:
                h = False
                continue
            self.verbs.append(line.strip())
        f.close()
        h = True
        f = codecs.open(u"auxV_A.txt", "r", "utf-8")
        for line in f:
            if h:
                h = False
                continue
            self.auxV_Author_reverse.append(u"[Пп]о (.{2,6} )?" + line.strip())
        f.close()

    def mystem(self, text=""):
        f = codecs.open("input.txt", "w", "utf-8")
        f.write(self.mystem_authors)
        p = subprocess.Popen("./run_mystem.sh", shell=True, stdout = subprocess.PIPE)
        f.close()
        stdout, stderr = p.communicate()

    def gs_numbers(self):
        f = codecs.open("nums.txt", "r", "utf-8")
        numbers = []
        for line in f:
            numbers.append(int(line.strip()))
        f.close()
        return numbers

    def refine_all_authors(self):

        id = 1
        f = codecs.open("mystem.json", "r", "utf-8")
        for line in f:
            author = u""
            persnfamn = u""
            prerelease = u""
            apro = u""
            someS = u""
            all_text = u""
            a = json.loads(line.strip())
            for key in a:
                ans = key["analysis"]
                try:
                    if (ans[0]["gr"][0][0] == u"S") and ((u"famn" in ans[0]["gr"][0][0]) or (u"persn" in ans[0]["gr"][0][0])):
                        persnfamn += key["text"] + u" "
                    if (ans[0]["gr"][0][0] == u"S") and (u"nom" in ans[0]["gr"]):
                        prerelease += key["text"] + u" "
                    if (ans[0]["gr"][0][0] == u"S"):
                        someS += key["text"] + u" "
                    if (u"APRO" in ans[0]["gr"][0][0]):
                        apro += key["text"] + u" "
                    all_text += key["text"] + u" "
                except: pass
            if author == u"": author = persnfamn
            if author == u"": author = prerelease
            if author == u"": author = someS
            if author == u"": author = apro
            if author == u"": author = all_text

            if author == u"":
                print line
                print id

            self.authors[id] = author.strip()
            id += 1


        f.close()

    def analyse_files(self):

        for i in range(0, 30000):
        #for i in self.gs_numbers():

            if i < 10000:
                i = u"0000" + str(i)
                i = i[-5:]
            self.analyse_file(u"news%s.txt" % str(i))


        self.make_results()

    def analyse_file(self, filename="news19059.txt"):

        print u"processing", filename
        f = codecs.open("news_txt/%s" % filename, "r", "utf-8") #news00000.txt
        text = f.read()
        f.close()

        sentences = self.sentence_splitter.tokenize(text)
        for s in sentences:
            s = self.reverse(s)
            for d in self.dividers:

                sSUB = d.sub(u"<%>", s)
                if "<%>" in sSUB:
                    sSUB = sSUB.split("<%>")
                    if self.dividers[d] == "left":
                        speech = self.speech_refiner(sSUB[0])
                        self.mystem_authors += u"%s\t%s\r\n" % (str(self.authID), sSUB[1].strip().replace("\n", " "))
                    else:
                        speech = self.speech_refiner(sSUB[1])
                        self.mystem_authors += u"%s\t%s\r\n" % (str(self.authID), sSUB[0].strip().replace("\n", " "))
                    self.result.append((filename, self.authID, speech))
                    self.authID += 1
        end = time.clock()
        print u"Прошло ", "%.1f" % (end-self.start), u"секунд"


    def make_results(self, filename=""):
        self.mystem()
        self.refine_all_authors()
        last_file = ""
        for i in range (len(self.result)):
            id = i+1
            result_entry = self.result[i]
            print result_entry[0][:-4] + u"_results.txt"
            if result_entry[0] != last_file:
                try: f.close()
                except: pass
                f = codecs.open(u"group_1/%s_results.txt" % (result_entry[0][:-4]), "w", "utf-8")
                last_file = result_entry[0]
            #print result_entry[0], id, self.authors[id], "++++" , result_entry[2]
            f.write(u"%s\t%s\r\n" % (self.authors[id], result_entry[2]))

        self.make_empty() #добавляем пустые файлы

    def make_empty(self):
        for i in range (0, 30000):
            if i < 10000:
                i = u"0000" + str(i)
                i = i[-5:]
            try:
                f = codecs.open(u"group_1/news%s_results.txt" % str(i), "r", "utf-8")
                f.close()
            except:
                f = codecs.open(u"group_1/news%s_results.txt" % str(i), "w", "utf-8")
                f.close()




start = time.clock()


op = Opinion()

#op.analyse_file()
op.analyse_files()
end = time.clock()
print u"Обработка завершена за ", "%.1f" % (end-start), u"секунд"