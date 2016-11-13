import copy
import math

def top10(likelyNominator,likelyDenominator):
    list = []
    q = 0
    for entry in sorted(likelyNominator.items(),key = lambda x : x[1],reverse = True):
        list.append(entry)
        q+=1
        if q == 10:
            break

    q = 0
    newLikely = {}
    for word in likelyNominator:
        newLikely[word] = math.e**(likelyNominator[word] - likelyDenominator[word])

    for entry in sorted(newLikely.items(),key = lambda x : x[1],reverse = True):
        list.append(entry)
        q+=1
        if q == 10:
            break

    return list



class doc:
    def __init__(self,sentiment,docs,posterior_1,posterior_2):
        self.sentiment = sentiment
        self.docs = docs
        self.posterior_1 = posterior_1
        self.posterior_2 = posterior_2

class multinomial:
    def __init__(self,training_file, learning_file,result):
        self.result = result
        #create dict,calculate likelihood nominator
        self.trainPos = {}
        self.trainNeg = {}

        #record words' quantities,calculate likelihood denominator
        self.trainPosNumber = 0
        self.trainNegNumber = 0

        #record documents' quantities,calculate prior
        self.trainPosDoc = 0
        self.trainNegDoc = 0

        self.learnText = []

        self.volcabulary = set()

        self.likely_pos = {}
        self.likely_neg = {}

        with open(training_file,"rt") as file:
            for line in file:
                if line[0] == '1':
                    text = line[2:len(line)-1].split(" ")
                    for pair in text:
                        key,value=pair.split(":")
                        value = int(value)
                        self.volcabulary.add(key)
                        if key in self.trainPos:
                            self.trainPos[key] += int(value)
                        else:
                            self.trainPos[key] = int(value)
                        self.trainPosNumber += int(value)
                    self.trainPosDoc +=1
                if line[0] == '-':
                    text = line[3:len(line)-1].split(" ")
                    for pair in text:
                        key, value = pair.split(":")
                        value = int(value)
                        self.volcabulary.add(key)
                        if key in self.trainNeg:
                            self.trainNeg[key] += int(value)
                        else:
                            self.trainNeg[key] = int(value)
                        self.trainNegNumber += int(value)
                    self.trainNegDoc += 1

        with open(learning_file,"rt") as file:
            for line in file:
                if line[0] == "1":
                    self.learnText.append(doc("1",line[2:len(line)-1],0.0,0.0))
                if line[0] == "-":
                    self.learnText.append(doc("-1",line[3:len(line)-1],0.0,0.0))

    def likelyhoods_laplacian(self,k):
        #create dictionary containing likelihoods:

        for word in self.volcabulary:
            if word in self.trainPos:
                self.likely_pos[word] = math.log((self.trainPos[word] + k)) - math.log(self.trainPosNumber + k * len(self.volcabulary))
            else:
                self.likely_pos[word] = math.log((1 + k )/ (self.trainPosNumber + k * len(self.volcabulary)))
            if word in self.trainNeg:
                self.likely_neg[word] = math.log((self.trainNeg[word] + k)) - math.log(self.trainNegNumber + k * len(self.volcabulary))
            else:
                self.likely_neg[word] = math.log((1 + k) / (self.trainNegNumber + k * len(self.volcabulary)))



    def prior(self,classification):
        #in positive class:
        if classification == "1":
            return math.log(self.trainPosDoc / (self.trainPosDoc + self.trainNegDoc))
        #in negative class:
        elif classification == "-1":
            return math.log(self.trainNegDoc / (self.trainPosDoc + self.trainNegDoc))

    def learn(self):
        #MAP posterior = prior * likelihoods of this set of document
        #priorPos is a dictionary of trained data
        priorPos = self.prior("1")
        priorNeg = self.prior("-1")
        print("prior" , priorPos,priorNeg)

        self.likelyhoods_laplacian(1)

        # for positive document
        PosResult = []
        NegResult = []

        #record the result document
        result = []
        #calculating posterior
        for doc in self.learnText:

            text = doc.docs.split(" ")
            condition_1 = priorPos
            condition_2 = priorNeg
            for pair in text:
                key,times = pair.split(":")
                times = int(times)
                if key in self.volcabulary:
                    condition_1 = condition_1 + self.likely_pos[key]*times
                    condition_2 = condition_2 + self.likely_neg[key]*times

            doc.posterior_1 = condition_1
            doc.posterior_2 = condition_2
            result.append(doc)
        return result

    def accuracy(self):
        result = self.learn()

        #counting tools
        total = 0
        correct = 0
        #(label1 correct, label-1 correct)
        accumulator = [0,0]
        accumDoc = [0,0]
        print(len(result))
        for o in result:
            if o.sentiment == "1":
                accumDoc[0] +=1
            elif o.sentiment == "-1":
                accumDoc[1] +=1

        for object in result:
            if (object.posterior_1 >= object.posterior_2) and (object.sentiment == "1") :
                accumulator[0]+=1
                correct +=1
            elif ((object.posterior_1) <= object.posterior_2) and (object.sentiment == "-1"):
                accumulator[1]+=1
                correct +=1
            total +=1


        with open(self.result,'wt') as file:
            print("accuracy: ", (correct/total),end = "\n", file = file)
            print(accumulator[0]/accumDoc[0],"    ",(1-accumulator[0]/accumDoc[0]),end = "\n",file = file)
            print((1-accumulator[1] / accumDoc[1]),"    ",accumulator[1]/accumDoc[1],end = "\n", file = file)

        return (correct/total)


    def start(self,filename):
        print("accuracy: " ,self.accuracy())

        #top 10 list
        positive10 = top10(self.likely_pos,self.likely_neg)
        negative10 = top10(self.likely_neg,self.likely_pos)

        with open(filename,'wt') as file:
            print("Top10 with highest likelihood of class 1: \n" , file = file)
            for each in range(0,10):
                print(str(positive10[each]),end = '\n',file=file)
            print("Top10 with highest odds rate of class 1: (Pr(word|class1)/Pr(word|class(-1))) in logarithm\n", file =file)
            for each in range(10,20):
                print(str(positive10[each]),end = '\n',file=file)

            print("Top10 with highest likelihood of class (-1): \n" , file = file)
            for each in range(0,10):
                print(str(negative10[each]) , end = '\n',file = file)
            print("Top10 with highest odds rate of class (-1):(Pr(word|class(-1))/Pr(word|class1)) in logarithm",file =file)
            for each in range(10,20):
                print(str(negative10[each]), end = '\n',file = file)

