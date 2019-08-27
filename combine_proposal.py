import numpy as np
import pandas as pd
import json
import os
import sys
import operator

def get_simple_file_name(dir):
    files = os.listdir(dir)
    full_names = []
    for file in files:
        # file = dir + file
        file = file.split('.')[0]
        full_names.append(file)
    return full_names

def get_full_file_name(dir):
    files = os.listdir(dir)
    full_names = []
    for file in files:
        file = file.split('_')[0]+'_'+file.split('_')[1]
        if file not in full_names:
            full_names.append(file)
    return full_names

def load_json(file):
    with open(file) as json_file:
        data = json.load(json_file)
        return data

def get_exception(index):
    exception = []
    exceptioin_time = []
    first_name = index.split('_')[0]
    file_path = '/data/dataset/dataset/'+first_name+'/result/data_'+index+'_3dexceptiondui.txt'
    exception_txt = open(file_path, 'r', encoding='UTF-8')
    line = exception_txt.readline()
    while line:
        exception.append(line.strip())
        line = exception_txt.readline()
    exception_txt.close()
    for item in exception:
        item_info = item.split(' ')
        exceptioin_time.append(item_info[0])
    return exceptioin_time

def get_new_exception(dataset, index):
    exception = []
    first_name = index.split('_')[0]
    file_path = 'output/exception/'+dataset+'/'+index+'.txt'
    exception_txt = open(file_path, 'r', encoding='UTF-8')
    line = exception_txt.readline()
    while line:
        exception.append(line.strip())
        line = exception_txt.readline()
    exception_txt.close()
    return exception

def get_final(dataset, index):
    final = []
    types = []
    first_name = index.split('_')[0]
    file_path = '/data/dataset/dataset/'+first_name+'/result/'+index+'final.txt'
    final_txt = open(file_path, 'r', encoding='UTF-8')
    line = final_txt.readline()
    while line:
        line_list = line.split(' ')
        start = int(line_list[1])
        end = start + int(line_list[2])
        event_type = int(line_list[4])
        if event_type != 3 and event_type !=4:
            event = [start, end]
            final.append(event)
            types.append(event_type)
        line = final_txt.readline()
    exceptions = get_new_exception(dataSet, index)
    #print(exceptions)
    #print(final)
    #for excpt in exceptions:
    #    for e in final:
    #        for e_idx in range(len(e)):
    #            if abs(e[e_idx]-int(excpt))<3:
    #                if e[e_idx]>int(excpt):
    #                    e[e_idx] = int(excpt)+3
    #                if e[e_idx]<int(excpt):
    #                    e[e_idx] = int(excpt)-3
    #print(final)
    return final,types

def get_recall(groundtruth,types, proposal,index):
    # f = open(str(index)+'_proposal_log.txt', 'w')
    # f.write('--------------------------\n')
    TP = 0
    count = len(groundtruth)
    proposal_len = len(proposal)
    for g_index in range(len(groundtruth)):
        g =groundtruth[g_index]
        flag = False
        for p in proposal:
            if g[0]>p[0]:
                start0 = p[0]
                start1 = g[0]
            else:
                start0 = g[0]
                start1 = p[0]
            if g[1]>p[1]:
                end0 = p[1]
                end1 = g[1]
            else:
                end0 = g[1]
                end1 = p[1]
            inner_len = end0 - start1
            outer_len = end1 - start0
            iou = float(inner_len) / float(outer_len)
            if iou>=0.5:
                TP = TP +1
                flag = True
                break
        # if flag==False:
            # print('g: ',g[0],g[1])
            # print('g_len: ', g[1]-g[0])
            # print('g_type: ',types[g_index])
            # f.write('g: '+str(g[0])+' '+str(g[1])+'\n')
            # f.write('g_len: '+str(g[1]-g[0])+'\n')
            # f.write('g_type: '+str(types[g_index])+'\n')
    recall = TP/count
    print('count: ',count)
    print('proposal_len: ',proposal_len)
    print('TP: ',TP)
    return recall

