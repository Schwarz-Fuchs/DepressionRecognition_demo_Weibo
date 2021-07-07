import re
import emoji
import pandas as pd
from tqdm import tqdm


def read_csv(csvfile):
    df = pd.read_csv(csvfile)
    return df


def basic_clean(text):
    #筛除无价值内容
    text = text.replace("@ ", "@")  # 统一转发格式
    text = re.sub(r"(回复)?(//)?\s*@\S*?\s*(:| |$)", " ", text)  # 去除正文中的@和回复/转发中的用户名
    text = re.sub(r"(回复)?(//)?\s*@\S*?\s*(:| |$)", " ", text)  # 去除正文中的@和回复/转发中的用户名(针对某些用户的二级@）
    text = re.sub(r"#\S+#", "", text)  # 除去话题内容
    URL_REGEX = re.compile(
        r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))',
        re.IGNORECASE)
    text = re.sub(URL_REGEX, "", text)  # 去除网址
    text = text.replace("转发微博", "")
    text = text.replace("轉發微博", "")
    text = text.replace("分享图片", "")
    text = text.replace("网页链接", "")
    text = text.replace("地址：网页链接", "")
    text = text.replace("Repost", "")
    text = text.replace("repost", "")  # 去除无意义的词语
    text = re.sub(r"\s+", " ", text)  # 合并正文中过多的空格
    text = emoji.demojize(text)  # 表情符重编码
    return text


def chinese_fliter(text):
    r1 = '[a-zA-Z0-9’!"#$%&\'()*+,-./:：;；|<=>?@~（）·①②③⑤④⑥⑦⑧⑨『』「」＜＞<>℃♤♡♢♧♠♥♦♣☀☀♀♂♩♪♫♬*＊✲❈❉，—。?★、…【】《》？“”‘’！[\\]^_`{|}~]+'
    r2 = '\s+'
    text = re.sub(r'[:].*?[:]', "", text)
    text = re.sub(r'[[].*?[]]', "", text)  # 过滤两种表情符号
    text = re.sub(r1, ' ', text)
    text = re.sub(r2, ' ', text)
    return text


def emoji_fliter(text):
    # 筛出emoji
    p1 = re.compile(r'[:].*?[:]', re.S)
    p2 = re.compile(r'[[].*?[]]', re.S)
    emoji_list1 = re.findall(p1, text)
    emoji_list2 = re.findall(p2, text)
    emoji_list = emoji_list1 + emoji_list2
    return ','.join(emoji_list)


def repost_clean(df):
    # 筛去无价值转发
    for i in tqdm(range(len(df) - 1)):
        origin_text = df.loc[i, "text"]
        if str(origin_text) != "nan" or "" or None or ' ':
            origin_text_list = list(origin_text)
            if origin_text_list[0] == '【':
                df.loc[i, "text"] = '1145141919810'
        else:
            continue
    return df


def df_clean(df, column):
    print("cleaning text……")
    for i in tqdm(range(len(df))):
        origin_text = df.loc[i, column]
        if str(origin_text) != "nan" or "" or None:
            df.loc[i, column] = basic_clean(origin_text)
        else:
            continue
    return df


def df_clean_nan(df):
    print("cleaning NAN data……")
    df["text"] = df["text"].fillna('1145141919810')
    for i in tqdm(range(len(df))):
        origin_text = df.loc[i, 'text']
        if str(origin_text) == ' ':
            df.loc[i, 'text'] ='1145141919810'
    empty_list = df[(df.text == '1145141919810')].index.tolist()
    df = df.drop(empty_list)
    return df


def clean_dataframe_generate(df):
    for i in tqdm(range(len(df))):
        origin_text = df.loc[i, "text"]
        if str(origin_text) != "nan" or "" or None:
            df.loc[i, "chinese_only_text"] = chinese_fliter(origin_text)
            df.loc[i, "emoji"] = emoji_fliter(origin_text)
        else:
            continue
    return df

def emoji_sum_up(df):
    emoji_list_all=[]
    sum=0
    for i in range(len(df)):
        emoji_set=str(df.loc[i,'emoji'])
        if emoji_set!='' and emoji_set!=' 'and emoji_set!='nan':
            emoji_list=emoji_set.split(",")
            sum = sum+1
            for emojis in emoji_list:
                if emojis not in emoji_list_all:
                    emoji_list_all.append(emojis)
        else:continue
    print(emoji_list_all)
    print(len(emoji_list_all))
    print(sum)
    file=open('C:/Users/surface/Desktop/final project/codes/the whole process/DICS/emoji_full_dic.txt','w',encoding="UTF-8")
    for emojis in emoji_list_all:
        file.write(str(emojis))
        file.write(",")
        file.write(emoji.emojize(emojis))
        file.write("\n")
    file.close()



if __name__ == "__main__":
    # csvfile="C:/Users/surface/Desktop/final project/codes/the whole process/normal_labled_origin.csv"
    # df=read_csv(csvfile)
    # text_clean_df=df_clean(df,"text")
    # text_clean_df.to_csv("normal_text_cleaned.csv")
    # df2 = read_csv("C:/Users/surface/Desktop/final project/codes/the whole process/normal_text_cleaned.csv")
    # df3=clean_dataframe_generate(df2)
    # df3=repost_clean(df3)
    # df3=df_clean_nan(df3)
    # df3.to_csv("normal_1.csv")

    # csvfile="C:/Users/surface/Desktop/final project/codes/the whole process/depressed.csv"
    # df = pd.read_csv(csvfile)
    # unique_id_list = df['id'].unique()
    # for i in range(len(unique_id_list)):
    # df.ix[(df.id == unique_id_list[i]),'id']=i+738
    # for i in tqdm(range(len(df))):
    # df.loc[i, "depressed"] = '1'
    # print(df)
    # df.to_csv("C:/Users/surface/Desktop/final project/codes/the whole process/depressed_used.csv")

    csvfile = "C:/Users/surface/Desktop/final project/codes/the whole process/data_using/normal_labeled.csv"
    df=pd.read_csv(csvfile)
    df=df_clean_nan(df)
    df.drop('Unnamed: 0',axis=1, inplace=True)
    print(df)
    df.to_csv("C:/Users/surface/Desktop/final project/codes/the whole process/data_using/normal_labeled_1.csv")
