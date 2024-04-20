import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from sqlalchemy import create_engine


options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=options)
driver.set_window_size(2560,1440)
url = "https://www.hkex.com.hk/Market-Data/Securities-Prices/Equities?sc_lang=en"
driver.get(url)



pdf_list_updated = []
directory = "/Users/chengmankitt/Pycharm/Portfolio/Doc_AR_pdf_MVP"
pdf_list = sorted(os.listdir(directory))[1::]
code_mvp = [i.split('_')[0] for i in pdf_list]



df = pd.DataFrame(columns=['stockcode', 'price', 'market_cap', 'suspended'])

for i in range(len(code_mvp)):
    try:
        driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Stock Code / Keywords"]').send_keys(code_mvp[i])
        driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Stock Code / Keywords"]').send_keys(Keys.ENTER)

        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'td[class="price"]')))
        stock_price = driver.find_element(By.CSS_SELECTOR, 'td[class="price"]').text
        cap = driver.find_element(By.CSS_SELECTOR, 'td[class="market"]').text
        suspended = driver.find_element(By.CSS_SELECTOR, 'span[class="flag suspend"]').text
        df.loc[len(df.index)] = [code_mvp[i], stock_price, cap, True]
        clear_existing = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Stock Code / Keywords"]').clear()
        print(f'{code_mvp[i]} done')
    except:
        df.loc[len(df.index)] = [code_mvp[i], stock_price, cap, False]
        clear_existing = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Stock Code / Keywords"]').clear()
        print(f'{code_mvp[i]} done')


# #FEATURE ENGINEERING
df_new = df.copy()
#Price
df_new['price'] = df_new['price'].str.replace('\n','_').str.split('_').str[0].str.strip('HK$')
df_new['value'] = df_new['market_cap'].str[:-1]
df_new['unit'] = df_new['market_cap'].str[-1]
df_new.drop(columns=['market_cap'], inplace=True)
def convert_to_numeric(x):
    if x == 'B':
        return 1000000000
    elif x == 'M':
        return 1000000
    elif x == 'K':
        return 1000
    else:
        return 0
df_new['numeric_value'] = df_new['unit'].apply(convert_to_numeric)



engine = create_engine('postgresql://postgres:geminate-prisoner-canard-spectre@database-1.cd26yy4eibqo.ap-southeast-2.rds.amazonaws.com:5432/Demo', echo=False)
df_new.to_sql('cap_table', engine, if_exists='replace', index=True)
