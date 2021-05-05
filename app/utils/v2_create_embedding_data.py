import face_recognition
from PIL import Image,ImageDraw

import torch
import torch.nn as nn
import torch.nn.parallel
import torch.backends.cudnn as cudnn
import torch.distributed as dist
import torch.optim as optim
import torch.multiprocessing as mp
import torch.utils.data
import torch.utils.data.distributed
import torchvision.transforms as transforms
import torchvision.datasets as datasets
import torchvision.models as models

import pymysql
import base64
import json
import time

import numpy as np

import os
from sshtunnel import SSHTunnelForwarder

import PIL.Image as Image
import os
import numpy as np
from app.FA.model_structure import StructureCheck
import time

# from app.FA.face_attribute import get_FA_model,FA_detect



SSH_PWD = base64.b64decode("MTMwNzEzMDc=").decode()
DB_PWD = MYSQL_PWD = base64.b64decode("MTIzNDU2").decode()
path = "/home/czd-2019/Datasets/Models_pic_dataset/the_run_way"

# model = get_FA_model("/home/czd-2019/Projects/flask-demo/flask_demo/face_attribute_net/test.pth")
# --------------------- FA model loading ------------------------
color_map=[2,3,4,5]
style_map=[0,1,6,7,8,9]
model = StructureCheck(isPretrained=False)
ckpt = "/home/czd-2019/Projects/MTL-face-attribute-classification/checkpoint_Jan08_structure_2_fixbugs_fixSAbugs_mid2_mid3_acc9220_epoch59/checkpoint_epoch59.pth"
torch.distributed.init_process_group(backend='nccl',
                                     init_method='tcp://127.0.0.1:10085',
                                     rank=0,
                                     world_size=1)
model.cuda()
model = torch.nn.parallel.DistributedDataParallel(model,device_ids=[0,1])
print("=> loading checkpoint '{}'".format(ckpt))
checkpoint = torch.load(ckpt)
model.module.load_state_dict(checkpoint['model_state_dict'])
# --------------------------------------------------------------

print(os.listdir(path))

file_name = os.listdir(path)
print(len(file_name))

total_encodings = []
total_name=[]
total_pic_path=[]
total_FA_results=[]
total_info = {}

count = 0
for fn in file_name:
    FA_results = {}
    count+=1
    # if count>4:
    #     break
    real_path = os.path.join(path,fn)
    print(real_path)



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



    encoding = face_recognition.face_encodings(image,face_locations,model="large")
    print(encoding[0].size)
    total_encodings.append(encoding[0].tolist())
    total_name.append(fn.replace('.jpg',''))
    total_pic_path.append(real_path)


