# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 17:42:37 2016

@author: Alfonso
"""

'''
Basic sudoko 
'''

import copy
from heapq import heappush, heappop,heapify


# AFTER CHECK. assign command into sudoku, and  return a new sudoku
def assign(sudoku, command):
    if command[0] == 'V':
        for n in range(0,len(command[2])):
            sudoku[command[1][0] + n][command[1][1]] = command[2][n]
    elif command[0] == 'H':
        for n in range(0,len(command[2])):
            sudoku[command[1][0]][command[1][1] + n] = command[2][n]
    return sudoku


# check whether the sudoGraph is completed
def comp(s):
    for i in s:
        if '_' in i:
            return False
    return True


class sudoku:
    checkDir = ['V','H']
    #define command = ['v'/'h', (x,y),word,word_length], 

    #define the sudoko by identifying file
    def __init__(self,filename1,filename2):
        #iniitial sudograph
        self.sudoGraph = []
        
        self.wordbank = []
        
        #initial fixed character in sudoku:
        self.drawing = {}

        #record track for writing each word
        self.track = []

        row = 0

        self.character = ['A','B','C',"D",'E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
        with open(filename1, 'rt') as file:
            for line in file:
                s = []
                for j in range(0,9):
                    if line[j] == '\n':
                        continue
                    s.append(line[j]) 
                self.sudoGraph.append(s)

                col = 0
                for position in line:
                    if position in self.character:
                        self.drawing[(row,col)] = position
                    col +=1
                row +=1
            #print(self.sudoGraph)

        with open(filename2,'rt') as file:
            for line in file:
                word = []
                for char in line:
                    if char.upper() in self.character:
                        word.append(char.upper())
                self.wordbank.append(word)
        #print(self.wordbank)
    #check one command's availablity
    def checkConstraint(self,sudoku,command):
        #check the direction of this command
        direction = command[0]
        start = command[1]
        word = command[2]

        #check word's length, and set each str into sudoku
        if (direction == 'V') and (start[0]+ len(word) <=9):
            for n in range(0,len(word)):
            #there has been this character in that position
                if word[n] == sudoku[start[0]+n][start[1]]:
                    continue
                #Existing other word OR rowCheck=True OR unitCheck=True OR colCheck=True
                elif (sudoku[start[0]+n][start[1]] in self.character) or (word[n] in sudoku[start[0]+n]) or (self.checkUnit(word[n],(start[0]+n,start[1]),sudoku)) or (self.checkCol(word[n],(start[0]+n,start[1]),sudoku)):
                    #print("Vconflict vh,row,col or unit")
                    return False
                    #print("Vcan set in")
            return True
                    
					
        elif (direction == 'H') and (start[1]+ len(word) <=9):
             for n in range(0,len(word)):
             #there has been this character in that position
                 if word[n] == sudoku[start[0]][start[1]+n]:
                     continue
                 #Existing other word OR rowCheck=True OR unitCheck=True OR colCheck=True
                 elif (sudoku[start[0]][start[1]+n] in self.character) or (word[n] in sudoku[start[0]]) or (self.checkUnit(word[n],(start[0],start[1]+n),sudoku)) or (self.checkCol(word[n],(start[0],start[1]+n),sudoku)):
                     #print("Hconflict vh,wor,col, or unit")
                     return False
             return True
                 
        else:
            return False

    def checkUnit(self,char,position,sudoku):
        i = int(position[0] / 3)
        j = int(position[1] / 3)
        
        for row in [i*3, i*3+1, i*3+2]:
            for col in [j*3, j*3+1, j *3+2]:
                if char == sudoku[row][col]:
                    return True
        return False

    def checkCol(self,char,position,sudoku):
        i = position[0]
        j = position[1]
        for row in range(0,9):
            if char == sudoku[row][j]:
                return True
        return False

    def recursive_search(self,assignment,wordbank):
        #check if completed
        if comp(assignment):
            #self.track = t
            return assignment

        #get one word from wordbank
        word = self.selectWord(assignment,wordbank)
        #print(wordbank)
        #each available command for assignment

        for command in self.domainValues(word,assignment):
            #print(command)
            #check each domainValues' availability
            if self.checkConstraint(assignment,command):
                Nassignment = copy.deepcopy(assignment)
                Nwordbank = copy.deepcopy(wordbank)
                Nwordbank.remove(word)
                Nassignment = assign(Nassignment,command)
                self.track.append(command)
                result = self.recursive_search(Nassignment,Nwordbank)
                if result:
                    return result
                self.track.remove(command)
        #words.remove(word)
        return False

    #pop out a word from wordbank and return this word
    def selectWord(self,assignment,wordbank):
        #store (n-times,'word') exists in assignment
        dict = {}
        #store [(-10,"apple"),(-9,"pine")]
        heap = []
        for word in wordbank:
            count = len(word)
            for char in word:
                if char in dict:
                    count = count + dict[char]
            heap.append((count,word))
        #heappop the most heu from heap
        heap.sort(reverse = True)
        result = heap[0][1]
        return result

    #select possible placements for this word according to sudoGraph
    def domainValues(self,word,assignment):
        command = []
        #each = []
        n=0
        #Available start position going loop
        while(10-len(word)>n):
            #if the first character exists in first rows
            if word[0] in assignment[n]:
                #start creating command. for V/H
                for dir in self.checkDir:
                    each=[]
                    each.append(dir)
                    each.append((n,assignment[n].index(word[0])))
                    each.append(word)
                    each.append(len(word))
                    #print(each)
                    if self.checkConstraint(assignment,each) == True:
                        command.append(each)
            #if the 1st char doesnot exist in 1st row
            else:
                #start creating commands
                for dir in self.checkDir:
                    #try each position of this row as start position
                    if dir == 'V':
                        for i in range(0,9):
                            each=[]
                            each.append(dir)
                            each.append((n,i))
                            each.append(word)
                            each.append(len(word))
                            #print(each, "this is each")
                            if self.checkConstraint(assignment,each) ==True:
                                #print(each,"this V command is OK")
                                command.append(each)
                    if dir == 'H':
                        for i in range(0,9):
                            each = []
                            each.append(dir)
                            each.append((i,n))
                            each.append(word)
                            each.append(len(word))
                            #print(each)
                            if self.checkConstraint(assignment,each) == True:
                                #print(each,"This H command is OK")
                                command.append(each)

            n = n+1
        return command

    def printG(res,outfile):
        with open(outfile,'wt') as file:
            for i in res:
                print(''.join(i),end=" ",file = file)


if __name__ == "__main__":
    su = sudoku("grid2.txt","bank2.txt")
    #print(su.sudoGraph)
    #used for testing traces
    #su.recursive_search(su.sudoGraph,su.wordbank)
    print(su.recursive_search(su.sudoGraph,su.wordbank))
    print(su.track)




