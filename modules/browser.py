import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import time
from modules.recaptcha import bypass_captcha_2captcha
import re
import traceback
from modules.MyLogger import logger

ROOT_DIR = Path(__file__).parent.parent

def make_firefox_browser():
    gecko_path = os.path.join(ROOT_DIR, "geckodriver.exe")
    gecko_service = Service(gecko_path)
    options = Options()
    # options.add_argument("--headless")
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
    browser = webdriver.Firefox(service=gecko_service, options=options)
    return browser

def wait_and_click(browser, locator, timeout=10):
    try:
        element = WebDriverWait(browser, timeout).until(EC.element_to_be_clickable(locator))
        element.click()
        return True
    except Exception as error:
        logger.log_and_save(f'Error to click in {locator}. Details: {error}')
        logger.log_and_save(f'Traceback: {traceback.format_exc()}')
        return False
    
def wait_and_get_text(browser, locator, timeout=10):
    try:
        element = WebDriverWait(browser, timeout).until(EC.presence_of_element_located(locator))
        return element.text.strip()
    except Exception as error:
        logger.log_and_save(f'Error to get text from {locator}. Details: {error}')
        logger.log_and_save(f'Traceback: {traceback.format_exc()}')
        return False
    
def wait_for_overlay_to_disappear(browser, timeout=20):
    WebDriverWait(browser, timeout).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "blockUI blockOverlay"))
    )

def get_information(browser, case_code):
    try:
        dict_case = {"case_number": case_code}

        fields = {
            "case_title": (By.XPATH, ".//span[text()='Case Title:']/following-sibling::span"),
            "case_type": (By.XPATH, ".//span[text()='Case Type:']/following-sibling::span"),
            "date_filed": (By.XPATH, ".//span[text()='Date Filed:']/following-sibling::span"),
            "case_location": (By.XPATH, ".//span[text()='Case Location:']/following-sibling::span"),
            "case_status": (By.XPATH, ".//span[text()='Case Status:']/following-sibling::span"),
        }

        for key, locator in fields.items():
            dict_case[key] = wait_and_get_text(browser, locator)

        texts = browser.find_elements(By.XPATH, '//div[@class="col-12 col-md-6"]')
        for record in texts:
            record = record.text
            if 'Decedent\n' in record:
                decedent = record.split('\n')
                dict_case.update(process_decedent(decedent))

            if "Applicant\n" in record:
                    applicant = record.split('\n')
                    dict_case.update(process_applicant(applicant))

            if "Personal Representative\n" in record:
                personal = record.split('\n')
                dict_case.update(process_personal_representative(personal))

            if "Attorneys Active\n" in record:
                attorney = record.split('\n')
                dict_case.update(process_attorney(attorney))

            if "Respondent\n" in record:
                respondent = record.split('\n')
                dict_case.update(process_respondent(respondent))

            if "Petitioner\n" in record:
                petitioner = record.split('\n')
                dict_case.update(process_petitioner(petitioner))

        return dict_case
    except Exception as error:
        logger.log_and_save(f"Error getting information for case: {case_code}")
        logger.log_and_save(f'Traceback: {traceback.format_exc()}')
        raise Exception(f"Error getting information for case: {case_code}")
    
def process_decedent(data):
    result = {}
    result['decedent_first_name'], result['decedent_last_name'], result['decedent_middle_initial'] = separate_name(data[1])
    result['dob'] = data[3].replace('DOB: ', "") if len(data) > 3 else 'NA'
    result['dod'] = data[5].replace('DOD: ', "") if len(data) > 5 else 'NA'
    result['decedent_address'] = data[2] if result['dob'] == 'NA' and result['dod'] == 'NA' else data[4]
    return result

def process_applicant(data):
    result = {}
    result['applicant_first_name'], result['applicant_last_name'], result['applicant_middle_initial'] = separate_name(data[1])
    result['applicant_address'] = data[2] if len(data) > 2 else 'NA'
    return result

def process_personal_representative(data):
    result = {}
    result['pr_first_name'], result['pr_last_name'], result['pr_middle_initial'] = separate_name(data[1])
    result['pr_address'] = data[2] if len(data) > 2 else 'NA'
    return result

def process_attorney(data):
    result = {}
    attorney_full_name = re.sub(r'\s*-.*', '', data[1])
    result['attorney_first_name'], result['attorney_last_name'], result['attorney_middle_initial'] = separate_name(attorney_full_name)
    return result

def process_respondent(data):
    result = {}
    result['respondent_first_name'], result['respondent_last_name'], result['respondent_initial_name'] = separate_name(data[1])
    result['respondent_dob'] = data[3].replace('DOB: ', "") if len(data) > 3 else 'NA'
    result['respondent_address'] = data[4] if len(data) > 4 else 'NA'
    return result

def process_petitioner(data):
    result = {}
    result['petitioner_name'] = data[1]
    result['petitioner_address'] = data[2] if len(data) > 2 else 'NA'
    return result


def separate_name(full_name):
    if not full_name or ',' not in full_name:
        return '', '', ''
    parts = full_name.split(', ')
    last_name = parts[0]
    first_name_parts = parts[1].split()
    first_name = first_name_parts[0]
    middle_initial = first_name_parts[1][0] if len(first_name_parts) > 1 else ''
    return first_name, last_name, middle_initial

def search_case(case_code, browser, index):
    browser.get('https://publicaccess.courts.state.mn.us/CaseSearch')
    # Wait for popup
    wait_and_click(browser, (By.ID, "tcModalAcceptBtn"), timeout=5)
    # Selecting case number search tab
    wait_and_click(browser, (By.XPATH, "//*[text()='Case Number']"), timeout=10)

    # Solving Captcha
    captcha_locator = (By.XPATH, ".//div[contains(@class, 'g-recaptcha')]")
    google_key = WebDriverWait(browser, 15).until(EC.presence_of_element_located(captcha_locator)).get_attribute("data-sitekey")
    url = browser.current_url

    # Typing Case Number
    search_element = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, "CaseSearchNumber")))
    search_element.send_keys(case_code)

    # Sending Captcha
    captcha_token = bypass_captcha_2captcha(google_key, url)
    captcha_element = browser.find_element(By.ID, 'g-recaptcha-response-1')
    browser.execute_script("arguments[0].style.display = 'block';", captcha_element)
    browser.execute_script(f"arguments[0].value = '{captcha_token}';", captcha_element)
    browser.execute_script("""
        var element = arguments[0];
        element.value = arguments[1];
        element.dispatchEvent(new Event('change', { bubbles: true }));
    """, captcha_element, captcha_token)

    if not wait_and_click(browser, (By.ID, "btnCaseSearch"), timeout=10):
        search_element.send_keys(Keys.ENTER)
    
    wait_for_overlay_to_disappear(browser)
    button = WebDriverWait(browser, 20).until(
        EC.presence_of_element_located((By.XPATH, "//a[@class='btn btn-lg btn-mpa-primary float-right mpa-case-search-results-btn']"))
    )
    browser.execute_script("arguments[0].scrollIntoView(true);", button)
    if not wait_and_click(browser, (By.XPATH, "//a[@class='btn btn-lg btn-mpa-primary float-right mpa-case-search-results-btn']"), timeout=30):
        raise Exception("Botão de detalhes não encontrado após a busca.")
    return get_information(browser, case_code)