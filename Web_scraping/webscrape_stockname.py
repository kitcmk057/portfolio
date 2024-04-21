import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from sqlalchemy import create_engine

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=options)
driver.set_window_size(2560,1440)


pdf_list_updated = []
directory = "/Users/chengmankitt/Pycharm/Portfolio/Doc_AR_pdf_MVP"
pdf_list = sorted(os.listdir(directory))[1::]
code_mvp = [i.split('_')[0] for i in pdf_list]
code_mvp = [i[1:] for i in code_mvp]
code_mvp


df = pd.DataFrame(columns=['stockcode', 'eng_name'])
for i in range(len(code_mvp)):
        url = f"https://finance.yahoo.com/quote/{code_mvp[i]}.HK?.tsrc=fin-srch"
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'h1[class="D(ib) Fz(18px)"]')))
        name = driver.find_element(By.CSS_SELECTOR, 'h1[class="D(ib) Fz(18px)"]')
        df.loc[len(df.index)] = [code_mvp[i], name.text]
        print(f'finish {code_mvp[i]}')
print(df)
df_copy = df.copy()
df_copy[['eng_name', 'remaining']] = df_copy['eng_name'].str.split(r'\s\([^)]+\)$', expand=True)
df_copy.drop(columns='remaining', inplace=True)
df_copy





engine = create_engine('postgresql://postgres:geminate-prisoner-canard-spectre@database-1.cd26yy4eibqo.ap-southeast-2.rds.amazonaws.com:5432/Demo', echo=False)
df_copy.to_sql('name_table', engine, if_exists='replace', index=True)

df1 = pd.read_csv('/Users/chengmankitt/Pycharm/Portfolio/name1.csv')
df2 = pd.read_csv('/Users/chengmankitt/Pycharm/Portfolio/name2.csv')
df3 = pd.read_csv('/Users/chengmankitt/Pycharm/Portfolio/name3.csv')
df4 = pd.read_csv('/Users/chengmankitt/Pycharm/Portfolio/name4.csv')
dfs = [df1, df2, df3, df4]

final_df = pd.concat(dfs, ignore_index=True)
final_df.drop(columns='Unnamed: 0', inplace=True)
new_df = final_df.drop_duplicates(subset=['stockcode', 'eng_name'], keep='first')
new_df
new_df.to_csv('name.csv')