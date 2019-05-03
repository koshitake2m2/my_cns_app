from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import re
import urllib
import time

def get_cns_cookies(username, password):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1280,1024')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(chrome_options=options)

    ac_url = 'https://ac.yamanashi.ac.jp/ActiveCampus/sso.php?url=aHR0cDovL2Nucy55YW1hbmFzaGkuYWMuanAv'

    # cnsにアクセス
    # はじめは認証してないためActiveCampusに移動する
    driver.get(ac_url)
    # フレームの切り替え
    driver.switch_to_frame('acTop')
    driver.find_element_by_name('login').send_keys(username)
    driver.find_element_by_xpath('/html/body/div[2]/div[1]/div/form/label[2]/input').send_keys(password)
    driver.find_element_by_xpath('/html/body/div[2]/div[1]/div/form/label[2]/input').send_keys(Keys.ENTER)

    # CNSにログインできるまで10秒待つ
    login_successed = False
    try:
        WebDriverWait(driver, 10).until(
        EC.title_is('山梨大学 Campus Networking Service - ホーム')
        )
        login_successed = True
    except:
        #print('time out: CNSにログインできませんでした。')
        print('time out: no login')
        return {}, login_successed

    # cookieを保持する
    cookies = driver.get_cookies()

    # スクリーンショット
    driver.save_screenshot('test.png')

    # ブラウザの１つタブを閉じる
    driver.close()
    # ブラウザ全体を終了
    driver.quit()
    return cookies, login_successed

def scrape_cns_home(cookies):
    url = 'https://cns.yamanashi.ac.jp/home.php'
    response = requests.get(url, cookies=cookies)
    #print(response.text)
    context = {}
    context['cns_home_text'] = response.text
    if response.text.find('<html>') < 0:
        context['failed_login'] = 'failed_login'
    return context

def scrape_cns_topicslist(cookies, page):
    # 表示すべて、種別すべて、掲示すべて、ページpage
    url = 'https://cns.yamanashi.ac.jp/topicslist.php?comid=&kidoku=10&sort_col=2&sort_ud=1&filter=&chgTab=4' + '&page=' + str(page)
    response = requests.get(url, cookies=cookies)

    # ログインしていない
    if response.text.find('<html>') < 0:
        context = {
            'failed_login': 'failed_login',
        }
        return context

    # スクレイピング
    # note: パーサーはlxmlを利用
    # パーサーのhtml.parserはhtmlをうまく解釈してくれず、スクレイピングできなかった
    soup = BeautifulSoup(response.text.replace('\u3000', ' '), 'lxml')
    # todo: replace '\u3000' to ' '
    #soup = BeautifulSoup(response.text, 'lxml')

    # セレクタ指定してトピックのリストを取得
    sel = 'table[style="table-layout:fixed"]'
    scraped_topics = soup.select(sel)[0].find_all('tr')

    # topicがない時
    if len(scraped_topics) == 0:
        context = {
            'topics_list': [],
        }
        return context

    # topicの辞書を作成して、リストを作成する
    topics_list = []
    for topic_i in range(1, len(scraped_topics)):
        scraped_topic = scraped_topics[topic_i]
        topic = {}
        # 投稿日
        topic['date'] = scraped_topic.find_all('td')[0].text
        # コミュニティ
        topic['community'] = scraped_topic.find_all('td')[1].text
        topic['community_link'] = scraped_topic.find_all('td')[1].a.get('href')
        # トピックタイトル
        topic['title'] = scraped_topic.find_all('td')[2].text
        if scraped_topic.find_all('td')[2].a.strong == None:
            topic['is_read'] = True
        else:
            topic['is_read'] = False
        topic['title_link'] = scraped_topic.find_all('td')[2].a.get('href')
        # トピック詳細のid
        parameters = urllib.parse.parse_qs(urllib.parse.urlparse(topic['title_link']).query)
        topic_id_list = parameters.get('id')
        if topic_id_list != None:
            topic_id = topic_id_list[0]
        else:
            topic_id = ''
        topic['id'] = topic_id
        # 添付ファイルの有無
        if scraped_topic.find_all('td')[3].img == None:
            topic['file_exists'] = False
        else:
            topic['file_exists'] = True
        # 投稿者
        topic['author'] = scraped_topic.find_all('td')[4].text
        topic['author_link'] = scraped_topic.find_all('td')[4].a.get('href')
        topics_list.append(topic)

    context = {
        'topics_list': topics_list,
    }
    return context

