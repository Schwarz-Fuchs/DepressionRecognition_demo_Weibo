host = 'm.weibo.cn'
base_url = 'https://%s/api/container/getIndex?' % host
user_agent = 'User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1 wechatdevtools/0.7.0 MicroMessenger/6.3.9 Language/zh_CN webview/0'#这里的user_agent是网上找的
#设置基本host参数

import requests
import urllib
import time
import os
from tqdm import tqdm
from urllib.parse import urlencode
from pyquery import PyQuery as pq
import datetime
import pandas as pd


def timestr_standard(time_str):
    #转换标准时间格式
    now_time = datetime.datetime.now()
    time_standard='null'
    if time_str.endswith('分钟前') or time_str.endswith('小时前') or time_str == '刚刚':
        #strptime是把字符串转换为时间类。strftime是把时间转换为字符串
        time_standard = datetime.datetime.strftime(now_time.date(),'%Y-%m-%d')
    elif time_str.startswith('昨天'):
        time_standard = datetime.datetime.strftime((now_time - datetime.timedelta(days = 1)).date(),'%Y-%m-%d')
    elif time_str.startswith('0') or time_str.startswith('1'):
        time_standard = str(now_time.year) + '-' + time_str
    elif time_str.startswith('20'):
        time_standard = time_str
    return time_standard

def get_single_page(page,user_id):
    #访问id所在url
    target_header = {
        'Host': host,
        'Referer': 'https://m.weibo.cn/u/%s' % user_id,
        'User-Agent': user_agent
    }
    params = {
        'type': 'uid',
        'value': user_id,
        'containerid': int('107603' + user_id),#containerid就是微博用户id前面加上107603
        'page': page
    }
    url = base_url + urlencode(params)
    try:
        response = requests.get(url, headers=target_header)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError as e:
        print('抓取错误', e.args)

def download_pics(pic_url,pic_name,pic_filebagPath):
    #图片保存（可选）
    pic_filePath = pic_filebagPath + '\\'
    try:
        if pic_url.endswith('.jpg'):#保存jpg图片
            f = open(pic_filePath + str(pic_name)+".jpg", 'wb')
        if pic_url.endswith('.gif'):#保存gif图片
            f = open(pic_filePath + str(pic_name)+".gif", 'wb')
        f.write((urllib.request.urlopen(pic_url)).read())
        f.close()
    except Exception as e:
        print(pic_name+" error",e)
    time.sleep(0.1)

def analysis_page(json,pic_filebagPath,base_data,pic_choice):
    #获取原始信息内容
    items = json.get('data').get('cards')
    for item in items:
        item = item.get('mblog')
        if item:
            ori_content=1
            if item.get('retweeted_status')!=None:
                ori_content=0
            data = {
                'id':item.get('user').get('id'),#用户id
                'name': item.get('user').get('screen_name'),  # 用户名
                'gender': item.get('user').get('gender'),  # 用户性别
                'followers_count':item.get('user').get('followers_count'),  # 用户粉丝数
                'follow_count':item.get('user').get('follow_count'),  # 用户关注数
                'blog_count':item.get('user').get('statuses_count'),  # 用户发博量
                'text': pq(item.get("text")).text(),  # 微博文本内容
                'attitudes': item.get('attitudes_count'),#点赞数
                'comments': item.get('comments_count'),#评论数
                'reposts': item.get('reposts_count'),#转发数
                'created_at': item.get('created_at'),  # 微博创建日期
                'content_auth':ori_content#原创性
            }
            base_data[len(base_data)] = data#把得到的数据字典存入总字典
            if pic_choice == 'y':#如果选择保存图片
                pics = item.get('pics')
                if pics:
                    for pic in pics:
                        picture_url = pic.get('large').get('url')#得到原图地址
                        pid = pic.get('pid')#图片id
                        pic_name = timestr_standard(data['created_at']) + '_' + pid[25:]#构建保存图片文件名，timestr_standard是一个把微博的created_at字符串转换为‘XXXX-XX-XX’形式日期的一个函数
                        download_pics(picture_url,pic_name,pic_filebagPath)#下载原图

