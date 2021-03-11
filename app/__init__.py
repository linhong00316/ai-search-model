from flask import Flask
from flask import Response, request, render_template, jsonify, abort, redirect, url_for, send_file
from config import config

# import flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy


from sqlalchemy import select

import os
import time
import io
import base64
from PIL import Image
import json


# app创建，建议后面优化时写成一个函数，返回创建的app实例

app = Flask(__name__, instance_relative_config=True)
app.config.from_object(config['development'])

db = SQLAlchemy(app)

import app.FD.face_detection_func as FD
from app.Database.db_orm import TblModel,TblBusiness
from app.FA.face_attribute_func import get_FA_model, FA_detect
from app.FD.face_detection_func import calFaceDistance,faceEncodingPipeline,getTop6FaceComparision,\
    getStyleFromFaceComparision_minimum,getStyleFromFaceComparision_mean



# db.session.query(EncodingTable).filter(EncodingTable.id==1582)
# name = ModelInfo.query.filter_by(name='pbt')
# # get num of SELECT result.
# print(name.count())

# print(name.id)
# print(name.pic_path)
# print(name.sex)
# print(name.black_hair)

# new_name = ModelInfo('pbt', 0, '/pic/pbt.jpg', 1)
# db.session.add(new_name)
# db.session.commit()

test_encoding = [-0.08829611539840698, 0.09958075731992722, 0.1182040125131607, -0.15085460245609283, -0.15787950158119202, 0.014677738770842552, -0.01921466365456581, -0.04888387769460678, 0.24283704161643985, -0.18055638670921328, 0.06763090938329697, 0.07459057122468948, -0.13392044603824615, 0.12628409266471863, 0.011102356016635897, 0.14059388637542725, -0.22655871510505676, -0.17900581657886505, 0.021747831255197525, -0.05553121864795685, 0.028109688311815265, 0.06164596602320671, 0.02634439989924431, 0.08188078552484512, -0.07881488651037216, -0.35969582200050354, -0.1718629151582718, -0.005975566804409027, 0.07632409781217575, -0.07471700757741928, 0.025209324434399605, 0.056233130395412445, -0.180342435836792, -0.010113714262843132, 0.03609016537666321, 0.06502948701381683, -0.07845202088356018, -0.09190592169761658, 0.20666056871414185, 0.041258350014686584, -0.2474856823682785, -0.027427077293395996, 0.06099234148859978, 0.2759360074996948, 0.21207162737846377, 0.05565915256738663, 0.03509844094514847, -0.05270559713244438, 0.11236845701932908, -0.24647197127342224, 0.10510144382715224, 0.17792704701423645, 0.00751110352575779, 0.09066973626613616, 0.05913996323943138, -0.1402711570262909, 0.05538780987262726, 0.11816512048244476, -0.1572016477584839, 0.1208646520972252, 0.12205488979816435, -0.15669089555740356, 0.08445987105369568, -0.0014346502721309662, 0.19463104009628296, 0.06656844913959503, -0.0918370485305786, -0.23021642863750455, 0.1869729906320572, -0.1955962032079697, -0.0932210013270378, 0.07328861951828003, -0.13903671503067017, -0.1753945350646973, -0.2733132243156433, 0.008122360333800316, 0.3848790228366852, 0.22561115026474, -0.05760357528924942, 0.06330068409442902, -0.06217947602272034, -0.010949619114398956, 0.0712517499923706, 0.2351550459861755, -0.03424876928329468, -0.017613008618354797, -0.07102178037166595, 0.05134370177984238, 0.2190365195274353, 0.03772537410259247, -0.10446196794509888, 0.23420009016990664, 0.015710867941379547, 0.04836801812052727, -0.002425294369459152, 0.12645769119262695, -0.11256013065576552, 0.004965882748365402, -0.18442142009735107, -0.02223782241344452, -0.05361485481262207, 0.025534117594361305, -0.042724739760160446, 0.25512784719467163, -0.18707583844661713, 0.22375036776065824, -0.08638548105955124, -0.024068543687462807, -0.10942370444536208, 0.0548151358962059, -0.10543091595172882, -0.06259997189044952, 0.10424135625362396, -0.23970258235931396, 0.13721618056297302, 0.26186567544937134, -0.011225455440580843, 0.14285007119178772, 0.050113122910261154, 0.06939753144979477, 0.06556327641010284, -0.0924677476286888, -0.1888091117143631, -0.047685541212558746, 0.02231393381953239, -0.014591582119464874, 0.04412173479795456, 0.07773531973361969]


test_user = {'name': 'test_user',
             'sex': 0,
             'pic_path': '/pic/test.jpg',
             'black_hair': 0}

