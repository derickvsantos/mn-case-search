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
from modules.recaptcha import resolve_captcha_2captcha
import re
import traceback

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

def get_information(browser, case_code):
    try:
        dict_case = {}
        dict_case['case_number'] = case_code
        case_title_element = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, ".//span[text()='Case Title:']/following-sibling::span"))
        )
        try:
            dict_case['case_title'] = case_title_element.text
        except:
            time.sleep(1)
            dict_case['case_title'] = case_title_element.text


        case_type_element = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, ".//span[text()='Case Type:']/following-sibling::span"))
        )
        dict_case['case_type'] = case_type_element.text

        date_filed_element = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, ".//span[text()='Date Filed:']/following-sibling::span"))
        )
        dict_case['date_filed'] = date_filed_element.text

        case_location_element = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, ".//span[text()='Case Location:']/following-sibling::span"))
        )
        dict_case['case_location'] = case_location_element.get_attribute("innerHTML")

        case_status_element = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, ".//span[text()='Case Status:']/following-sibling::span"))
        )
        dict_case['case_status'] = case_status_element.get_attribute("innerHTML")
        texts = browser.find_elements("xpath", '//div[@class="col-12 col-md-6"]')
        for record in texts:
            record = record.text
            if "Decedent\n" in record:
                dict_case['decedent'] = record
                decedent = record.split('\n')
                dict_case['decedent_first_name'], dict_case['decedent_last_name'], dict_case['decedent_middle_initial'] = separate_name(decedent[1])
                try:
                    dict_case['dob'] = decedent[3].replace('DOB: ', "")
                except:
                    dict_case['dob'] = 'NA'
                try:
                    dict_case['dod'] = decedent[5].replace('DOD: ', "")
                except:
                    dict_case['dod'] = 'NA'
                if dict_case['dob'] == 'NA' and dict_case['dod'] == 'NA':
                    dict_case['decedent_address'] = decedent[2]
                elif dict_case ['dob'] != 'NA' and dict_case['dod'] == 'NA':
                    dict_case['decedent_address'] = decedent[4]
            if "Applicant\n" in record:
                dict_case['applicant_info'] = record
                applicant = record.split('\n')
                dict_case['applicant_first_name'], dict_case['applicant_last_name'], dict_case['applicant_middle_initial'] = separate_name(applicant[1])
                dict_case['applicant_address'] = applicant[2]
            if "Personal Representative\n" in record:
                personal = record.split('\n')
                dict_case['pr_first_name'], dict_case['pr_last_name'], dict_case['pr_middle_initial'] = separate_name(personal[1])
                dict_case['pr_address'] = personal[2]
            if "Attorneys Active\n" in record:
                attorney = record.split('\n')
                attorney_full_name = re.sub(r'\s*-.*', '', attorney[1])
                dict_case['attorney_first_name'], dict_case['attorney_last_name'], dict_case['attorney_middle_initial'] = separate_name(attorney_full_name)
            if "Respondent\n" in record:
                respondent = record.split('\n')
                dict_case['respondent_first_name'], dict_case['respondent_last_name'], dict_case['respondent_initial_name'] = separate_name(respondent[1])
                dict_case['respondent_dob'] = respondent[3].replace('DOB: ', "")
                try:
                    dict_case['respondent_address'] = respondent[4]
                except:
                    dict_case['respondent_address'] = "NA"
            if "Petitioner\n" in record:
                petitioner = record.split('\n')
                dict_case['petitioner_name'] = petitioner[1]
                try:
                    dict_case['petitioner_address'] = petitioner[2]
                except:
                    dict_case['petitioner_address'] = "NA"

        return dict_case
    except Exception as error:
        print(error)
        raise Exception(traceback.format_exc())

def separate_name(full_name):
    parts = full_name.split(', ')
    last_name = parts[0]
    first_name_parts = parts[1].split()
    first_name = first_name_parts[0]
    middle_initial = first_name_parts[1][0] if len(first_name_parts) > 1 else ''
    return first_name, last_name, middle_initial

def search_case(case_code, browser, index):
    browser.get('https://publicaccess.courts.state.mn.us/CaseSearch')
    case_number_element = WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//*[text()='Case Number']"))
    )
    try:
        popup_element = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.ID, "tcModalAcceptBtn"))
    )
        time.sleep(0.5)
        popup_element.click()
    except:
        pass
    
    case_number_element.click()
    try:
        captcha_locator = WebDriverWait(browser, 15).until(
            EC.presence_of_element_located((By.XPATH, ".//div[contains(@class, 'g-recaptcha')]"))
        )
        google_key = captcha_locator.get_attribute("data-sitekey")
    except:
        captcha_locator = WebDriverWait(browser, 15).until(
            EC.presence_of_element_located((By.XPATH, ".//div[contains(@class, 'g-recaptcha')]"))
        )
        google_key = captcha_locator.get_attribute("data-sitekey")
    url = browser.current_url
    
    
    search_element = WebDriverWait(browser, 20).until(
        EC.presence_of_element_located((By.ID, "CaseSearchNumber"))
    )

    search_element.send_keys(case_code)
    captcha_token = resolve_captcha_2captcha(google_key, url)
    captcha_element = browser.find_element(By.ID, 'g-recaptcha-response-1')
    browser.execute_script("arguments[0].style.display = 'block';", captcha_element)
    browser.execute_script(f"arguments[0].value = '{captcha_token}';", captcha_element)
    browser.execute_script("""
        var element = arguments[0];
        element.value = arguments[1];
        element.dispatchEvent(new Event('change', { bubbles: true }));
    """, captcha_element, captcha_token)
    

    btn_find = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "btnCaseSearch"))
    )
    
    try:
        btn_find.click()
    except:
        search_element.send_keys(Keys.ENTER)
        btn_find = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "btnCaseSearch"))
        )
    
    try:
        button_details = WebDriverWait(browser, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='btn btn-lg btn-mpa-primary float-right mpa-case-search-results-btn']"))
        )
        button_details.click()
    except Exception as e:
        try:
            btn_find = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "btnCaseSearch"))
            )
            btn_find.click()
        except:
            pass
        try:
            button_details = WebDriverWait(browser, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@class='btn btn-lg btn-mpa-primary float-right mpa-case-search-results-btn']"))
            )
            browser.execute_script("arguments[0].scrollIntoView(true);", button_details)
            browser.execute_script("arguments[0].focus();", button_details)
            button_details.send_keys(Keys.ENTER)
        except:
            button_details.click()
    
    case_info = get_information(browser, case_code)
    return case_info