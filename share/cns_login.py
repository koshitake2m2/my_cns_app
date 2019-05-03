# CNSログイン
# .env.sampleを参考に.envファイルを作成して実行する

# 参考文献：
# python selenium リファレンス：https://kurozumi.github.io/selenium-python/index.html

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

cns_username = os.environ.get("CNS_USERNAME")
cns_password = os.environ.get("CNS_PASSWORD")

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1280,1024')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(chrome_options=options)

cns_url = 'https://cns.yamanashi.ac.jp'

# cnsにアクセス
# はじめは認証してないためActiveCampusに移動する
driver.get(cns_url)
# フレームの切り替え
driver.switch_to_frame('acTop')
driver.find_element_by_name('login').send_keys(cns_username)
driver.find_element_by_xpath('/html/body/div[2]/div[1]/div/form/label[2]/input').send_keys(cns_password)
driver.find_element_by_xpath('/html/body/div[2]/div[1]/div/form/label[2]/input').send_keys(Keys.ENTER)

# CNSにログインできるまで10秒待つ
try:
    WebDriverWait(driver, 10).until(
    EC.title_is('山梨大学 Campus Networking Service - ホーム')
    )
except:
    print('time out: CNSにログインできませんでした。')

# cookieを保持する
cookies = driver.get_cookies()

# cookie = {}
# for c in driver.get_cookies():
#     if c['name'] == 'CNSTAB':
#         cookie = c

# スクリーンショット
# driver.save_screenshot('test.png')

# ブラウザの１つタブを閉じる
driver.close()
# ブラウザ全体を終了
driver.quit()