class bernoulli:
    def __init__(self,training_file, learning_file,result):
        self.result = result
        #create dict,calculate likelihood nominator
        self.trainPos = {}
        self.trainNeg = {}

        #record documents' quantities,calculate prior
        self.trainPosDoc = 0
        self.trainNegDoc = 0

        self.learnText = []

        #restore words' likelihood
        self.likely_pos = {}
        self.likely_neg = {}

        self.volcabulary = set()

        with open(training_file,"rt") as file:
            for line in file:
                if line[0] == '1':
                    text = line[2:len(line)-1].split(" ")
                    for pair in text:
                        key,value=pair.split(":")
                        self.volcabulary.add(key)
                        if key in self.trainPos:
                            self.trainPos[key] += 1
                        else:
                            self.trainPos[key] = 1
                    self.trainPosDoc +=1
                if line[0] == '-':
                    text = line[3:len(line)-1].split(" ")
                    for pair in text:
                        key,value = pair.split(":")
                        self.volcabulary.add(key)
                        if key in self.trainNeg:
                            self.trainNeg[key] += 1
                        else:
                            self.trainNeg[key] = 1
                    self.trainNegDoc += 1

        with open(learning_file,"rt") as file:
            for line in file:
                if line[0] == "1":
                    self.learnText.append(doc("1",line[2:len(line)-1],0.0,0.0))
                if line[0] == "-":
                    self.learnText.append(doc("-1",line[3:len(line)-1],0.0,0.0))


    def likelyhoods_laplacian(self,k):
        #create dictionary containing likelihoods:

        for word in self.volcabulary:
            if word in self.trainPos:
                self.likely_pos[word] = (self.trainPos[word] + k) / (self.trainPosDoc + k * 2)
            else:
                self.likely_pos[word] = (0+k) / (self.trainPosDoc + k*2)

            if word in self.trainNeg:
                self.likely_neg[word] = (self.trainNeg[word] + k) / (self.trainNegDoc + k * 2)
            else:
                self.likely_neg[word] = (0+k) / (self.trainNegDoc + k*2)

        #print(self.likely_pos)

    def prior(self,classification):
        #in positive class:
        if classification == "1":
            return math.log(self.trainPosDoc / (self.trainPosDoc + self.trainNegDoc))
        #in negative class:
        elif classification == "-1":
            return math.log(self.trainNegDoc / (self.trainPosDoc + self.trainNegDoc))

    def learn(self):
        #MAP posterior = prior * likelihoods of this set of document
        #priorPos is a dictionary of trained data
        priorPos = self.prior("1")
        priorNeg = self.prior("-1")

        self.likelyhoods_laplacian(3)

        # for positive document
        PosResult = []
        NegResult = []

        #record the result document
        result = []
        #calculating posterior
        for doc in self.learnText:

            text = doc.docs.split(" ")
            condition_1 = priorPos
            condition_2 = priorNeg
            log = []
            for pair in text:
                key,value= pair.split(":")
                log.append(key)

            for word in self.volcabulary:
                if word in log:
                    condition_1 = condition_1 + math.log(self.likely_pos[word])
                    condition_2 = condition_2 + math.log(self.likely_neg[word])
                else:
                    condition_1 = condition_1 + math.log(1.0-self.likely_pos[word])
                    condition_2 = condition_2 + math.log(1.0-self.likely_neg[word])

            doc.posterior_1 = condition_1
            doc.posterior_2 = condition_2
            result.append(doc)
        return result

    def accuracy(self):
        result = self.learn()

        #counting tools
        total = 0
        correct = 0
        #(label1 correct, label-1 correct)
        accumulator = [0,0]
        accumDoc = [0,0]
        print(len(result))
        for o in result:
            if o.sentiment == "1":
                accumDoc[0] +=1
            elif o.sentiment == "-1":
                accumDoc[1] +=1

        for object in result:
            if (object.posterior_1 >= object.posterior_2) and (object.sentiment == "1") :
                accumulator[0]+=1
                correct +=1
            elif ((object.posterior_1) <= object.posterior_2) and (object.sentiment == "-1"):
                accumulator[1]+=1
                correct +=1
            total +=1


        with open(self.result,'wt') as file:
            print("accuracy: ", (correct/total),end = "\n", file = file)
            print(accumulator[0]/accumDoc[0],"    ",(1-accumulator[0]/accumDoc[0]),end = "\n",file = file)
            print((1-accumulator[1] / accumDoc[1]),"    ",accumulator[1]/accumDoc[1],end = "\n", file = file)

        return (correct/total)

    def start(self,filename):
        print("accuracy: " ,self.accuracy())

        #top 10 list
        positive10 = top10(self.likely_pos,self.likely_neg)
        negative10 = top10(self.likely_neg,self.likely_pos)

        with open(filename,'wt') as file:
            print("Top10 with highest likelihood of class 1: \n" , file = file)
            for each in range(0,10):
                print(str(positive10[each]),end = '\n',file=file)
            print("Top10 with highest odds rate of class 1: (Pr(word|class1)/Pr(word|class2)) in logarithm\n", file =file)
            for each in range(10,20):
                print(str(positive10[each]),end = '\n',file=file)

            print("Top10 with highest likelihood of class 2: \n" , file = file)
            for each in range(0,10):
                print(str(negative10[each]) , end = '\n',file = file)
            print("Top10 with highest odds rate of class 2:(Pr(word|class2)/Pr(word|class1)) in logarithm",file =file)
            for each in range(10,20):
                print(str(negative10[each]), end = '\n',file = file)


if __name__ == "__main__":
    #rt = multinomial("rt-train.txt","rt-test.txt","rt_nultinomial_result.txt")
    #fisher = multinomial("fisher_train_2topic.txt","fisher_test_2topic.txt","fisher_multinomial_result.txt")
    #rt.start("rt_multinomial_top10list.txt")
    #fisher.start("fisher_multinomial_top10list.txt")

    fisher1 = bernoulli("fisher_train_2topic.txt","fisher_test_2topic.txt","fisher_bernoulli_result.txt")
    fisher1.start("fishe_bernoulli_top10list.txt")
    rt1 = bernoulli("rt-train.txt","rt-test.txt","rt_bernoulli_result.txt")
    rt1.start("rt_bernoulli_top10list.txt")










