# class fifoQueue2(list, maxlength=None):

#     def add_new_arrival(self, from_number, time_arrived, text_of_SMS):
#         self.append((False, from_number, time_arrived, text_of_SMS))    #append tuple to self

#     def message_count(self):
#         return len(self)


class fifoQueue(list):

    def __init__(self, max_length):
        self.max_length = max_length
        super(fifoQueue, self).__init__(self) 
    
    def put(self, item):
            self.append(item)
            if len(self) > self.max_length:
                self.pop(0)

    def isEmpty(self):
        return self.Empty()
    
    def size(self):
        return len(self)
    
    def avgSignal(self):
        total = 0
        for i in range(len(self)):
            #print("Items are : " + str(self[i]))
            total = total+ self[i]
        return total/len(self)
    
    def avgWeightedSignal(self, halfSize):      # S(avg)
        total = 0
        wtTotal = 0
        for i in range(len(self)):
            #print("Items are : " + str(self[i]))
            wt = 2**(-i/halfSize)
            total = total+ self[i]*wt
            wtTotal += wt
        return total/wtTotal
    
    def agrSignal(self,size):
        if len(self) > size:
            length = size
        else:
            length = len(self)
        tempDict = dict()
        for i in range(length):
            if str(int(float(self[len(self)-i-1])*monitor.percentToNano/monitor.cpuBucWidth)+1) in tempDict: 
                tempDict.update({str(int(float(self[len(self)-i-1])*monitor.percentToNano/monitor.cpuBucWidth)+1):str(int(tempDict.get(str(int(float(self[len(self)-i-1])*monitor.percentToNano/monitor.cpuBucWidth)+1)))+1)})
            else:
                tempDict.update({str(int(float(self[len(self)-i-1])*monitor.percentToNano/monitor.cpuBucWidth)+1):'1'})
        upSum = 0
        downSum = 0
        for key, value in tempDict.items():
            upSum += int(key) * int(value)
            downSum += int(value)
        return upSum/downSum
    
    def peakSignal(self):
        max = 0
        for i in self:
            max = i if i>max else max
        return max
