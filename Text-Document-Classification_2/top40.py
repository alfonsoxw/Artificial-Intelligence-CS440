import copy
import math

def confused(docList):
    confusedTopicdDict = {}
    repeat = []
    recordText = []
    for num in range(0,40):
        repeat.append(0)

    for i in range(0,40):
        j = copy.deepcopy(repeat)
        confusedTopicdDict[i] = j

    for doc in docList:
        confusedTopicdDict[doc.sentiment][doc.MPosterior[0]] +=1

    for topic in confusedTopicdDict:
        recordText.append((topic,confusedTopicdDict[topic].index(max(confusedTopicdDict[topic]))))

    return recordText
class doc:
    def __init__(self,sentiment,docs,MPosterior):
        self.sentiment = sentiment
        self.docs = docs
        self.MPosterior = MPosterior

class multinomial:
    def __init__(self,training_file, learning_file,result):
        self.result = result
        #create dict,calculate likelihood nominator
        self.trainOverallCount = []
        for i in range(0,40):
            j = {}
            self.trainOverallCount.append(j)

        self.trainOverallProb = []

        self.volcabulary = set()

        self.learnText = []

        self.trainDoc = [403,504,438,440,392,112,105,250,299,306,314,162,205,139,223,243,203,144,120,106,118,261,282,360,242,207,182,253,332,317,220,232,213,286,304,226,417,248,231,205]

        self.trainPrior = []

        with open(training_file,"rt") as file:
            for line in file:
                c = int(line[0:2])
                if c < 10:
                    text = line[2:len(line)-1].split(" ")
                    for pair in text:
                        key,value = pair.split(":")
                        value = int(value)
                        self.volcabulary.add(key)
                        if key in self.trainOverallCount[c]:
                            self.trainOverallCount[c][key] += value
                        else:
                            self.trainOverallCount[c][key] = value
                else:
                    text = line[3:len(line)-1].split(" ")
                    for pair in text:
                        key, value = pair.split(":")
                        value = int(value)
                        self.volcabulary.add(key)
                        if key in self.trainOverallCount[c]:
                            self.trainOverallCount[c][key] += value
                        else:
                            self.trainOverallCount[c][key] = value
        with open(learning_file,"rt") as file:
            for line in file:
                c = int(line[0:2])
                if c < 10:
                    self.learnText.append(doc(c,line[2:len(line)-1]," "))
                else:
                    self.learnText.append(doc(c,line[3:len(line)-1]," "))

    def likelyhoods_laplacian(self,k):
        unique = len(self.volcabulary)
        #create dictionary containing likelihoods:
        for num in range(0,40):
            dict = {}
            total = sum(self.trainOverallCount[num].values())
            for word in self.volcabulary:
                if word in self.trainOverallCount[num]:
                    dict[word] = (self.trainOverallCount[num][word] + k) / (total + k * unique)
                else:
                    dict[word] =  k / (total + k * unique)
            self.trainOverallProb.append(dict)


    def prior(self):
        #in positive class:
        for i in range(0,40):
            prior = math.log(self.trainDoc[i]/10244)
            self.trainPrior.append(prior)
    def learn(self):
        #MAP posterior = prior * likelihoods of this set of document
        self.prior()
        #print("prior" , priorPos,priorNeg)

        self.likelyhoods_laplacian(0.01)

        #record the result document
        result = []
        unique = len(self.volcabulary)

        #calculating posterior
        for doc in self.learnText:

            text = doc.docs.split(" ")

            #record current doc's words' frequencies
            dict = {}
            #condition = (current_class,current_MPosterior)

            condition = (float('-inf'),float('-inf'))
            c = copy.deepcopy(condition)
            for pair in text:
                key,times = pair.split(":")
                times = int(times)
                dict[key] = times

            num = 0
            for c in self.trainOverallProb:
                prob = self.trainPrior[num]
                total = sum(c.values())
                for word in dict:
                    if word in c:
                        prob = prob + math.log(c[word]) * dict[word]
                    else:
                        continue
                if prob > condition[1]:
                    c = copy.copy(condition)
                    condition = (num,prob)
                num +=1

            doc.MPosterior = condition
            #doc.M = c
            result.append(doc)
        return result

    def accuracy(self):
        result = self.learn()

        recordTestDoc = [0]*40
        recordTestCorrect = []
        for i in range(0,40):
            test = [0] * 40
            recordTestCorrect.append(test)


        #counting tools
        total = 0
        correct = 0
        for object in result:
            recordTestDoc[object.sentiment] +=1
            recordTestCorrect[object.sentiment][object.MPosterior[0]]+=1
            if (object.sentiment == object.MPosterior[0]) :
                correct +=1
            else:
                #print(object.sentiment,object.posterior_1,object.posterior_2)
                pass
            total +=1

        with open(self.result,'wt') as file:
            print(correct,len(result))
            for i in range(0,40):
                for j in recordTestCorrect[i]:
                    x = j / recordTestDoc[i]
                    print(x,end = "  ",file = file)
                print("\n",file = file)

        return (correct/total)


    def start(self):
        print("accuracy: " ,self.accuracy())

