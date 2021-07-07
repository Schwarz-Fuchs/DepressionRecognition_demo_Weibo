import requests
import re
import json
import pandas as pd
from tqdm import tqdm

def nick_name_extract(json_path):
    print("reading json data\n")
    with open(json_path) as f:
        data = list(json.load(f))
    print('data read\n')
    nick_name_list=[]
    print('loading nick name\n')
    for i in tqdm(range(len(data))):
        nick_name_list.append((data[i]["nickname"]))
    return nick_name_list


def getHTMLText(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = 'utf8'
        return r.text
    except:
        return ""

def getUID(name):
    try:
        url = "https://s.weibo.com/user?q=%s&Refer=SUer_box" % name
        html = getHTMLText(url)

        plt = re.findall('class="s-btn-c" uid=([1-9][0-9]{9})', html)
        if len(plt) >= 1:
            return plt[0]
        return ""
    except:
        return ""

def getUID_namelist(name_list):
    UID_list=[]
    print('getting UID\n')
    for i in tqdm(range(10000)):
        UID=getUID(name_list[i])
        if UID!='':
            UID_list.append(UID)
        else:
            continue
    return UID_list

def list_save(list,path):
    df = pd.DataFrame(data=list)
    df.to_csv(path)
    print('df saved')
    return df

if __name__ == "__main__":
    nick_list=nick_name_extract("C:/Users/surface/Desktop/final project/codes/depressed.json")
    print(nick_list)
    UID_LIST=getUID_namelist(nick_list)
    list_save(UID_LIST,'depressed_UID.csv')