def auto_get(user_id):
    #摘取'cards'内有价值内容
    base_data = {}
    page = 20   #获取20*10文本内容
    pic_choice = "n" #存储图片? y/n
    time_start = time.time()
    try:
        json = get_single_page(1,user_id)
        screen_name = json.get('data').get('cards')[0].get('mblog').get('user').get('screen_name')  # 博主昵称
        total = json.get('data').get('cardlistInfo').get('total')  # 博主微博总条数
        if pic_choice == 'y':  # 如果选择保存图片，则分配图片保存路径
            pic_filebagPath = 'C:/Users/surface/Desktop/final project/codes/pictures'
            os.makedirs(pic_filebagPath)  # 建立文件夹
        else:
            pic_filebagPath = None  # 选择不保存文件夹则不分配路径
        if page == 'all':  # 寻找总条数
            page = total // 10
            while get_single_page(page,user_id).get('ok') == 1:
                page = page + 1
            print('总微博条数：%s' % total)
        page = int(page) + 1
        for page in tqdm(range(1, page)):  # 抓取数据
            json = get_single_page(page,user_id)
            analysis_page(json, pic_filebagPath,base_data,pic_choice)
    except Exception as e:
        print('error:', e)
    finally:
        return base_data

def set_new_df():
    dataframe = pd.DataFrame(columns=["id","name","gender","followers_count","follow_count","blog_count",
                                      "created_at", "text", "attitudes", "comments", "reposts","content_auth"])
    return dataframe

def df_insert(dic,dataframe):
    dic_len=len(dic)
    for i in range(dic_len):
       total_rows = len(dataframe)
       dataframe.loc[total_rows+1]=[str(dic[i]["id"]),str(dic[i]["name"]),str(dic[i]["gender"]),str(dic[i]["followers_count"]),str(dic[i]["follow_count"]),str(dic[i]["blog_count"]),
                                    str(dic[i]["created_at"]),str(dic[i]["text"]),str(dic[i]["attitudes"]),str(dic[i]["comments"]),str(dic[i]["reposts"]),str(dic[i]["content_auth"])]
    return dataframe

def auto_get_from_IDlist(IDlist,filepath):
    #uidlist批量抓取
    df=set_new_df()
    for id in IDlist:
        basedata=auto_get(id)
        df_insert(basedata, df)

    df.to_csv(filepath)

def csv_to_list(filepath):
    file=open(filepath,'r',encoding="gbk")# 读取以utf-8
    context = file.read() # 读取成str
    list_result=context.split("\n")#  以回车符\n分割成单独的行
    length=len(list_result)
    for i in range(length):
        list_result[i]=list_result[i].split(",")
    ID_list=[]
    for i in range(len(list_result)-1):
        if list_result[i][1]!="0" or "":
            ID_list.append(list_result[i][1])
    file.close()
    return  ID_list



