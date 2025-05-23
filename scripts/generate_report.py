import sys
import os
import pandas as pd
import numpy as np
import datetime

# 1. Import libraries & ensure config path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.snowflake_config import get_connection

# 2. Query data from Snowflake
conn = get_connection()
query = """
SELECT *
FROM SPGICI_MARKETDATA_SHARE.MDV2.PRICEDATA
WHERE assessdate >= '2020-01-01'
  AND symbol IN (
      'WEACC20','AARLQ20','WEABI20','WEAKF20',
      'WEACT20','AARLO20','WEACR20','WEAKL20')
  AND bate = 'u';
"""
df = pd.read_sql(query, conn)
conn.close()

# 3. Clean columns and convert date fields
df.columns = df.columns.str.strip().str.upper()
df['ASSESSDATE'] = pd.to_datetime(df['ASSESSDATE'], errors='coerce')
df['MODIFIEDDATETIME'] = pd.to_datetime(df['MODIFIEDDATETIME'], errors='coerce')
df = df.sort_values(by=['DESCRIPTION', 'ASSESSDATE'])

# 4. Calculate DoD % Change
df['DoD_Change_Percent'] = df.groupby('DESCRIPTION')['VALUE'].pct_change()

# 5. Statistical summary
stat_summary = df.groupby('DESCRIPTION')['VALUE'].agg(['min', 'max', 'mean', 'std']).reset_index()
stat_summary.columns = ['DESCRIPTION', 'Min', 'Max', 'Average', 'Stdev']

# 6. Prepare tables to export
price_table = df[['SYMBOL', 'DESCRIPTION', 'ASSESSDATE', 'VALUE']].rename(columns={'VALUE': 'PRICE'})
dod_table = df[['ASSESSDATE', 'DESCRIPTION', 'DoD_Change_Percent']]
raw_data = df.copy()

# 7. Save tables to Excel file
excel_path = "reports/data_report.xlsx"
with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    price_table.to_excel(writer, sheet_name='Price Data', index=False)
    dod_table.to_excel(writer, sheet_name='DoD % Change', index=False)
    stat_summary.to_excel(writer, sheet_name='Stat Summary', index=False)
    raw_data.to_excel(writer, sheet_name='Raw Data', index=False)

print("✅ Report generated and tables saved to Excel")
