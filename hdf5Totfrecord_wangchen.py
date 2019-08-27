import tensorflow as tf
import numpy as np
import os
import h5py
from  snippets import getSnippets
# def splitTensor(tensor):
#     new=[]
#     for i in tensor:
#         for a in np.split(i,4,axis=0):
#             new.append(a)
#     return new
def flatten(l):
    result=[]
    for k in l:
        result+=k
    return result
def writeTotfrecord(ready,actionLabel,startendLabel,Writer):
    print(np.shape(ready))
    #ready =resizeDimenssion(ready,snippetCount)
    features={}
    tensor=np.array(ready)
    # tensor=splitTensor(tensor)
    tensor=np.array(tensor)
    print(np.shape(tensor))
    features['tensor'] = tf.train.Feature(bytes_list=tf.train.BytesList(value=[tensor.tostring()]))
    features['tensor_shape'] = tf.train.Feature(int64_list=tf.train.Int64List(value=tensor.shape))
    features['actionLabel']=tf.train.Feature(int64_list=tf.train.Int64List(value=actionLabel))
    features['startendLabel']=tf.train.Feature(int64_list=tf.train.Int64List(value=startendLabel))
    # math.ceil(length / SCALE_FACTOR)
    tf_features = tf.train.Features(feature= features)
    tf_example = tf.train.Example(features = tf_features)
    tf_serialized = tf_example.SerializeToString()
    Writer.write(tf_serialized)

hdf5Path="./snippet_feature/norm/"
options = tf.python_io.TFRecordOptions(tf.python_io.TFRecordCompressionType.ZLIB)
for filename in os.listdir(hdf5Path):
    if filename[0]==".":
        continue
    print('./wangchen/'+filename.split(".")[0]+".tfrecord")
    trainWriter = tf.python_io.TFRecordWriter('./wangchen/'+filename.split(".")[0]+".tfrecord", options=options)
    print(hdf5Path+filename)
    f = h5py.File(hdf5Path+filename, 'r')
    tensor_key=""
    label_key=""
    for key in f.keys():
        if key[:6] == "tensor":
            tensor_key=key
        elif key[:5] == "label":
            label_key=key
    result=getSnippets(filename.split(".")[0][:-26])  #换成你的get方法 可以得
    result=flatten(result)
    action=[]
    for i in result:
        if i==1:
            action.append(1)
        else:
            action.append(0)
    start_end=[]
    for i in result:
        if i==2 or i==3:
            start_end.append(1)
        else:
            start_end.append(0)
    print(len(result))
    print(len(f[tensor_key][:]))
    assert len(result)==len(f[tensor_key])
    bias_array=[0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95]
    for bias in bias_array:
        print("bias"+str(bias))
        start = bias
        segmetn_count=(len(result)-bias)//100
        for i in range(segmetn_count):
            writeTotfrecord(f[tensor_key][start:start+100],action[start:start+100],start_end[start:start+100],trainWriter)
            start=start+100
    trainWriter.close()