business_intro_text = {
    "adidas":"adidas（阿迪达斯）创办于1949年，是德国运动用品制造商阿迪达斯AG成员公司。以其创办人阿道夫·阿迪·达斯勒（Adolf Adi Dassler）命名，1920年在黑措根奥拉赫开始生产鞋类产品。1949年8月18日以adidas AG名字登记。阿迪达斯原本由两兄弟共同开设，在分道扬镳后，阿道夫的哥哥鲁道夫·达斯勒 （Rudolf Dassler）开设了运动品牌puma。其经典广告语：“没有不可能”（Nothing is impossible）。2011年3月，斥资1.6亿欧元启用全新口号——adidas is all in（全倾全力）。",
    "uniqlo":"优衣库（英文名称：UNIQLO，日文假名发音：ユニクロ），为日本迅销公司的核心品牌，建立于1984年，当年是一家销售西服的小服装店，现在已经是家喻户晓的品牌。优衣库(Uniqlo) 的内在涵义是指通过摒弃了不必要装潢装饰的仓储型店铺，采用超市型的自助购物方式，以合理可信的价格提供顾客希望的商品。现任董事长兼总经理柳井正，在日本首次引进了大卖场式的服装销售方式，通过独特的商品策划、开发和销售体系来实现店铺运作的低成本化，由此引发了优衣库的热卖潮。在2018世界品牌500强排行榜中，优衣库排名第168位。",
    "chanel":"香奈儿（Chanel）是法国奢侈品品牌，创始人是Coco Chanel（原名是Gabrielle Bonheur Chanel ，中文名是加布里埃·香奈儿），该品牌于1910年在法国创立。该品牌产品种类繁多，有服装、珠宝饰品及其配件、化妆品、护肤品、香水等。该品牌的时装设计有高雅、简洁、精美的风格，在20世纪40年代就成功地将“五花大绑”的女装推向简单、舒适的设计。2018年12月18日，世界品牌实验室编制的《2018世界品牌500强》揭晓，香奈儿位列44位。2019年10月，Interbrand发布的全球品牌百强榜排名22",
    "hm":"H&M是Erling Persson于1947年在瑞典创立的服饰品牌。如今，H&M在全世界1500 多个专卖店销售服装、配饰与化妆品，H&M横扫欧洲街头，得力于公司兼顾流行、品质及价格的三合一哲学，以及积极扩张的政策。位于瑞典市Stora Gatan大街的老H&M店是世界上第一家H&M专卖店。H&M品牌名是由“Hennes” （瑞典语中“她”的意思） 女装与“Mauritz”男装品牌合并，各取第一个字母而成“H&M”。",
    "longines":"浪琴（LONGINES）于1832年在瑞士索伊米亚创立，拥有逾180多年的悠久历史与精湛工艺，在运动计时领域亦拥有显赫传统与卓越经验。以飞翼沙漏为标志的浪琴表以优雅著称于世，作为全球领先钟表制造商斯沃琪集团旗下的著名品牌，浪琴表已遍布世界150多个国家。浪琴作为世界锦标赛的计时器及国际联合会的合作伙伴，浪琴表品牌以其优雅的钟表享誉全球，亦是世界领先钟表制造商 Swatch Group S.A. 公司的旗下一员。2018年12月，世界品牌实验室发布《2018世界品牌500强》榜单，浪琴排名第324。",
    "muji":"1980年無印良品诞生于日本，主推服装、生活杂货、食品等各类优质商品。無印良品是指“没有名字的优良商品”。無印良品自始至终坚持3个基本原则：1．原材料的选择； 2．工序的改善；3．包装的简化。从合理的生产工序中诞生的商品非常简洁，但就风格而言却并非极简主义。就如“空的容器”一样。正因为其单纯、空白，所以那里才诞生了能够容纳所有人思想的自由性。",
    "nike":"NIKE公司总部位于美国俄勒冈州波特兰市。公司生产的体育用品包罗万象，例如服装，鞋类，运动器材等。NIKE是全球著名的体育运动品牌，英文原意指希腊胜利女神，中文译为耐克。耐克商标图案是个小钩子。耐克一直将激励全世界的每一位运动员并为其献上最好的产品视为光荣的任务。耐克首创的气垫技术给体育界带来了一场革命。运用这项技术制造出的运动鞋可以很好地保护运动员的膝盖.在其在作剧烈运动落地时减小对膝盖的影响。",
    "tiffany":"Tiffany & Co.（蒂芙尼），珠宝界的皇后，以钻石和珠宝腕表著称。1837年诞生于美国纽约。Tiffany自1837年成立以来，一直将设计富有惊世之美的原创作品视为宗旨。事实证明，Tiffany珠宝不仅能将恋人的心声娓娓道来，其独创的银器、文具和餐桌用具更是令人心驰神往。“经典设计”是Tiffany作品的定义，也就是说，每件令人惊叹的Tiffany杰作都可以世代相传。",
    "zara":"ZARA 是1975年设立于西班牙隶属Inditex集团（股票代码ITX）旗下的一个子公司，既是服装品牌也是专营ZARA品牌服装的连锁零售品牌。ZARA是全球排名第三、西班牙排名第一的服装商，在87个国家内设立超过两千多家的服装连锁店。ZARA深受全球时尚青年的喜爱，设计师品牌的优异设计价格却更为低廉，简单来说就是让平民拥抱High Fashion。Inditex是西班牙排名第一，超越了美国的GAP、瑞典的H&M、丹麦的KM成为全球排名第一的服装零售集团。"
}

