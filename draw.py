import csv
import os
import random

class draw(object):
    def __init__(self):
        self.input_file = None
        self.traj_file = None

        self.input = None
        self.traj = None
        
        self.zero = ['0','0','0']
        self.params = []
        self.dist = []
        self.tour = []
        self.d = 0
        self.delta = 0

        self.parameters = [["TOURSET", "DISTRIBUTIONS", None, 
                            "ALPHA", "BETA", "GAMMA", None, 
                            "RANDOM", "DELTA", None]]
        self.data = {}
        self.trajectory = {}
        self.data[0] = ["TOURID", "DATA"]
        
    def run(self, tourID, delta):
        isParam = True
        length = 0
        for i, result in enumerate(self.input):
            if i == 0:
                length = len(result) - 5
                for x in range(length):
                    self.tour.append([])
            if (result[-5:-2] == self.zero):
                if i == 0:
                    self.input_file.close()
                    return False
                else:
                    isParam = False
            if (isParam):
                self.params.append([result[-5], result[-4], result[-3]])
                self.dist.append([result[-2], result[-1]])
            for index in range(length):
                self.tour[index].append(float(result[index]))
            
        index = self.random(delta)
        self.parameters.append([tourID, self.dist[0][self.delta], None] + self.params[0] + [None, index, self.d, None])
        for i, row in enumerate(self.params):
            if i == 0:
                continue
            self.parameters.append([None, self.dist[i][self.delta], None] + self.params[i])
        self.parameters.append([])
        self.data[tourID] = self.tour[self.d]
        self.input_file.close()
        coords = []
        for i, row in enumerate(self.traj):
            if i == 0:
                continue
            coords.append(row[0])
            coords.append(row[1])
        self.trajectory[tourID] = coords
        self.traj_file.close()
        return True
            
    def random(self, delta):
        index = random.random()
        total = 0
        if (delta == '0.2'):
            self.delta = 0
        else:
            self.delta = 1
        for i, d in enumerate(self.dist):
            total += float(d[self.delta])
            if total >= index:
                self.d = i
                break
        total = 0
        return index
        
    def new(self, inputfile, trajfile, delta):
        random.seed()
        try:
            self.input_file = open(inputfile, 'r', newline = '')
            self.input = csv.reader(self.input_file, delimiter = ',')

            self.traj_file = open(trajfile, 'r', newline = '')
            self.traj = csv.reader(self.traj_file, delimiter = ',')
        except IOError:
            return False
        
        self.params = []
        self.tour = []
        self.dist = []
        return True

    def reset(self, delta):
        self.parameters = [["TOURSET", "DISTRIBUTIONS "+ delta, None, 
                             "ALPHA", "BETA", "GAMMA", None, 
                             "RANDOM", "DELTA " + delta]]
        self.data = {}
        self.trajectory = {}
        self.data[0] = ["TOURID", "DATA"]

    def getData(self):
        if len(self.data) > 1:
            return self.data
        else:
            return None

    def getTrajectory(self):
        return self.trajectory;

    def write(self, type, name, directory):
        if name[-4:] != '.csv':
            name = name + '.csv'
        try:
            with open(os.path.join(directory, name), 'w', newline = '') as stream:
                output = csv.writer(stream, delimiter = ',')
                if type == 'DATA':
                    for row in self.data:
                        output.writerow(row)
                elif type == "PARAM":
                    for row in self.parameters:
                        output.writerow(row)
                stream.close()
        except PermissionError:
            raise PermissionError