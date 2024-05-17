import pandas as pd
import gc
import hashlib
import xml.etree.ElementTree as ET
import requests
import logging
import traceback
from util import root_dir, today

# 로그 설정
logging.basicConfig(filename='log/crawling_issue.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

url = "https://www.kofiabond.or.kr/proframeWeb/XMLSERVICES/"


columns = ["종목명", "표준코드", "발행일", "만기일", "잔존기간", "발행액", "이자 지급유형", "이자 주기(월)", "표면금리"]

url="https://www.kofiabond.or.kr/proframeWeb/XMLSERVICES/"

cookies = {
    'WMONID': 'MupihE7A3ey',
}

headers = {
    'Content-Type': 'application/xml',
}

bond_types = {
    v:(str(i) if v != "전체" else "") for i, v in enumerate(
        ["전체", "국채", "지방채", "특수채", "통안증권",
              "은행채", "기타금융채", "회사채", "ABS"])
}

if __name__ == "__main__":
        dfs = {}
        
        for bond_key, bond_value in bond_types.items():
            data = f'<?xml version="1.0" encoding="utf-8"?>\n<message>\n  <proframeHeader>\n    <pfmAppName>BIS-KOFIABOND</pfmAppName>\n    <pfmSvcName>BISIssInfoSntcSrchSO</pfmSvcName>\n    <pfmFnName>list</pfmFnName>\n  </proframeHeader>\n  <systemHeader></systemHeader>\n    <BISComDspDatDTO>\n    <val1>EXP</val1>\n    <val2>{today}</val2>\n    <val3>99991231</val3>\n    <val4>{bond_value}</val4>\n    <val5></val5>\n    <val6></val6>\n    <val7></val7>\n</BISComDspDatDTO>\n</message>\n'
            response = requests.post(
                url, cookies=cookies, headers=headers, data=data)
           
            root = ET.fromstring(response.text)
            data_nums = int(root.find('.//dbio_total_count_').text)
            if data_nums == 0:
                logging.info("Null data")
                logging.info("-----")
                exit(0)

            logging.info(f"{bond_key}: finish download")
            data = []
            for bis_com_dsp_dat_dto in root.findall('.//BISComDspDatDTO'):
                row = {child.tag: child.text for child in bis_com_dsp_dat_dto}
                data.append(row)

            df = pd.DataFrame(data).iloc[:, :len(columns)]
            df.columns = columns
            dfs[bond_key] = df


        dfs_types = []
        del bond_types["전체"]
        dfs["전체"]["채권종류"] = None
        logging.info(f"Total: {dfs['전체'].shape}")

        for b in bond_types.keys():
            dfs[b]["채권종류"] = b
            dfs_types.append(dfs[b])
        df_type = pd.concat(dfs_types)
        del dfs_types

        result = pd.concat([df_type, dfs["전체"]])
        del df_type
        del dfs
        result.drop_duplicates(subset=columns, keep="last", inplace=True)
        result["수집일"] = today

        result["채권종류"] = result["채권종류"].fillna("알수없음")
        logging.info(f"Result: {result.shape}")
        logging.info(f"-----------")
            
        result.to_csv(f"{root_dir}/kofia_bis_bond_issue_{today}.csv", index=False)