# 创建实例结束


# app.config['IS_FA_NET_USED'] = True


# todo GPU初始化

if app.config['IS_FA_NET_USED']:
    try:
        FA_model = get_FA_model("flask_demo/face_attribute_net/test.pth")
        print("Face attribute net init success!")
    except OSError:
        print("[ERROR]: Face attribute net init error!")
        FA_model=None
else:
    FA_model = None
    print("[WARNNING]: Face attribute net do not be selected!")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/ajax_test',methods=['GET', 'POST'])
def ajax_test():
    if request.method == 'GET':
        return render_template('ajax_test.html', flag=0)
    elif request.method == 'POST':
        result = request.form.get('c1')
        print(result)
        result = request.form.get('c2')
        print(result)
        result = request.files.get('img')
        print(result)
        upload_path = "app/static/upload_img/"+str(int(time.time())) + ".jpg"
        result.save(upload_path)
        # t = request.get_json()
        # print(t)
        # name = request.form.get('data1')
        # num = request.form.get('data2')
        # print(name)
        # print(num)
        return jsonify(name="name",num=123123)


@app.route('/business_test', methods=['GET','POST'])
def business_test():
    # res = TblBusiness.query.filter_by(business_name='nike').all()
    # print(res[0])
    # print(len(res))
    # print(res[0].attribute_encodings)
    res = TblBusiness.query.filter_by(id_business=1002).all()
    print(res)
    print(TblBusiness.query.filter_by(id_business=1002).first())
    best = FD.getStyleFromFaceComparision_mean(test_encoding)
    best_2 = FD.getStyleFromFaceComparision_minimum(test_encoding)

    return jsonify(best=best,best_2=best_2)

