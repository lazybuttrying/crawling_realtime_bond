import os
import pandas as pd
import logging
import traceback
from util import today, root_dir, read_file_nan_check
from util import today_file as filename

logging.basicConfig(filename='log/chname.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

result_today, msg = read_file_nan_check(filename)
logging.info(f"today file: {msg}")

if result_today.shape[0] == 0: 
    logging.info(f"Empty data (today:{today})")
else:
    result_today.to_excel(f"{root_dir}/result_today_{today}.xlsx", engine="openpyxl", index=False)
    os.remove(filename)
    logging.info(f"Rename today data (today:{today})")
    result_today, msg = read_file_nan_check(filename)

logging.info("-----")
