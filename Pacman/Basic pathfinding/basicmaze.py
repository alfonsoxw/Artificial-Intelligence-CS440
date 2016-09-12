'''
Basic path finding for Pacman assignment
Author:　Litian Ma
'''


class Maze:

    check_priority = ['u', 'r', 'd', 'l']
    # initialize the maze by identifying the filename
    def __init__(self, filename):
        # width, height, startPos, dotsPos, mazeGraph


        # maze represented by two dim list
        self.mazeGraph = []



        # all dots' position
        self.dotsPos = []

        # find start position
        row = 0

        with open(filename, 'rt') as file:
            for line in file:
                self.mazeGraph.append(list(line))

                # check whether there is a start point(only one)
                startcol = line.find('P')
                if startcol != -1:
                    self.startPos = (row, startcol)
                    self.width = len(line)

                # check whether there is a dot
                for i in range(len(line)):
                    if line[i] == '.':
                        self.dotsPos.append((row, i))
                row += 1
            self.height = row

    def is_accessable(self, direction, row, column):
        if direction == 'u':
            return row != 0 and self.mazeGraph[row - 1][column] != '%'
        elif direction == 'd':
            return row != self.height - 1 and self.mazeGraph[row + 1][column] != '%'
        elif direction == 'l':
            return column != 0 and self.mazeGraph[row][column - 1] != '%'
        elif direction == 'r':
            return column != self.width - 1 and self.mazeGraph[row][column + 1] != '%'

    def find_all_accessable (self, check_priority, row, column):
        result = []
        for i in check_priority:
            if self.is_accessable(i, row, column):
                if i == 'u': result.append((row - 1, column))
                elif i == 'd': result.append((row + 1, column))
                elif i == 'l': result.append((row, column - 1))
                elif i == 'r': result.append((row, column + 1))

        return result

    def dfs(self):
        dfs_result = self.mazeGraph
        Set, Queue = set(), []
        Queue.append(self.startPos)

        while Queue:
            cur = Queue.pop()
            if cur in Set:
                continue

            Set.add(cur)
            if cur in self.dotsPos:
                break
            Queue.extend(self.find_all_accessable(Maze.check_priority, cur[0], cur[1]))
            dfs_result[cur[0]][cur[1]] = '.'

        return dfs_result

    def printgraph (self, result_graph):
        with open('mazeresult.txt', 'wt') as f:
            for line in result_graph:
                print(''.join(line), file=f)

if __name__ == '__main__':
    mz = Maze('mediumMaze.txt')
    mz.printgraph(mz.dfs())



