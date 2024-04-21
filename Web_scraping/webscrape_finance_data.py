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


directory = "/Users/chengmankitt/Pycharm/Portfolio/Doc_AR_pdf_MVP"
pdf_list = sorted(os.listdir(directory))[1::]
code_mvp = [i.split('_')[0] for i in pdf_list]

code_mvp_list = []
for i in range(len(code_mvp)):
                url = f"http://www.aastocks.com/en/stocks/analysis/company-fundamental/profit-loss?symbol={code_mvp[i]}"
                driver.get(url)
                df = pd.DataFrame({
                    'year': ['0', '1', '2', '3', '4'],
                    'stock_code': [f'{code_mvp[i]}', f'{code_mvp[i]}', f'{code_mvp[i]}', f'{code_mvp[i]}', f'{code_mvp[i]}']
                })

                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'tr[ref="PL_Field_NB_4_1"] > td')))
                f_year = driver.find_elements(By.CSS_SELECTOR, 'tr[ref="PL_Field_NB_4_1"] > td')
                turnover = driver.find_elements(By.CSS_SELECTOR, 'tr[ref="PL_Field_NB_4_2"] > td')
                cogs = driver.find_elements(By.CSS_SELECTOR, 'tr[ref="PL_Field_NB_4_5"] > td')
                gross_profit = driver.find_elements(By.CSS_SELECTOR, 'tr[ref="PL_Field_NB_4_6"] > td')
                net_profit = driver.find_elements(By.CSS_SELECTOR, 'tr[ref="PL_Field_NB_4_14"] > td')
                EBITDA = driver.find_elements(By.CSS_SELECTOR, 'tr[ref="PL_Field_NB_4_20"] > td')
                currency = driver.find_elements(By.CSS_SELECTOR, 'tr[ref="PL_Field_NB_4_18"] > td')
                unit = driver.find_elements(By.CSS_SELECTOR, 'tr[ref="PL_Field_NB_4_17"] > td')

                df['currency'] = [currency[1].text, currency[2].text, currency[3].text, currency[4].text, currency[5].text]
                df['unit'] = [unit[1].text, unit[2].text, unit[3].text, unit[4].text, unit[5].text]
                df['closing_date'] = [f_year[1].text, f_year[2].text, f_year[3].text, f_year[4].text, f_year[5].text]
                df['turnover'] = [turnover[1].text, turnover[2].text, turnover[3].text, turnover[4].text, turnover[5].text]
                df['turnover'] = df['turnover'].str.replace(',','')
                df['cogs'] = [cogs[1].text, cogs[2].text, cogs[3].text, cogs[4].text, cogs[5].text]
                df['cogs'] = df['cogs'].str.replace(',', '')
                df['gross_profit'] = [gross_profit[1].text, gross_profit[2].text, gross_profit[3].text, gross_profit[4].text, gross_profit[5].text]
                df['gross_profit'] = df['gross_profit'].str.replace(',', '')
                df['ebitda'] = [EBITDA[1].text, EBITDA[2].text, EBITDA[3].text, EBITDA[4].text, EBITDA[5].text]
                df['ebitda'] = df['ebitda'].str.replace(',', '')
                df['net_profit'] = [net_profit[1].text, net_profit[2].text, net_profit[3].text, net_profit[4].text, net_profit[5].text]
                df['net_profit'] = df['net_profit'].str.replace(',', '')

                bs_url = f'http://www.aastocks.com/en/stocks/analysis/company-fundamental/balance-sheet?symbol={code_mvp[i]}'
                driver.get(bs_url)
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'tr[ref="BS_Field_NB_30"] > td')))
                net_asset = driver.find_elements(By.CSS_SELECTOR, 'tr[ref="BS_Field_NB_30"] > td')

                df['net_asset'] = [net_asset[1].text, net_asset[2].text, net_asset[3].text, net_asset[4].text, net_asset[5].text]
                df['net_asset'] = df['net_asset'].str.replace(',', '')


                code_mvp_list.append(df)
                print(f'Done {code_mvp[i]}')

final_df = pd.concat(code_mvp_list, ignore_index=True)
final_df[['closing_year', 'closing_month']] = final_df['closing_date'].str.split('/', expand=True)
final_df.drop(columns=['closing_date'], inplace=True)
final_df['cogs'] = final_df['cogs'].str.replace('-','0')
final_df.dropna(inplace=True)
final_df.reset_index(inplace=True)
final_df.drop(columns=['index'], inplace=True)
final_df


engine = create_engine('postgresql://postgres:geminate-prisoner-canard-spectre@database-1.cd26yy4eibqo.ap-southeast-2.rds.amazonaws.com:5432/Demo', echo=False)
final_df.to_sql('waterfall_table', engine, if_exists='replace', index=True)