if  __name__  == "__main__":
    ID_list=csv_to_list("C:/Users/surface/Desktop/final project/codes/the whole process/normal_UID.csv")
    #ID_list_depressed|not depressed
    #['7330062278', '6204349469', '7521658968', '5452767390', '7468349210', '7341052951', '5512534511', '6788739517', '7303712245', '6123256207', '3097909471', '6650895759', '5762513867', '6434954429', '5941084435', '7488778571', '7277514987', '2378720564', '1920763034', '7475269167', '7520094992', '2234832150', '3481268501', '7224317908', '7502646946', '7322770089', '5353169287', '6043357404', '7473465630', '6382605200', '5201002889', '5647152761', '6313648029', '7387236005', '5488900007', '7555942587', '5663684576', '7334175774', '5100749033', '6331215268', '5204084368', '6586588405', '5846075574', '5227154049', '7527952385', '5712817902', '6891258938', '1453134362', '2511997264', '2692828184', '3563350211', '7410575052', '6140361747', '5665305725', '5224215063', '6342861058', '5790675878', '5417496826', '5216412447', '5529746863', '6928383281', '2697866762', '6034319265', '2281189251', '2664942675', '7483289462', '6030634334', '6425012858', '5887880870', '7529001704', '5797969686', '5091475547', '6306531714', '6637915010', '6305368758', '5181880868', '6063401113', '7270782054', '1935042221', '6573070974', '5548616793', '3984270672', '6184964778', '6084516954', '7516257148', '5456863115', '5976157724', '6550098769', '6775570770', '6160951523', '3806022623', '7282836665', '5307191255', '5848957549', '1868975947', '6064526626', '6416499785', '1215048895', '6929626085', '7506061230', '6460161828', '5619062345', '6334529425', '6467824291', '5189229809', '5614428267', '7305108091', '5525000203', '6148309926', '6174904624', '5509229386', '5589807083', '6566887841', '1910808715', '7493116136', '2240439863', '6408774615', '5657992540', '5685479292', '5690212563', '5626317242', '5504627787', '5531608174', '5091693881', '6388320196', '5835980419', '5504325746', '7310919151', '5625821367', '6325806586', '6508362396', '7393887129', '7416556708', '2394022987', '5590631900', '5604393971', '6185404771', '2713798575', '6316319691', '6638726357', '1941166083', '1851627917', '5876331106', '5949187667', '5667086132', '5627814675', '6931461680', '2205774451', '7456749481', '7267044074', '2376563655', '5700488637', '7443347697', '3225401030', '5510980073', '6301321064', '7402756348', '5835921974', '5774951759', '2206990423', '5761068539', '5241587483', '6537198787', '5949018379', '6144327879', '5878096166', '6168539499', '5844474777', '7444324385', '5027533476', '7312706915', '1917048154', '5834408741', '7305940517', '3992947759', '5994874145', '2078562107', '7438939930', '5828928902', '6377598593', '1776132110', '2653974432', '6883856940', '7000697557', '7339604319', '5109961837', '6174824441', '5684637881', '7010377669', '5362764947', '6257139949', '7186004359']highscjool
    #['7380380328', '6646137226', '2423195302', '7473183047', '5760277420', '7513421404', '7531209788', '5621446799', '5208129552', '3815518374', '7479962615', '6620427966', '7519937333', '2965522933', '5264805456', '6484132337', '5720178591', '5861164393', '6077274180', '6324377531', '6331546832', '6875133202', '7553078981', '6647447051', '5512041304', '1895317914', '7197235515', '5372320735', '5609066712', '6604221275', '6520432580', '5299447516', '7276181309', '7444272489', '6136539239', '6491665975', '1824772220', '6505947457', '7402830136', '7035075040', '6088313827', '5819332943', '6576878127', '1853750652', '6619782610', '5514911320', '7074503852', '6873258807', '7166314763', '6562563288', '6480000323', '6997315444', '6445424239', '5559665559', '7202552293', '7305498537', '6481033543', '7270753619', '6450830825', '6483534068', '6882841677', '6564639621', '2517227834', '7546819414', '6989973336', '6863419577', '5880561424', '7476525338', '5722955558', '6525407598', '6120426688', '6378570822', '3171035483', '3138370217', '7335835985', '5217495158', '6444646488', '5863396613', '7492627095', '5160133000', '5655598016', '5702618807', '7146490731', '6605253596', '7288789452', '6816216423', '3732929905', '7313631207', '5837855488', '5526780361', '3168644792', '5304237682', '5805368370', '7396127035', '3266625661', '7373923561', '7529211185', '7489114807', '7363180342', '7533290963', '5457816314', '5723974228', '5339534188', '7002479556', '7404162633', '7385241672', '5602605885', '7186004359', '6282887753', '6001116859', '2250484490', '2421538634', '5113642196', '7356594967', '5599932745', '6330406235', '5626278922', '6422197302', '6849214337', '5567220572', '5771416974', '6319548129', '5720090533', '7562367166', '7439546981', '6399009551', '7404770343', '7333227568', '6178731171', '1784043610', '7455954840', '6491813311', '7448938978', '7484780710', '3787006023', '7402247989', '6361609650', '3200162187', '7341554397', '6164143093', '3539197462', '3956697070', '7475081970', '6994101241', '7355062313', '6187088610', '5696215196', '7053063595', '6520566309', '7414037628', '3678844687', '5759947327', '6484788760', '7400863912', '5761048694', '5629271631', '3284055400', '7508538339', '6105934196', '6573663873', '6608822737', '7427793841', '7400895793', '5629767216', '1841980502', '7312857400', '7341491052', '6346069060', '6352595180', '7313410096', '6935123770', '3199544937', '6058491329', '6338237780', '6589028971', '3155112052', '3916056328', '7476590575', '5215051559', '6453028367', '7562647311', '7282561567', '7547339776', '7332137108', '6965481875', '7448125435', '6614215646', '7182477977', '5936461909', '1851377310', '6986739352', '7398372113', '6539554921', '2173850307', '7131823344', '7073476067', '5916491911', '6864114703', '6468572123', '5704690152', '7381364774', '6442731313', '7521703993', '7162403020', '7517158882']depressioni
    auto_get_from_IDlist(ID_list,"normal_labled_origin.csv")