# FA_result = FA_detect(model,real_path)
# print(FA_result)
# # todo: face attribute into DATABASE.
#
# print(face_locations)
# exit(0)

    # FA part.
    with open(real_path, 'rb') as f:
        img = Image.open(f)
        img = img.convert('RGB')

    print("input image size: [%d,%d]" % (img.size))
    img = img.resize((224, 224), Image.BILINEAR)
    normalize = transforms.Normalize(mean=[0.5, 0.5, 0.5],
                                     std=[0.5, 0.5, 0.5])

    trans = transforms.Compose([
        transforms.ToTensor(),
        normalize,
    ])

    threshold=0.5
    temp_result=[]
    output_after_sigmoid=[]
    model.eval()
    with torch.no_grad():
        input = trans(img).unsqueeze(0)
        output = model(input.cuda())
        print("----------------------------------------------")
        output_after_sigmoid = [torch.sigmoid(i) for i in output]
        # print(output_after_sigmoid)

        for j in range(8):
            for i in output_after_sigmoid[j]:
                pred_result = i > threshold
                pred_result = pred_result.int()
                temp_result.append(pred_result)
        # print(temp_result)

    FA_result_gpu = temp_result.copy()
    # print(FA_result_gpu[0].cpu().numpy())
    print("----------------------------------------------")
    print(len(FA_result_gpu))
    # test = output_after_sigmoid[0].cpu().numpy()
    # print(test)
    # print(test[0].argsort()[0:3])
    # exit()

    need_process=[0,0,0,0,0,0,0,0]

    for index,labels in enumerate(FA_result_gpu):
        if (labels.cpu().tolist().count(1)<=1) and index==0:
            print("Start [Hair] special processing.")
            # 处理无1的hair中的情况，分发色和发型两部分
            hair_color = [v for i, v in enumerate(output_after_sigmoid[index].cpu().numpy()[0]) if (i == 2 or i == 3 or i == 4 or i == 5)]
            # print(hair_color)
            hair_style = [v for i, v in enumerate(output_after_sigmoid[index].cpu().numpy()[0]) if not (i == 2 or i == 3 or i == 4 or i == 5)]

            better_result_color = np.argmax(hair_color)
            better_result_style = np.argmax(hair_style)
            # print(better_result_color)
            # print(better_result_style)

            better_result_color = color_map[better_result_color]
            better_result_style = style_map[better_result_style]
            # print(better_result_color)
            # print(better_result_style)

            # FA_result_words.append(subtasks[index][better_result_color])
            # FA_result_words.append(subtasks[index][better_result_style])

            labels[better_result_color] = 1
            labels[better_result_style]=1

            FA_results[index]=labels.cpu().tolist().copy()

        elif (labels.cpu().tolist().count(1)<=1) and index==7:
            print("Start [Holictic] special processing.")
            # 处理无1的holistic中的情况，取出前三个最大值
            holistic_output = output_after_sigmoid[index].cpu().numpy()[0]
            top3_index_of_holistic = holistic_output.argsort()[0:3]
            for t in top3_index_of_holistic:
                labels[t] = 1

                # FA_result_words.append(subtasks[index][t])
            FA_results[index]=labels.cpu().tolist().copy()

        elif 1 in labels:
            # 处理有1的正常情况
            # for i,l in enumerate(labels):
            #     if l:
            #         FA_result_words.append(subtasks[index][i])


            FA_results[index] = labels.cpu().tolist().copy()
        elif (not 1 in labels) and index==6:
            print("Start [Neck] special processing.")
            FA_results[index] = labels.cpu().tolist().copy()
            # 忽略无1的neck的类别的处理
            continue
        elif index==1:
            # 补充两个额外的eyes属性
            labels_update = labels.cpu().tolist().copy() + [0,0]
            if not 1 in labels :
                print("Start [Eyes] special processing.")
                # 处理无1的eyes中的情况
                output_s = output_after_sigmoid[index].cpu().numpy()[0]
                better_result = np.argmax(output_s)
                if better_result in [0,1,2,3]:
                    # FA_result_words.append(subtasks[index][better_result])
                    labels_update[better_result] = 1
                    FA_results[index]=labels_update
                else:
                    if output_s[better_result] > 1e-1:
                        # 定义为narrowEyes
                        labels_update[better_result]=1
                        FA_results[index] = labels_update
                        # FA_result_words.append(subtasks[index][better_result])
                    elif output_s[better_result] > 1e-3 and output_s[better_result] < 1e-1:
                        # 定义为NormalEyes
                        labels_update[5] = 1
                        FA_results[index] = labels_update
                        # FA_result_words.append(subtasks[index][5])
                    else:
                        # 定义为BigEyes
                        labels_update[6] = 1
                        FA_results[index] = labels_update
                        # FA_result_words.append(subtasks[index][6])
            else:
                FA_results[index] = labels_update
        else:
            # 处理无1的正常情况
            output_s = output_after_sigmoid[index].cpu().numpy()[0]
            better_result = np.argmax(output_s)
            labels[better_result]=1
            FA_results[index] = labels.cpu().tolist().copy()

            # FA_result_words.append(subtasks[index][better_result])
    total_FA_results.append(FA_results)


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


    for [n,fd,fa,p] in list(zip(total_name,total_encodings,total_FA_results,total_pic_path)):
        fd_json = json.dumps(fd)
        fa_json = json.dumps(fa)

        t1 = time.time()
        sql = """
        INSERT INTO Tbl_model_fa (name,face_encoding,pic_path,sex,mail,attribute_encoding) VALUES(%s,%s,%s,%s,%s,%s)
        """
        cursor.execute(sql, (n, fd_json, p,0,'test@mail.com',fa_json))
        conn.commit()
        t2 = time.time()
        print("cost:{%.3f}"%(t2-t1))
