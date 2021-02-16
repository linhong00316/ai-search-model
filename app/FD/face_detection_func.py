import face_recognition
import numpy as np
import time

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import BaseQuery
from app.Database.db_orm import TblModel




def calFaceDistance(face_encodings,face_to_compare):
    '''
    计算face之间的欧氏距离
    :param face_encodings: 数据库中的face encodings.
    :param face_to_compare: 输入的用于比较的face encoding.
    :return: distance
    '''

    print(face_encodings.shape)

    if len(face_encodings) == 0:
        return np.empty((0))

    return np.linalg.norm(face_encodings - face_to_compare, axis=1)


def faceEncodingPipeline(real_path):
    '''
    正常的人脸检测与编码
    :param real_path:
    :return:
    '''
    start = time.time()
    image = face_recognition.load_image_file(real_path)
    face_locations = face_recognition.face_locations(image,model="cnn",number_of_times_to_upsample=1)

    if len(face_locations)==0:
        face_locations = face_recognition.face_locations(image,
                                                         model="cnn",
                                                         number_of_times_to_upsample=2)
        if len(face_locations)==0:
            print("{%s}. No face detected."%(real_path))
        elif len(face_locations)>1:
            print("{%s}. More than 1 face detected." % (real_path))
    elif len(face_locations)>1:
        print("{%s}. More than 1 face detected."%(real_path))

    encoding = face_recognition.face_encodings(image,face_locations,model="large")
    print("[TIME COST] faceEncodingPipeline cost : "+str(time.time()-start))
    return encoding


def getTop6FaceComparision(uplaod_encoding):
    '''
    获取
    :param uplaod_encoding: 上传的图片的encoding
    :return: dict of top 6 models
    '''
    print("------- [Face Comparision Info] ---------")
    total_encoding = TblModel.query.all()
    # print(total_encoding[0].encoding)
    print("nums of encoding in db: "+str(len(total_encoding)))
    encodings = []
    distances = []
    ids = []

    for i in range(len(total_encoding)):
        encodings.append(total_encoding[i].face_encoding)
        ids.append(total_encoding[i].id_model)

    distances = calFaceDistance(np.array(encodings),np.array(uplaod_encoding))
    # print(ids)


    # print(distances.tolist())
    # print(len(distances))
    # temp = [zip(ids,distances)]

    # Return the index of the list of sorted distances.
    index_sorted = np.argsort(distances)
    # print(ind)

    top6Distances=[]
    top6Id = []
    temp =[]
    for i in range(6):
        # get top-6's index.
        temp.append(index_sorted[i])
        # save top-6's distances.
        top6Distances.append(distances[index_sorted[i]])



    top6Id = [ids[i] for i in temp]
    print(top6Id)
    print(top6Distances)

    top6Models = []
    # # !此查询方法没有按照给定的id list返回信息,而是重新按id从小到大进行排序.
    # top6Models = EncodingTable.query.filter(EncodingTable.id.in_(top6Index)).all()
    for i in top6Id:
        top6Models.append(TblModel.query.get(i))

    print(top6Models)
    print([i.name for i in top6Models])
    print("------- [Face Comparision Info] ---------")
    top6ModelsInfo = {}

    count = 0
    for i in top6Models:
        # temp_dict = {
        #     'name':i.name,
        #     'id':i.id,
        #     'pic_path':i.pic_path,
        #     'attr_encoding':i.attr_encoding,
        #     'img_stream':"",
        # }
        top6ModelsInfo[count] = i.get_dict().copy()
        count+=1

    return top6ModelsInfo