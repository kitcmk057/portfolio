import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:geminate-prisoner-canard-spectre@database-1.cd26yy4eibqo.ap-southeast-2.rds.amazonaws.com:5432/Tableau', echo=False)


fin_df = pd.read_csv('/Users/chengmankitt/Pycharm/Portfolio/Archive/Archive/code_findata.csv')
fin_df[['closing_year', 'closing_month']] = fin_df['Closing Date'].str.split('/', expand=True)
fin_df.drop(columns=['Unnamed: 0', 'Closing Date'], inplace=True)
fin_df_test = fin_df.copy()
fin_df_test.rename(columns={
    "Currency": "currency",
    "Total Turnover": "turnover",
    "EBITDA": "ebitda",
    "Net Profit": "net_profit",
    "Net Assets": "net_asset"
}, inplace=True)
fin_df_test['turnover'] = fin_df_test['turnover'].str.replace(',','')
fin_df_test['turnover'] = fin_df_test['turnover'].str.replace('-','-')
fin_df_test['turnover'] = fin_df_test['turnover'].astype(float)

fin_df_test['ebitda'] = fin_df_test['ebitda'].str.replace(',','')
fin_df_test['ebitda'] = fin_df_test['ebitda'].str.replace('-','-')
fin_df_test['ebitda'] = fin_df_test['ebitda'].astype(float)

fin_df_test['net_profit'] = fin_df_test['net_profit'].str.replace(',','')
fin_df_test['net_profit'] = fin_df_test['net_profit'].str.replace('-','0')
fin_df_test['net_profit'] = fin_df_test['net_profit'].astype(float)

fin_df_test.to_sql('financial_table', engine, if_exists='replace', index=True)
