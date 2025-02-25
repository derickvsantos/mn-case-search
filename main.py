from modules.browser import search_case
import traceback
from modules.create_csv import write_to_csv
from modules.browser import make_firefox_browser
from modules.MyLogger import logger
from datetime import datetime

if __name__ == "__main__":
    case_prefix = "02-PR-24-"
    start_case_number = 1
    end_case_number = 827
    list_cases = []
    try:
        logger.log_and_save(f"Opening firefox")
        browser = make_firefox_browser()
        # browser.maximize_window()
    except Exception as error:
        logger.log_and_save(f"Error to open firefox")
        logger.log_and_save(f"Details: {error}")
        logger.log_and_save(f"Traceback: {traceback.format_exc()}")
        raise Exception("Error to open firefox")

    try:
        error_count = 0
        for index, case_number in enumerate(range(start_case_number, end_case_number + 1)):
            #for start_case_number dont be "1" but "01" for example
            if case_number < 10:
                case_number = f"0{case_number}"
            full_case_number = f"{case_prefix}{case_number}"
            logger.log_and_save(f"Searching infos for case: {full_case_number}")
            try:
                case_info = search_case(full_case_number, browser, index)
                list_cases.append(case_info)
            except Exception as error:
                logger.log_and_save(f"Error retrieving information for case {full_case_number}: {error}")
                logger.log_and_save(traceback.format_exc())
                error_count += 1
                if error_count > 5:
                    logger.log_and_save("Too many errors. Stopping execution")
                    raise Exception("Too many errors, verify the logs")

        if list_cases:
            file_timestamp = datetime.now().strftime("%m-%d_%H.%M.%S")
            filename = f"results-{file_timestamp}.csv"
            write_to_csv(list_cases, filename="results.csv")
            logger.log_and_save("CSV created")
        else:
            logger.log_and_save("Fail creating csv")
    except Exception as error:
        logger.log_and_save(f"Error to get information for case: {full_case_number}")
        logger.log_and_save(f"Details: {error}")
        # Print with full error description
        logger.log_and_save(f"Traceback: {traceback.format_exc()}")
    finally:
        browser.quit()
        logger.log_and_save("End of execution")