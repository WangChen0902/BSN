import json
import random


f_exception = open("data/data_48_1_3dexceptiondui.txt")
exceptions=f_exception.readlines()

f_kts = open(r"data/data_48_1_3d_boundary.txt")
out = f_kts.read()
kts = json.loads(out)

# kts = []
# num = 0
# for i in range(416):
#     num += random.randint(60, 120)
#     kts.append(num)
#
# print(kts)


# kts = []
# for i in range(42015):
#     if (i%90 ==0):
#         kts.append(i)
# print(kts)

def boundaryJiaozheng(start,end,type=""):
    for i in exceptions:
        test = int(i.split(" ")[0])
        if test > start and test < end:
            if test-start>end-test or type=="5":
                test-=3
                start=start-end+test
                end=test
            elif test-start<=end-test or type=="0" or type=="1":
                test+=3
                end = test+end-start
                start = test
    return start, end

final_jian = open("data/48_1final.txt",'rb')

final_start =[]
final_end = []


row = final_jian.readlines()
for i in row:
    test = str(i).split(" ")
    if test[4][0]!= '3':
        #print(test[4][0])
        start = int(test[1])
        end = start + int(test[2])
        start2, end2 = boundaryJiaozheng(start, end)
        # print(start2,end2)
        final_start.append(start2)
        final_end.append(end2)


TP = 0
IOUarray = []

for i in range(len(final_start)):
    start = final_start[i]
    temp = 10000
    index = 0
    for j in range(len(kts)-1):
        if abs(start - kts[j]) < temp:
            index = j
            temp = abs(start-kts[j])
    kts_start = kts[index]
    kts_end = kts[index + 1]
    end = final_end[i]
    iouArray = []
    iouArray.append(start)
    iouArray.append(end)
    iouArray.append(kts_start)
    iouArray.append(kts_end)
    iouArray.sort()
    IOU =(iouArray[2] - iouArray[1]) / (iouArray[3] - iouArray[0])
    IOUarray.append(IOU)
    if IOU > 0.5:
        TP += 1

startiou = 0.5
endiou = 0.95
ioucount = 0
ioulast = 0
while startiou <= endiou:
    startiou += 0.05
    tempcount = 0
    ioucount += 1
    for i in range(len(IOUarray)):
        if IOUarray[i] > startiou:
            tempcount += 1
    ioulast += (tempcount / len(final_start))
print('平均召回率：',ioulast/ioucount)
recall = TP / len(final_start)
print('IOU等于0.5时：',recall)

