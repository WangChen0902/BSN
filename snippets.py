import os
import cv2
import numpy as np

ROOT_PATH="/data/dataset/dataset"
def getVideoAllframe(tagName):
    video_full_path=ROOT_PATH+"/"+tagName.split("_")[0]+"/"+"data_"+tagName+"_3d.mp4"
    print(video_full_path)
    biaoji_full_path=ROOT_PATH+"/"+tagName.split("_")[0]+"/"+"biaoji.txt"
    f=open(biaoji_full_path,"r")
    line_count=0
    start=0
    for line in f.readlines():
        if line_count==0:
            line_count+=1
            continue
        if line.split(",")[2].split(" ")[0].split("_")[2]==tagName.split("_")[1]:
            start=int(line.split(",")[2].split(" ")[1])
    if start==0:
        print("exception!   匹配失败")
    cap = cv2.VideoCapture(video_full_path)
    frames_num = cap.get(7)
    return int(frames_num) - int(start)


def getSegmentNumber(segmentCount,exceptions,tagName):
    if segmentCount==0: #第一个片段
        return exceptions[0]-3,0
    elif segmentCount<len(exceptions):
        return exceptions[segmentCount]-exceptions[segmentCount-1]-6,exceptions[segmentCount-1]+3
    else: #最后一个片段
        return getVideoAllframe(tagName)-exceptions[segmentCount-1]-2,exceptions[segmentCount-1]+3


def getSnippetCount(num_of_one_segment):
    # if num_of_one_segment%16==0:
    #     return num_of_one_segment//16
    # else:
    #     return  (num_of_one_segment//16) +1
    return num_of_one_segment//16


def changeToint(exceptions):
    result=[]
    for i in exceptions:
        result.append(int(i.split(" ")[0]))
    return result


def controlRange(x, range):
    if x <= 0:
        x = 0
    if x >= range:
        x = range
    return x


def getSnippetLabel(x1, x2, snip):
    snip_1 = snip*16
    snip_2 = (snip+1)*16
    #print(snip_1, snip_2)
    if(x1<=snip_1 and x2>=snip_2):
        return 1
    elif(x1>snip_1 and x2>=snip_2):
        if(x1 - snip_1 <= 8):
            return 1
        else:
            return 0
    elif(x1<=snip_1 and x2<snip_2):
        if(snip_2 - x2 <= 8):
            return 1
        else:
            return 0
    elif(x1>snip_1 and x2<snip_2):
        if(x1 - x2 >= 8):
            return 1
        else:
            return 0
    else:
    	return 0


def getSnippets(tagName):
    f_exception=open(ROOT_PATH+"/"+tagName.split("_")[0]+"/result/"+"data_"+tagName+"_3dexceptiondui.txt")
    exceptions=changeToint(f_exception.readlines())
    #print(exceptions)
    num_of_segment=len(exceptions)+1
    folder = "./split_save/"
    result=[]
    for i in range(num_of_segment):
        num_of_one_segment,boundary = getSegmentNumber(i, exceptions, tagName)
        print("num_of_one_segment "+str(num_of_one_segment%16+6))
        #print(num_of_one_segment)
        snippet_count = getSnippetCount(num_of_one_segment)
        #print(snippet_count)
        event = []
        f = open(folder + "/"+tagName+"_" + str(i) + ".txt", 'r')
        line = f.readline()
        while line:
            event.append(line.strip())
            line = f.readline()
        print(i)
        print(event)
        snippet_label = []
        # 0 background, 1 action, 2 start/end
        for m in range(snippet_count):
            snippet_label.append(0)
        for j in event:
            start = int(j.split(' ')[1])
            duration = int(j.split(' ')[2])
            action_type = int(j.split(' ')[4])
            no_startend = False
            if action_type==3 or action_type==4:
                no_startend = True
            start_1 = controlRange(start - duration//5, num_of_one_segment)
            start_2 = controlRange(start + duration//5, num_of_one_segment)
            end_1 = controlRange(start + duration - duration//5, num_of_one_segment)
            end_2 = controlRange(start + duration + duration//5, num_of_one_segment)
            action_1 = controlRange(start, num_of_one_segment)
            action_2 = controlRange(start + duration, num_of_one_segment)
            print(start_1, start_2, end_1, end_2, action_1, action_2, num_of_one_segment)
            for k in range(snippet_count):
                if(snippet_label[k]==0 or snippet_label[k]==1):
                    if getSnippetLabel(action_1, action_2, k)==1 and no_startend==False:
                        snippet_label[k] = 1
                    if getSnippetLabel(start_1, start_2, k)==1 and no_startend==False:
                        snippet_label[k] = 2
                    if getSnippetLabel(end_1, end_2, k)==1 and no_startend==False:
                        snippet_label[k] = 3
                if (k==0):
                    snippet_label[k] = 2
                if (k==snippet_count-1):
                    snippet_label[k] = 3
        result.append(snippet_label)
        #print(snippet_label)
        file_name = 'label_save/' + tagName + '_' + str(i) + '_label.txt'
        f_ = open(file_name, 'w+')
        print(snippet_label)
        # print(exceptions[i])
        for line in snippet_label:
            f_.write(str(line)+'\n')
    return result
def flatten(l):
    result=[]
    for k in l:
        result+=k
    return result

tag_name = '4_2'
test=flatten(getSnippets(tag_name))
segmetn_count = (len(test) ) // 100
count=0
print(test)
for i in range(segmetn_count):
    print(test[i*100:(i+1)*100])
    print(count)
    print("-----------------")
    count+=1
