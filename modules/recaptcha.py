import time
import requests
from modules.MyLogger import logger
import traceback

API_KEY = "CHANGE-ME"

def bypass_captcha_2captcha(site_key, page_url):
    url_request = f"http://2captcha.com/in.php?key={API_KEY}&method=userrecaptcha&googlekey={site_key}&pageurl={page_url}&json=1"
    
    response = requests.get(url_request).json()
    
    if response.get("status") != 1:
        logger.log_and_save(f"Fail to create task: {response}")
        raise Exception("Fail to Solve Catpcha")

    captcha_id = response["request"]
    print(f"CAPTCHA enviado! ID: {captcha_id}")

    # Wait for captcha break
    for _ in range(120):
        time.sleep(1)
        url_result = f"http://2captcha.com/res.php?key={API_KEY}&action=get&id={captcha_id}&json=1"
        result = requests.get(url_result).json()

        if result.get("status") == 1:
            logger.log_and_save("Captcha solved")
            return result["request"]
        else:
            continue

    logger.log_and_save("Fail to Solve Captcha")
    logger.log_and_save(f'Traceback: {traceback.format_exc()}')
    raise Exception("Fail to Solve Catpcha")