def get_shortest(groundtruth,types, proposal,index):
    f = open(str(index)+'_proposal_log.txt', 'w')
    TP = 0
    count = len(groundtruth)
    proposal_len = len(proposal)
    for g_index in range(len(groundtruth)):
        best_iou = 0
        best_proposal = [0,0]
        g =groundtruth[g_index]
        flag = False
        for p in proposal:
            if g[0]>p[0]:
                start0 = p[0]
                start1 = g[0]
            else:
                start0 = g[0]
                start1 = p[0]
            if g[1]>p[1]:
                end0 = p[1]
                end1 = g[1]
            else:
                end0 = g[1]
                end1 = p[1]
            inner_len = end0 - start1
            outer_len = end1 - start0
            iou = float(inner_len) / float(outer_len)
            if iou>best_iou:
                best_iou = iou
                best_proposal = [p[0], p[1]]
        if best_iou<0.5:
            short_0 = best_proposal[0]-g[0]
            short_1 = best_proposal[1]-g[1]
            g_lenth = g[1] - g[0]
            f.write('groundtruth: ['+str(g[0])+','+str(g[1])+']\n')
            f.write('groundtruth_lenth: '+str(g_lenth)+'\n')
            f.write('best_proposal: ['+str(best_proposal[0])+','+str(best_proposal[1])+']\n')
            f.write('best_iou: '+str(best_iou)+'\n')
            f.write('boundary: ['+str(short_0)+','+str(short_1)+']\n')

dataSet = sys.argv[1]
file_path = "./output/TEM_results/"+dataSet+"/"
video_list = get_simple_file_name(file_path)
full_video_list = get_full_file_name(file_path)
# print(full_video_list)
json_file = load_json("./output/"+dataSet+"_result_proposal.json")

results = json_file['results']

info_list = {}
for info in results:
    video_name_list = info.split('_')
    first_name = video_name_list[0]+'_'+video_name_list[1]
    second_name = video_name_list[2]
    if first_name not in info_list:
        info_list[first_name] = {}
    info_list[first_name][int(second_name)] = results[info]
new_info_list = {}
for index in info_list:
    sorted_info = sorted(info_list[index].items(), key=lambda x:x[0])
    new_info_list[index] = sorted_info
#print(new_info_list['4_2'])
# sorted_info = sorted(info_list.items(), key=lambda x:x[0])
frame_info_list = {}
for i in new_info_list:
    frame_info_list[i] = []
    for j in new_info_list[i]:
        #print(j[0])
        current_index = j[0]
        #print(j[1])
        for k in j[1]:
            new_frame = [int((k['segment'][0]+current_index)*100),int((k['segment'][1]+current_index)*100)]
            frame_info_list[i].append(new_frame)
        # print(j)
for ii in frame_info_list:
    frame_info_list[ii].sort(key=lambda x:x[0])
first_4_2 = []
for i in range(len(frame_info_list['4_2'])):
    tmp_list = [int(frame_info_list['4_2'][i][0]), int(frame_info_list['4_2'][i][1])]
    first_4_2.append(tmp_list)
print(first_4_2)

for index in frame_info_list:
    for frame in frame_info_list[index]:
        for f in range(len(frame)):
            frame[f] = frame[f]*16 + 8

diff_dict = {}

for index in frame_info_list:
    # print(index)
    exceptions = get_new_exception(dataSet, index)
    # file = 'output/exception/'+dataSet+'/'+index+'.txt'
    # f = open(file, 'w')
    # for e in exceptions:
    #     f.write(e+'\n')
    # print(exceptions)
    diff_dict[index] = []
    for fi in range(len(frame_info_list[index])):
        diff_dict[index].append([])
    previous_excpt = 0
    for excpt in exceptions:
        find_excpt = False
        diff = 0
        if previous_excpt==0:
            diff = (int(excpt) - int(previous_excpt)-4)%16 + 7
        else:
            diff = (int(excpt) - int(previous_excpt)-7)%16 + 7
        #diff_dict[index].append(diff)
        for ffi in range(len(frame_info_list[index])):
            frame = frame_info_list[index][ffi]
            if (frame[0]>int(excpt) or (frame[0]<int(excpt) and frame[1]>int(excpt))) and find_excpt==False:
                find_excpt = True
            if find_excpt==True:
                diff_dict[index][ffi].append(diff)
            for f in range(len(frame)):
                if find_excpt==True:
                    #print(diff)
                    frame[f] = frame[f] + diff
        previous_excpt = excpt

for index in frame_info_list:
    frame_info_list[index].sort(key=lambda x:x[0])
after_4_2 = frame_info_list['4_2']
diff_4_2 = diff_dict['4_2']
#print(first_4_2)
for iii in range(len(first_4_2)):
    print(str(first_4_2[iii][0])+' '+str(first_4_2[iii][1])+' '+str(after_4_2[iii][0])+' '+str(after_4_2[iii][1]))
#print(diff_dict['4_2'])

total_recall = 0
count = len(frame_info_list)
for index in frame_info_list:
    final,types = get_final(dataSet, index)
    # print(final)
    # print(len(final))
    # print(len(frame_info_list[index]))
    recall = get_recall(final,types,frame_info_list[index],index)
    get_shortest(final,types,frame_info_list[index],index)
    print(recall)
    total_recall = total_recall + recall
print('average: ', total_recall/count)