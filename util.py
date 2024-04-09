import pandas as pd 
from datetime import datetime as dt
from datetime import timedelta

today = (dt.now()+timedelta(hours=9))
if today.weekday() == 0:
    yesterday = today-timedelta(days=3)
else:
    yesterday = today-timedelta(days=1)

today = today.strftime("%Y%m%d")
yesterday = yesterday.strftime("%Y%m%d")

        
root_dir = "/home/dodev0987/realtime/data"
# root_dir ="./data"
total_file = f"{root_dir}/result_total.xlsx"
today_file = f"{root_dir}/result_today.xlsx"
init_file = f"{root_dir}/result_init.xlsx"

columns = [
    "날짜", "시간", "종목명", "잔존기간", "신용등급", 
    "수익률", "단가(원)", "거래량", "거래대금", 
    "시장구분", "매매구분", "매매유형"
]

def create_file(filename):
    df = pd.DataFrame(columns=columns)
    df.to_excel(filename, engine="openpyxl", index=False)
    df = pd.read_excel(filename) 
    return df

def read_file_nan_check(filename):
    try:
        df = pd.read_excel(filename) 
        msg = "read file"
    except:
        df = create_file(filename)
        msg = "create new file"

    return df, msg
