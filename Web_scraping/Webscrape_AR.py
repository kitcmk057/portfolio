import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=options)
driver.set_window_size(2560,1440)
url = "https://www1.hkexnews.hk/search/titlesearch.xhtml"
driver.get(url)


#Click header catagory
combobox_click = driver.find_element(By.CSS_SELECTOR, 'div[class="combobox-group searchType filter__dropdown-js"]').click()
WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-value="rbAfter2006"]')))
headline_select = driver.find_element(By.CSS_SELECTOR, 'div[data-value="rbAfter2006"]').click()

#Click Annual Report
searchtype_click = driver.find_element(By.CSS_SELECTOR, 'div[class="tier1-wrap searchType-Categroy filter__dropdown-js"]').click()
WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li[data-value="40000"]')))
FS_click = driver.find_element(By.CSS_SELECTOR, 'li[data-value="40000"]').click()
WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li[data-value="40100"]')))

AR_click = driver.find_element(By.CSS_SELECTOR, 'li[data-value="40100"]').click()

#STOCK CODE MANIPULATION #PANDAS
df = pd.read_excel("/Users/chengmankitt/Pycharm/Portfolio/ListOfSecurities.xlsx")
df.columns = pd.Series(df.iloc[1,:])
df = df.iloc[2:,:]
df_hk_main = df[(df["Category"] == "Equity") & (df["Trading Currency"] == "HKD") & (df["Sub-Category"] == "Equity Securities (Main Board)")]
stock_code = df_hk_main["Stock Code"].to_list()


a = 0
#For Loop
for j, code in enumerate(stock_code[a::]):
    # Input Codes
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[id="searchStockCode"]')))
    clean = driver.find_element(By.CSS_SELECTOR, 'input[id="searchStockCode"]').clear()
    search = driver.find_element(By.CSS_SELECTOR, 'input[id="searchStockCode"]').send_keys(code)
    # Handle Timeout issue
    try:
        dropdown_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'span[class="keyword-highlight"]')))
        stock_code_select = driver.find_element(By.CSS_SELECTOR, 'span[class="keyword-highlight"]').click()
    except:
        clean = driver.find_element(By.CSS_SELECTOR, 'input[id="searchStockCode"]').clear()
        search = driver.find_element(By.CSS_SELECTOR, 'input[id="searchStockCode"]').send_keys(code)
        dropdown_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'span[class="keyword-highlight"]')))
        stock_code_select = driver.find_element(By.CSS_SELECTOR, 'span[class="keyword-highlight"]').click()

    # Click Search
    Search_button = driver.find_element(By.CSS_SELECTOR, 'a[class="filter__btn-applyFilters-js btn-blue"]').click()

    # Get AR
    df = pd.DataFrame(columns=["Stock_code", "Name", "PDF_link"])
    AR = driver.find_elements(By.CSS_SELECTOR, 'div[class="doc-link"] > a')
    for i, link in enumerate(AR):
        stock_code_select = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(link))
        df.loc[len(df) + 1] = [code, link.text, link.get_attribute('href')]
        df.to_csv(f'/Users/chengmankitt/Pycharm/Portfolio/stock_csv/{code}.csv')

    # Clear Search
    clear_existing = driver.find_element(By.CSS_SELECTOR, 'input[id="searchTitle"]').clear()
    print(f'{code}: {len(df)}: {a+j}')
