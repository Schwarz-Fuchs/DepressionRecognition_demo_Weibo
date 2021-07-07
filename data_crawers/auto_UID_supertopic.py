import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests
import re
import numpy as np

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

def Transfer_Clicks(browser):
    time.sleep(5)
    try:
        browser.execute_script("window.scrollBy(0,document.body.scrollHeight)", "")
    except:
        pass
    return "Transfer successfully \n"

def isPresent():
    temp =1
    try:
        driver.find_elements_by_css_selector('div.line-around.layout-box.mod-pagination > a:nth-child(2) > div > select > option')
    except:
        temp =0
    return temp

def extract_IDs(elems,ID_list):
    for elem in elems:
        #用户名
        weibo_username = elem.find_elements_by_css_selector('h3.m-text-cut')[0].text
        print("用户名："+ weibo_username )
        ID=getUID(weibo_username)
        ID_list.append([ID,weibo_username])
    return list


def get_current_weibo_data(elems, maxWeibo,ID_list):
    # 开始爬取数据
    before = 0
    after = 0
    n = 0
    timeToSleep = 100
    while True:
        before = after
        Transfer_Clicks(driver)
        time.sleep(3)
        elems = driver.find_elements_by_css_selector('div.card.m-panel.card9')
        print("当前包含微博最大数量：%d,n当前的值为：%d, n值到5说明已无法解析出新的微博" % (len(elems), n))
        after = len(elems)
        if after > before:
            n = 0
        if after == before:
            n = n + 1
        if n == 5:
            print("当前关键词最大微博数为：%d" % after)
            extract_IDs(elems,ID_list)
            break
        if len(elems) > maxWeibo:
            print("当前微博数以达到%d条" % maxWeibo)
            extract_IDs(elems,ID_list)
            break


# 爬虫运行
def spider(username, password, driver,  keyword, maxWeibo,ID_list):

    # 加载驱动，使用浏览器打开指定网址
    driver.set_window_size(452, 790)
    driver.get("https://passport.weibo.cn/signin/login")
    print("开始自动登陆，若出现验证码手动验证")
    time.sleep(3)

    elem = driver.find_element_by_xpath("//*[@id='loginName']")
    elem.send_keys(username)
    elem = driver.find_element_by_xpath("//*[@id='loginPassword']")
    elem.send_keys(password)
    elem = driver.find_element_by_xpath("//*[@id='loginAction']")
    elem.send_keys(Keys.ENTER)
    print("暂停30秒，用于验证码验证")
    time.sleep(30)

    '''
    # 添加cookie
    cookie = []
    for ix in cookie:
        driver.add_cookie(ix)
    driver.get("https://m.weibo.cn")
    '''

    while 1:  # 循环条件为1必定成立
        result = isPresent()
        # 解决输入验证码无法跳转的问题
        driver.get('https://m.weibo.cn/')
        print('判断页面1成功 0失败  结果是=%d' % result)
        if result == 1:
            elems = driver.find_elements_by_css_selector(
                'div.line-around.layout-box.mod-pagination > a:nth-child(2) > div > select > option')
            # return elems #如果封装函数，返回页面
            break
        else:
            print('页面还没加载出来呢')
            time.sleep(20)

    time.sleep(2)

    # 搜索关键词
    elem = driver.find_element_by_xpath("//*[@class='m-text-cut']").click()
    time.sleep(2)
    elem = driver.find_element_by_xpath("//*[@type='search']")
    elem.send_keys(keyword)
    elem.send_keys(Keys.ENTER)
    time.sleep(5)

    # elem = driver.find_element_by_xpath("//*[@class='box-left m-box-col m-box-center-a']")
    # 修改为点击超话图标进入超话，减少错误
    elem = driver.find_element_by_xpath(
        "//img[@src ='http://simg.s.weibo.com/20181009184948_super_topic_bg_small.png']")
    elem.click()
    print("超话链接获取完毕，休眠2秒")
    time.sleep(2)
    yuedu_taolun = driver.find_element_by_xpath(
        "//*[@id='app']/div[1]/div[1]/div[1]/div[4]/div/div/div/a/div[2]/h4[1]").text
    yuedu = yuedu_taolun.split("　")[0]
    taolun = yuedu_taolun.split("　")[1]
    time.sleep(2)
    name = keyword
    shishi_element = driver.find_element_by_xpath("//*[@class='scroll-box nav_item']/ul/li/span[text()='帖子']")
    driver.execute_script('arguments[0].click()', shishi_element)
    get_current_weibo_data(elems,maxWeibo,ID_list)  # 爬取实时
    time.sleep(2)


if __name__ == '__main__':
    ID_list=[]
    username = "13261899211"
    password = "ZLZ990401"
    driver = webdriver.Chrome()
    maxWeibo = 3000
    keyword = "抑郁"
    spider(username, password, driver,keyword, maxWeibo,ID_list)
    sorted_ID_List=[]
    for letter in ID_list:
        if letter not in sorted_ID_List:
            sorted_ID_List.append(letter)
    print("目前取得的用户ID数量为："+str(len(sorted_ID_List)))
    print(sorted_ID_List)
    np.save('depressed_userID.csv', sorted_ID_List)

