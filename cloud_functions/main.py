from datetime import datetime 
file_name = 'orders-2025-07-26.csv' 
today_str = datetime.utcnow().strftime("%Y-%m-%d")
print(today_str)
if today_str in file_name:
    print('current_date')
else:
    print('not current_date') 