class bernoulli:
    def __init__(self,training_file, learning_file,result):
        self.result = result
        #create dict,calculate likelihood nominator
        self.trainOverallCount = []
        for i in range(0,40):
            j = {}
            self.trainOverallCount.append(j)

        self.trainOverallProb = []

        self.volcabulary = set()

        self.learnText = []

        self.trainDoc = [403,504,438,440,392,112,105,250,299,306,314,162,205,139,223,243,203,144,120,106,118,261,282,360,242,207,182,253,332,317,220,232,213,286,304,226,417,248,231,205]

        self.trainPrior = []

        with open(training_file,"rt") as file:
            for line in file:
                c = int(line[0:2])
                if c < 10:
                    text = line[2:len(line)-1].split(" ")
                    for pair in text:
                        key,value = pair.split(":")
                        self.volcabulary.add(key)
                        if key in self.trainOverallCount[c]:
                            self.trainOverallCount[c][key] += 1
                        else:
                            self.trainOverallCount[c][key] = 1
                else:
                    text = line[3:len(line)-1].split(" ")
                    for pair in text:
                        key, value = pair.split(":")
                        self.volcabulary.add(key)
                        if key in self.trainOverallCount[c]:
                            self.trainOverallCount[c][key] += 1
                        else:
                            self.trainOverallCount[c][key] = 1
        with open(learning_file,"rt") as file:
            for line in file:
                c = int(line[0:2])
                if c < 10:
                    self.learnText.append(doc(c,line[2:len(line)-1]," "))
                else:
                    self.learnText.append(doc(c,line[3:len(line)-1]," "))

    def likelyhoods_laplacian(self,k):
        #create dictionary containing likelihoods:
        for num in range(0,40):
            dict = {}
            total = self.trainDoc[num]
            for word in self.volcabulary:
                if word in self.trainOverallCount[num]:
                    dict[word] = (self.trainOverallCount[num][word] + k) / (total + k * 2)
                else:
                    dict[word] =  k / (total + k * 2)
            self.trainOverallProb.append(dict)


    def prior(self):
        #in positive class:
        for i in range(0,40):
            prior = math.log(self.trainDoc[i]/10244)
            self.trainPrior.append(prior)
    def learn(self):
        #MAP posterior = prior * likelihoods of this set of document
        self.prior()

        self.likelyhoods_laplacian(0.09)

        #record the result document
        result = []
        unique = len(self.volcabulary)

        #calculating posterior
        for doc in self.learnText:

            text = doc.docs.split(" ")

            #record current doc's words' frequencies
            dict = {}
            #condition = (current_class,current_MPosterior)

            condition = (float('-inf'),float('-inf'))
            c = (float('-inf'),float('-inf'))
            for pair in text:
                key,times = pair.split(":")
                times = int(times)
                dict[key] = times

            num = 0
            for topic in self.trainOverallProb:
                prob = self.trainPrior[num]
                total = sum(topic.values())
                for word in dict:
                    if word in topic:
                        prob = prob + math.log(topic[word]) * dict[word]
                    else:
                        continue
                if prob > condition[1]:
                    c = condition
                    condition = (num,prob)
                num +=1

            doc.MPosterior = condition
            result.append(doc)
        return result

    def accuracy(self):
        result = self.learn()
        confusedCheckList = []
        recordTestDoc = [0]*40
        recordTestCorrect = []
        for i in range(0,40):
            test = [0] * 40
            recordTestCorrect.append(test)


        #counting tools
        total = 0
        correct = 0
        for object in result:
            recordTestDoc[object.sentiment] +=1
            recordTestCorrect[object.sentiment][object.MPosterior[0]]+=1
            if (object.sentiment == object.MPosterior[0]) :
                correct +=1
            else:
                confusedCheckList.append(object)
            total +=1

        recordConfuse = confused(confusedCheckList)
        with open("confusedTopic.txt",'wt') as file:
            print(recordConfuse,end = "\n",file = file)


        with open(self.result,'wt') as file:
            print(correct,len(result))
            for i in range(0,40):
                for j in recordTestCorrect[i]:
                    x = j / recordTestDoc[i]
                    print(x,end = "  ",file = file)
                print("\n",file = file)

        return (correct/total)


    def start(self):
        print("accuracy: " ,self.accuracy())



if __name__ == '__main__':
    #fisher = multinomial("fisher_train_40topic.txt","fisher_test_40topic.txt","fisher_multinomial_result.txt")
    #fisher.start()

    fisher1 = bernoulli("fisher_train_40topic.txt","fisher_test_40topic.txt","fisher_bernoulli_result.txt")
    fisher1.start()