def scrape_cns_topicsdetail(cookies, topic_id):
    url = 'https://cns.yamanashi.ac.jp/topicsdetail.php?id=' + topic_id
    response = requests.get(url, cookies=cookies)

    # ログインしていない
    if response.text.find('<html>') < 0:
        context = {
            'failed_login': 'failed_login',
        }
        return context

    # スクレイピング
    soup = BeautifulSoup(response.text.replace('\u3000', ' '), 'lxml')

    # セレクタ指定してトピックのリストを取得
    sel = 'table[width="700"]'
    # コミュニティ、タイトル取得
    community, title = re.search(r'.*「(.*?)」.*『(.*?)』.*', soup.select(sel)[0].strong.text).groups()
    # 投稿日、時間、カテゴリ(種別)
    date = soup.select(sel)[1].find_all('tr')[0].find_all('td')[0].text.replace(' ','').split('\n')[1][:10]
    time_hms = soup.select(sel)[1].find_all('tr')[0].find_all('td')[0].text.replace(' ','').split('\n')[1][10:]
    category = soup.select(sel)[1].find_all('tr')[0].find_all('td')[0].text.replace(' ','').split('\n')[3]
    # 投稿者、投稿者の所属
    author, author_affiliation = soup.select(sel)[1].find_all('tr')[0].find_all('td')[1].text.replace('\n', '').replace(' ', '').split(':')
    # 本文
    # note: 本文はhtmlの文字列のままでtemplateに書くく時にはautoescape offにする
    raw_text = str(soup.select(sel)[1].find_all('tr')[1].td)
    # 本文中のリンクのリンク先を変更
    matches = re.findall(r'<a href="(.*?)".*?>(.*?)</a>', raw_text)
    edited_text = raw_text
    for match in matches:
        edited_text = edited_text.replace(match[0], match[1])

    # 添付ファイル
    attached_files = []
    if soup.select(sel)[1].find_all('tr')[2].table:
        for attached_file_tag in soup.select(sel)[1].find_all('tr')[2].table.find_all('tr'):
            attached_file = {}
            attached_file['name'] = attached_file_tag.text
            # note: ダウンロードをできるようにするためには以下の２点のアプローチがあるが、難しいのでここでは取り組まないことにする
            # 1. djangoで一時的に保存して、保存先のパスを返す
            # 2. selenium, requestsを駆使してレスポンスを返す
            attached_file['link'] = 'https://cns.yamanashi.ac.jp/' + attached_file_tag.a.get('href')
            attached_files.append(attached_file)

    # todo: レスポンスも取得できたらなおよし！

    topic = {
        'community': community,
        'title': title,
        'date': date,
        'time_hms': time_hms,
        'category': category,
        'author': author,
        'author_affiliation': author_affiliation,
        'text': edited_text,
        'attached_files': attached_files,
    }
    context = {
        'topic': topic,
    }
    return context

# todo: 廃棄
def get_cns_download_file(cookies, download_file_name, download_id):
    url = 'https://cns.yamanashi.ac.jp/download.php?seq=0&id=' + str(download_id)
    response = requests.post(url, cookies=cookies, data={ 'id': download_id })
#    matches = re.findall(r'<script type="text/javascript">window.top.location.href ="(.*?)";</script>', response.content)
    download_file = response.content
    #download_file = requests.get('https://www.yahoo.co.jp/').content
    return download_file
