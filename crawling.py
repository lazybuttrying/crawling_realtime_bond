import pandas as pd
import hashlib
import xml.etree.ElementTree as ET
import requests
import logging
import traceback
from util import columns, today, read_file_nan_check
from util import today_file as filename
from util import root_dir, yesterday

# 로그 설정
logging.basicConfig(filename='log/crawling.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

url = "https://www.kofiabond.or.kr/proframeWeb/XMLSERVICES/"

payload = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n<message>\r\n  <proframeHeader>\r\n    <pfmAppName>BIS-KOFIABOND</pfmAppName>\r\n    <pfmSvcName>BISCurTrdDescSrchSO</pfmSvcName>\r\n    <pfmFnName>listTime</pfmFnName>\r\n  </proframeHeader>\r\n  <systemHeader></systemHeader>\r\n    <BISComDspDatDTO>\r\n    <val1>20240322</val1>\r\n    <val2></val2>\r\n    <val3></val3>\r\n    <val4></val4>\r\n    <val5></val5>\r\n    <val6></val6>\r\n    <val7></val7>\r\n    <val9></val9>\r\n</BISComDspDatDTO>\r\n</message>"
headers = {
  'Content-Type': 'application/xml',
  'Cookie': 'WMONID=mbni6GooFd8'
}

def set_hashes(df: pd.DataFrame) -> pd.DataFrame:
    df["hash"] = df[columns].apply(lambda x: hashlib.md5(str(x.values).encode("utf-8")).hexdigest(), axis=1)
    return df


if __name__ == "__main__":
    try:
        payload = f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n<message>\r\n  <proframeHeader>\r\n    <pfmAppName>BIS-KOFIABOND</pfmAppName>\r\n    <pfmSvcName>BISCurTrdDescSrchSO</pfmSvcName>\r\n    <pfmFnName>listTime</pfmFnName>\r\n  </proframeHeader>\r\n  <systemHeader></systemHeader>\r\n    <BISComDspDatDTO>\r\n    <val1>{today}</val1>\r\n    <val2></val2>\r\n    <val3></val3>\r\n    <val4></val4>\r\n    <val5></val5>\r\n    <val6></val6>\r\n    <val7></val7>\r\n    <val9></val9>\r\n</BISComDspDatDTO>\r\n</message>"
        response = requests.request("POST", url, headers=headers, data=payload)
        root = ET.fromstring(response.text)
        data_nums = int(root.find('.//dbio_total_count_').text)
        if data_nums == 0:
            logging.info("Null data")
            logging.info("-----")
            exit(0)

        data = []
        for bis_com_dsp_dat_dto in root.findall('.//BISComDspDatDTO'):
            row = {"날짜": today}
            for child in bis_com_dsp_dat_dto:
                row[child.tag] = child.text
            data.append(row)

        df = pd.DataFrame(data).iloc[:, :len(columns)]
        df.columns = columns
        df = df.sort_values(["날짜", "시간"])
        df.to_excel(f"new.xlsx", engine="openpyxl", index=False)
        df = pd.read_excel("new.xlsx")

        result_today, msg = read_file_nan_check(filename)
        logging.info(f"today file: {msg}")
        result_today = result_today[columns]
        # if result_today.shape[0] != 0: 
        #     val = result_today.iloc[0,0]
        #     logging.info(f"today:{today}, {type(today)} & yesterday:{yesterday}, {type(yesterday)}")
        #     if val == int(yesterday):
        #         result_today.to_excel(f"{root_dir}/result_today_{yesterday}.xlsx", engine="openpyxl", index=False)
        #         os.remove(filename)
        #         result_today, msg = read_file_nan_check(filename)

        df = set_hashes(df)
        result_today = set_hashes(result_today)
        logging.info(f"[duplication check] new: {df.duplicated().sum()}")
        logging.info(f"[duplication check] old: {result_today[columns+['hash']].duplicated().sum()}")

        df['numbering'] = df.groupby('hash').cumcount()
        result_today['numbering'] = result_today.groupby('hash').cumcount()


        logging.info(f"[Shape] New data: {df.shape}, Old data: {result_today.shape}")
        if result_today.shape[0] == 0:
            result = df
        else:
            result = pd.concat([result_today, df])
        
        logging.info(f"[duplication check] total: {result.duplicated().sum()}")
        result = result.drop_duplicates().sort_values(["날짜","시간"])
        result["잔존기간"] = result["잔존기간"].apply(lambda x: f"{x:06}")
        # print(filename)
        result.to_excel(filename, engine="openpyxl", index=False)
        logging.info(f"Data successfully updated: {result.shape}")

    except Exception as e:
        logging.error(f"An error occurred: {traceback.format_exc()}")
    
    logging.info(f"-----")


