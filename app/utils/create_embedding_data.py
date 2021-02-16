import face_recognition
from PIL import Image,ImageDraw


import pymysql
import base64
import json
import time

import numpy as np

import os
from sshtunnel import SSHTunnelForwarder

# from app.FA.face_attribute import get_FA_model,FA_detect



SSH_PWD = base64.b64decode("MTMwNzEzMDc=").decode()
DB_PWD = MYSQL_PWD = base64.b64decode("MTIzNDU2").decode()
path = "/home/czd-2019/Datasets/Models_pic_dataset/the_run_way"

# model = get_FA_model("/home/czd-2019/Projects/flask-demo/flask_demo/face_attribute_net/test.pth")

print(os.listdir(path))

file_name = os.listdir(path)
print(len(file_name))

total_encodings = []
total_name=[]
total_pic_path=[]

total_info = {}

count = 0
for fn in file_name:
    count+=1
    real_path = os.path.join(path,fn)



    image = face_recognition.load_image_file(real_path)
    face_locations = face_recognition.face_locations(image,model="cnn",number_of_times_to_upsample=1)


    if len(face_locations)==0:
        # 放大一倍再检测一次，防止
        face_locations = face_recognition.face_locations(image,
                                                         model="cnn",
                                                         number_of_times_to_upsample=2)
        if len(face_locations)==0:
            print("{%s}. No face detected."%(real_path))
            continue
        elif len(face_locations)>1:
            print("{%s}. More than 1 face detected." % (real_path))
            continue
    elif len(face_locations)>1:
        print("{%s}. More than 1 face detected."%(real_path))
        continue

    # FA_result = FA_detect(model,real_path)
    # print(FA_result)
    # # todo: face attribute into DATABASE.
    #
    # print(face_locations)
    # exit(0)


    encoding = face_recognition.face_encodings(image,face_locations,model="large")
    for i in range(len(face_locations)):
        if encoding[i].size != 128:
            print("encoding error!")
            continue
        total_encodings.append(encoding[i].tolist())
        total_name.append(fn.replace('.jpg',''))
        total_pic_path.append(real_path)

    print(count)
print(len(total_encodings))

with SSHTunnelForwarder(
        ("10.128.24.196", 22),
        ssh_username="czd-2019",
        # ssh_pkey="/xxx/id_rsa",
        ssh_password=SSH_PWD,
        remote_bind_address=('127.0.0.1', 3306),
        # local_bind_address=('0.0.0.0', 10022)
) as tunnel:
    conn = pymysql.connect(
        host="127.0.0.1",
        user="user_c",
        password=DB_PWD,
        database="PROJECT_MODEL"
    )

    cursor = conn.cursor()


    for [n,e],p in zip(list(zip(total_name,total_encodings)),total_pic_path):
        e_json = json.dumps(e)

        t1 = time.time()
        sql = """
        INSERT INTO Tbl_model (name,face_encoding,pic_path,sex,mail) VALUES(%s,%s,%s,%s,%s)
        """
        cursor.execute(sql, (n, e_json, p,0,'test@mail.com'))
        conn.commit()
        t2 = time.time()
        print("cost:{%.3f}"%(t2-t1))