@app.route('/', endpoint='upload', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index_v2.html', flag=0)
    elif request.method == 'POST':
        print("post")
        # 获取用户上传的图片，保存；并且保留图片流返回给前端显示
        upload_path = "app/static/upload_img/upload_pil_" + str(int(time.time())) + ".jpg"
        fp = request.files.get('img')
        print(fp)
        fp.save(upload_path)

        # img = fp.read()
        # print(img)
        # byte_stream = io.BytesIO(img)
        # print(byte_stream)


        im_pil = Image.open(upload_path)
        print(im_pil.width)
        print(im_pil.height)

        # # The path of upload image.
        # im_pil.save(upload_path)
        imgByteArr = io.BytesIO()
        im_pil.save(imgByteArr,format='JPEG')
        imgByteArr = imgByteArr.getvalue()

        search_mode = request.form.get('search_mode')
        return_num = request.form.get('return_num')
        print(request.form.get('isTest'))
        print("search_mode: "+search_mode)
        print("return_num: "+return_num)

        # Face detection.
        upload_encoding = faceEncodingPipeline(upload_path)
        # todo:确认上传的照片是否有人脸，否则返回提示页面
        print(len(upload_encoding[0]))
        if len(upload_encoding[0])!=128:
            return render_template('404.html')


        output_result_1 = Face_comparision_api(upload_encoding)
        # return jsonify(img_rtn=base64.b64encode(imgByteArr).decode('utf-8'),
        #                top6ModelsInfo = top6ModelsInfo)

        render_1 = render_template('response_top_n_info.html',
                               flag=1,
                               top6ModelsInfo = output_result_1)

        output_result_2 = business_FD_minimum_api(upload_encoding)

        render_2 = render_template('response_result_2.html',
                               flag=1,
                               top6ModelsInfo = output_result_2)

        output_result_3 =  business_FD_mean_api(upload_encoding)
        render_3 = render_template('response_result_3.html',
                                   top3BusinessNames = output_result_3)


        return jsonify(r1=render_1,
                       r2=render_2,
                       r3=render_3)
        # return render_template('response_top_n_info.html',
        #                        flag=1,
        #                        top6ModelsInfo=top6ModelsInfo)
        if search_mode=="1":
            # 与数据库里的encoding比较
            print("Start Face Comparision.")
            top6ModelsInfo = Face_comparision_api(upload_encoding)
            return render_template('Index.html', flag=1,
                                   img_rtn=base64.b64encode(imgByteArr).decode('utf-8'),
                                   top6ModelsInfo = top6ModelsInfo
                                   )
        elif search_mode=="2" and (app.config['IS_FA_NET_USED'] == True):
            # Face attribute detection.
            attr_result = FA_detect_api(upload_path)
            print("result jsonify print:")
            print(attr_result)
            return render_template('Index.html', flag=1,
                                   attr_result=attr_result,
                                   img_rtn=base64.b64encode(imgByteArr).decode('utf-8'),
                                   )
        else:
            return render_template('404.html')

# @app.route('/pytorch', methods=['GET', 'POST'])
# def net_try():
#     model = get_FA_model("flask_demo/face_attribute_net/test.pth")
#     final_result = FA_detect(model=model,
#                              pic_path="/home/czd-2019/Projects/face-attribute-prediction/self_network/model_pic_test/0001.jpg")
#
#     return jsonify(final_result)

@app.route('/db_test',methods=['GET', 'POST'])
def db_try():
    result = TblModel.query.filter_by(id_model=1001)
    print(result.count())
    encoding = result[0]
    print(encoding)
    return jsonify(encoding.get_dict())

@app.route('/vue_test',methods=['GET', 'POST'])
def vue_test():
    return render_template('vue_test.html')


def FA_detect_api(pic_path):
    final_result = FA_detect(model=FA_model,
                             pic_path=pic_path)
    result_json = {'0':"",
                   '1':"",
                   '2':"",
                   '3':"",
                   '4':"",
                   '5':""}
    for i in range(len(final_result)):
        result_json[str(i)] = final_result[i]

    # print(result_json)

    # print(final_result)
    return result_json



def Face_comparision_api(upload_encoding):
    top6_model_info = getTop6FaceComparision(upload_encoding)
    # 将服务器端的图片转为img stream，准备送给前端
    for i in range(6):
        # print(top6ModelInfo[i])
        fp = open(top6_model_info[i]['pic_path'],'rb')
        img_stream = fp.read()
        img_coded = base64.b64encode(img_stream).decode('utf-8')
        top6_model_info[i]['img_stream'] = img_coded

    # return jsonify(top6ModelInfo)
    return top6_model_info


def business_FD_minimum_api(upload_encoding):
    top6_model_info = getStyleFromFaceComparision_minimum(upload_encoding)
    for i in range(6):
        fp = open(top6_model_info[i]['pic_path'],'rb')
        img_stream = fp.read()
        img_coded = base64.b64encode(img_stream).decode('utf-8')
        top6_model_info[i]['img_stream'] = img_coded

    return top6_model_info


def business_FD_mean_api(upload_encoding):
    list_top3_business_names = getStyleFromFaceComparision_mean(upload_encoding)
    dict_result={}
    for n in range(len(list_top3_business_names)):
        dict_result[n] = {
            "name":list_top3_business_names[n],
            "intro":business_intro_text[list_top3_business_names[n]]
        }

    return dict_result



@app.route('/hello', methods=['GET', 'POST'])
def hello_world():
    # return 'Hello Flask!'
    return render_template('select_info.html', new_user=new_name)


@app.route('/profile', methods=['GET', 'POST'])
def get_profile():
    profile = {"name": "czdpzc",
               "number": "123"}
    if request.method == "GET":
        return profile
    elif request.method == 'POST':
        post_profile = request.json
        post_name = post_profile["name"]
        post_num = post_profile["number"]

        # print(post_name)
        return post_name + " " + post_num


@app.route('/upload_image', methods=["POST"])
def get_image():
    # print(request.form)
    print(len(request.data))
    print(request.files.__len__())
    received_file = request.files['input_image']
    imageFileName = received_file.filename
    print(imageFileName)

    # if received_file:
    #     received_dirPath = '../resources/received_images'
    #     if not os.path.isdir(received_dirPath):
    #         os.makedirs(received_dirPath)
    #     imageFilePath = os.path.join(received_dirPath, imageFileName)
    #     received_file.save(imageFilePath)
    #     print('image file saved to %s' % imageFilePath)
    #     usedTime = time.time() - startTime
    #     print('接收图片并保存，总共耗时%.2f秒' % usedTime)
    #     startTime = time.time()
    #     result = predict_image(model_loaded, imageFilePath)
    #     result = str(result)
    #     usedTime = time.time() - startTime
    #     print('完成对接收图片的预测，总共耗时%.2f秒' % usedTime)
    #     # return result
    #     return render_template("result.html", result=result)

    return "test"
