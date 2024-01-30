import sys
import time
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.support.select import Select
from datetime import datetime
import requests
from bs4 import BeautifulSoup
'''
使用Chrome浏览器121.0.6167.86版本，若需要对应的chromedriver可下载
https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/121.0.6167.85/win64/chromedriver-win64.zip
'''

# 使用request静态获取网页中货币代码与中文的信息，速度更快
def request_code():
    response = requests.get("https://www.11meigui.com/tools/currency")
    # 使用BeautifulSoup解析网页内容
    soup = BeautifulSoup(response.text, 'html.parser')

    # 解析网页中的货币代码和中文名称
    codelist = []
    rows = soup.select("table tbody tr")
    for row in rows:
        cells = row.find_all("td")  # 获取当前行的所有单元格
        if len(cells) > 1:
            # 根据页面结构提取和保存所需信息
            item = {
                "Ch": cells[1].text.strip(),
                "code": cells[-2].text.strip()
            }
            codelist.append(item)
    return codelist

# 使用selenium方式获取网页中货币代码与中文的信息
def selenium_code():
    driver=webdriver.Chrome()
    driver.get("https://www.11meigui.com/tools/currency")
    time.sleep(1)
    codeElements=driver.find_elements("css selector", "table tbody tr")
    codelist=[]
    for element in codeElements:
        infos = element.find_elements("css selector", "td")
        if len(infos) > 1:  # 确保infos列表不为空
            item = {
                "Ch": infos[1].text.strip(),
                "code": infos[-2].text.strip()
            }
            codelist.append(item)
    driver.close()
    return codelist

# 查询货币代码对应的中文
def get_ch(code, codelist):
    for dict in codelist:
        if dict['code'] == code:
            return dict['Ch']
    return None


# 使用selenium查询目标货币的现汇卖出价
def get_sells(Ch_code,input_time):
    driver=webdriver.Chrome()
    driver.get("https://www.boc.cn/sourcedb/whpj/")
    time.sleep(1)
    # 定位到下拉框元素
    select_element = driver.find_element("css selector", "select[name='pjname']")
    # 使用Select类包装下拉框元素
    select_obj = Select(select_element)
    # 根据选项的可见文本来选择,如果没有目标货币则抛出异常
    try:
        select_obj.select_by_visible_text(Ch_code)
    except NoSuchElementException:
        print(f"未找到指定货币: {Ch_code}")
        sys.exit(1)
    time.sleep(1)
    # 点击搜索
    driver.find_element("css selector", "tbody>tr>td>input[class='search_btn']").click()
    time.sleep(1)
    # 目标时间转为datetime形式，便于处理
    inputtime=datetime.strptime(input_time, "%Y%m%d").date()
    currency=[]
    # 判断目标时间是否大于页面中货币时间
    timebelow=True
    # 记录当前页面第一个时间，判断翻页功能是否翻到最后一页
    firsttime=''
    oldtime=''
    while timebelow:
        # 获取每页货币信息
        rows = driver.find_elements("css selector", "div.BOC_main.publish table tbody tr:nth-child(n+2)")
        # 遍历获取到的每一个tr元素
        for index,row in enumerate(rows):
            # 用字典存储信息
            item={}
            infos = row.find_elements("css selector", "td")
            # 记录每页第一个日期，判断是否到最后一页
            if index==0:
                firsttime=item["time"]=infos[-1].text
                if firsttime==oldtime:
                    timebelow = False
                    break
            # 获取每个元素的卖出价和日期
            if len(infos)>1:  # 确保infos列表不为空
                showtime=datetime.strptime(infos[-1].text, "%Y.%m.%d %H:%M:%S").date()

                # 与目标时间相同的信息记录
                if showtime==inputtime:
                    item["sell"]=infos[-3].text
                    item["time"]=infos[-1].text
                    currency.append(item)
                # 目标时间大于显示时间则终止记录
                elif showtime<inputtime:
                    timebelow=False
                    break
        # 如果当前最后一个时间仍大于目标时间，则跳转至下一个页面
        driver.find_element("css selector","li[class='turn_next']").click()
        oldtime=firsttime
    driver.close()
    if len(currency)==0:
        print("未找到指定时间该货币现汇卖出价")
        sys.exit(1)
    else:
        print(currency[0]['sell'])
    return currency

# 生成对应的txt文件
def write_txt(currency,code,Ch_code):
    Ch_code = Ch_code
    code = code
    # 计算最长的日期时间字符串长度
    max_time_length = max(len(item['time']) for item in currency)
    # 打开文件准备写入
    with open('result.txt', 'w', encoding='utf-8') as file:
        file.write(f"货币名称：{Ch_code}  货币代号：{code}\n")
        # 写入列标题，根据最长的日期时间长度动态调整对齐
        file.write(f"{'现汇卖出价':<13}{'日期':<{max_time_length}}\n")
        # 遍历数据列表写入每一行的数据
        for item in currency:
            sell = item['sell']
            time = item['time']
            file.write(f"{sell:<10}{time:<{max_time_length}}\n")

# 判断时间是否合法
def validate_date(input_time):
    try:
        datetime.strptime(input_time, "%Y%m%d")
    except ValueError:
        print(f"时间格式不正确或时间不合法: {input_time}")
        sys.exit(1)


if __name__=="__main__":
    if len(sys.argv) != 3:
        print("使用方式: python3 test1.py 日期 货币代号")
        sys.exit(1)
    input_time=sys.argv[1]
    validate_date(input_time)
    code=sys.argv[2]

    codelist=request_code() # 使用request静态爬取货币代号与中文信息，速度更快
    # codelist=selenium_code() # 使用selenium爬取货币代号与中文信息，较慢

    Ch_code=get_ch(code,codelist) # 获取货币的中文名称
    if Ch_code==None:
        print("未找到对应货币代码中文")
        sys.exit(1)
    currency=get_sells(Ch_code,input_time) # 使用selenium获取目标货币的所有现汇卖出价
    write_txt(currency,code,Ch_code) # 生成txt文件
