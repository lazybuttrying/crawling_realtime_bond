import logging
import traceback
import pandas as pd
import os
from datetime import datetime as dt
from util import today, root_dir, total_file, today_file, init_file
from util import create_file, read_file_nan_check

def delete_file(destination_path):
    try:
        os.remove(destination_path)
        print(f"파일 '{destination_path}' 삭제 완료")
    except FileNotFoundError:
        print(f"파일 '{destination_path}'가 존재하지 않습니다.")

    # create_file(destination_path)
    


# 로거 설정
logging.basicConfig(filename='merge.log', level=logging.INFO, format='%(asctime)s - %(message)s')


if __name__ == "__main__":
    try:
        ftotal, msg =  read_file_nan_check(total_file)
        logging.info(f"total file: {msg}")
        today = pd.read_excel(today_file)
        if today.shape[0] == 0:
            logging.info("No data in today file")
            exit(0)
        else:
            logging.info(f"Today file: {today.shape}, Total file: {ftotal.shape}")

        if ftotal.shape[0] == 0:
            day = today
        else:
            day = pd.concat([ftotal, today], axis=0)
        day = day.sort_values(["날짜", "시간"])


        if len(day) > 1000000:
            day.to_excel(f"{root_dir}/result_total_{today}.xlsx",
                          engine="openpyxl", index=False)
            delete_file(total_file)
            logging.info("Out of lines, delete result_total.xlsx and save to result_total_{today}.xlsx")
        else:
            day.to_excel(total_file,
                         engine="openpyxl", index=False)
            logging.info(f"Data successfully concatenated and saved to result_total.xlsx: {day.shape}")
        delete_file(today_file)
        logging.info("Data successfully deleted result_today.xlsx")

    except Exception as e:
        logging.error(f"An error occurred: {traceback.format_exc()}")

