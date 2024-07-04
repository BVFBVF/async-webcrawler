import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import asyncio
import threading
import requests
import contextlib
import psycopg2
import re
import os
import sys


global_urls = []
processed_urls = []
error_printed = False
changedata_flag = False
last_error = None


async def get_keywords(url, SQL_INSERT_K) -> None:
    if url not in processed_urls:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        global error_printed, last_error
        keywords = []
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--lang=en')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.binary_location = '/usr/local/bin/chrome'
        with contextlib.redirect_stderr(None), contextlib.redirect_stdout(None):
            driver = uc.Chrome(driver_executable_path='/usr/local/bin/chromedriver', options=options)
        try:
            driver.get('https://www.wordstream.com/keywords')
            driver.find_element(By.ID, 'input_1_1').send_keys(url)
            driver.find_element(By.ID, 'gform_submit_button_1').send_keys(Keys.ENTER)
            time.sleep(3)
            driver.find_element(By.CSS_SELECTOR, '[id=refine-continue]').click()
            time.sleep(3)
            last_height = driver.execute_script('return document.body.scrollHeight')
            while True:
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(2)
                new_height = driver.execute_script('return document.body.scrollHeight')
                if last_height == new_height:
                    break
                last_height = new_height
            kws = driver.find_elements(By.CSS_SELECTOR, '.sc-bTmccw.kpSNBr.MuiTableCell-root.MuiTableCell-body.MuiTableCell-sizeMedium')
            if len(kws) == 0:
                await get_keywords(url, SQL_INSERT_K)
            for kw in kws:
                if '$' not in kw.text and kw.text != 'Low' and not re.fullmatch(r'([0-9]+(,)*)+', kw.text) and kw.text != '-' and kw.text != 'High' and kw.text != 'Medium':
                    keywords.append(kw.text)
            l = [url for _ in range(len(keywords))]
            for k in range(len(l)):
                cursor.execute(SQL_INSERT_K, (l[k], keywords[k]))
        except Exception as error:
            if error_printed == False:
                print('Error while extracting keywords, trying one more time. to learn more about the error, type: "info".')
                error_printed = True
            last_error = error
            await get_keywords(url, SQL_INSERT_K)
        finally:
            connection.commit()
            cursor.close()
            driver.close()
    else:
        return None

async def crawl_w_h(url, processed_urls):
    global error_printed, last_error
    results = []
    while True:
        options = uc.ChromeOptions()
        options.add_argument('--lang=en')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.binary_location = '/usr/local/bin/chrome'
        with contextlib.redirect_stderr(None), contextlib.redirect_stdout(None):
            driver = uc.Chrome(driver_executable_path='/usr/local/bin/chromedriver', options=options)
        try:
            driver.get(url)
            time.sleep(2)
            last_height = driver.execute_script('return document.body.scrollHeight')
            while True:
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(2)
                new_height = driver.execute_script('return document.body.scrollHeight')
                if last_height == new_height:
                    break
                last_height = new_height
            tags = driver.find_elements(By.XPATH, '//*')
            for tag in tags:
                if tag.get_attribute('href') is not None and tag.get_attribute('href') not in processed_urls:
                    results.append(tag.get_attribute('href'))
            break
        except Exception as error:
            if error_printed == False:
                print('Error while getting to url, trying one more time. to learn more about the error, type: "info".')
                error_printed = True
            last_error = error
        finally:
            driver.close()
            try:
                driver.quit()
            finally:
                return results

async def crawl(urls, processed_urls, SQL_INSERT_K):
    global error_printed, last_error
    results = []
    for url in urls:
        if url not in processed_urls:
            try:
                await get_keywords(url, SQL_INSERT_K)
                print('Keywords for', url, 'were recorded in your database.')
            finally:
                processed_urls.append(url)
                while True:
                    options = uc.ChromeOptions()
                    options.add_argument('--headless')
                    options.add_argument('--lang=en')
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    options.binary_location = '/usr/local/bin/chrome'
                    with contextlib.redirect_stderr(None), contextlib.redirect_stdout(None):
                        driver = uc.Chrome(driver_executable_path='/usr/local/bin/chromedriver', options=options)
                    try:
                        driver.get(url)
                        s_code = requests.get(url).status_code
                        if s_code == 403:
                            print('This website have an antibot challenge system. Trying another way...')
                            results.extend(await crawl_w_h(url, processed_urls))
                            break
                        else:
                            time.sleep(1)
                            last_height = driver.execute_script('return document.body.scrollHeight')
                            while True:
                                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                                time.sleep(2)
                                new_height = driver.execute_script('return document.body.scrollHeight')
                                if last_height == new_height:
                                    break
                                last_height = new_height
                            tags = driver.find_elements(By.XPATH, '//*')
                            for tag in tags:
                                if tag.get_attribute('href') is not None and tag.get_attribute('href') not in processed_urls:
                                    results.append(tag.get_attribute('href'))
                            break
                    except Exception as error:
                        if error_printed == False:
                            print('Error while getting to url, trying one more time. to learn more about the error, type: "info".')
                            error_printed = True
                        last_error = error
                        try:
                            return await crawl_w_h(url, processed_urls)
                        except Exception as e:
                            print(e)
                            continue
                    finally:
                        driver.close()
                        return results

def reset_flag():
    global error_printed
    if error_printed:
        time.sleep(10)
        error_printed = False

def user_input_handler():
    global last_error
    while True:
        user_input = sys.stdin.readline().strip()
        if user_input.lower() == 'info' and last_error:
            print(last_error)
        elif user_input.lower() == 'show':
            print(global_urls)
        elif user_input.lower() == 'stop':
            print('Stopping process...')
            os._exit(0)
        elif user_input.lower() == 'help':
            print('To learn last error: print - "info"\nTo stop the programm: print - "stop"\nTo check last founded urls: print - "show"')

def get_http(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url
    return url

def get_main_url(url):
    if url[-1] != '/':
        url = url + '/'
    slashes = 0
    for i in range(len(url)):
        if url[i] == '/':
            slashes += 1
        if slashes == 3:
            url = url[:i + 1]
            break
    return url

skip_extensions = [
    '.exe', '.bat', '.msi', '.sh', '.bin', '.jar',
    '.zip', '.rar', '.7z', '.tar', '.gz',
    '.iso', '.img', '.dll', '.so',
    '.mp4', '.avi', '.mov', '.wmv',
    '.mp3', '.wav', '.flac',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp',
    '.pdf', '.doc', '.docx', '.xml', '.json', '.ico',
    '.svg'
]

async def main(SQL_INSERT_K):
    print('Program started.')
    global global_urls, table
    rslts = []
    filtered_results = []
    while True:
        tasks = []
        for url in global_urls:
            tasks.append(crawl([url], processed_urls, SQL_INSERT_K))
        global_urls.clear()
        rslts.extend(await asyncio.gather(*tasks))
        flat_results = [item for sublist in rslts if sublist is not None for item in sublist if item is not None]
        for url in flat_results:
            if not url.startswith('http://'):
                if not any(url.endswith(end) for end in skip_extensions):
                    filtered_results.append(url)
        global_urls.extend(filtered_results)
        flat_results.clear()
        filtered_results.clear()
        if len(global_urls) == 0:
            print("No url's were found.")
            quit(0)

def start_threads():
    input_thread = threading.Thread(target=user_input_handler, daemon=True)
    flag_thread = threading.Thread(target=reset_flag, daemon=True)

    print("Starting threads...")
    input_thread.start()
    flag_thread.start()
    print("Threads started.")

if __name__ == '__main__':
    while True:
        print("Enter the initial URL for webcrawler to start working:")
        first_url = input()
        if len(first_url) != 0:
            print('Enter your database name:')
            db_name = input()
            if len(db_name) != 0:
                print('Enter username:')
                user = input()
                if len(user) != 0:
                    print('Enter password:')
                    password = input()
                    if len(password) != 0:
                        print('Enter host:  (If you want to run it in docker - enter "host.docker.internal)"')
                        host = input()
                        if len(host) != 0:
                            print('Enter port:')
                            port = input()
                            if len(port) != 0:
                                print('Enter the name of the table which you want to write data:')
                                table = input()
                                global_urls.append(first_url)
                                db_config = {
                                    'dbname': db_name,
                                    'user': user,
                                    'password': password,
                                    'host': host,
                                    'port': port
                                }
                                SQL_INSERT_K = f'INSERT INTO {table} (url, keyword) VALUES (%s, %s)'
                                start_threads()
                                while True:
                                    try:
                                        connection = psycopg2.connect(**db_config)
                                        cursor = connection.cursor()
                                        print("Successfully connected to the database.")
                                        print('*' * len("Successfully connected to the database."))
                                        asyncio.run(main(SQL_INSERT_K))
                                        break
                                    except Exception as error:
                                        last_error = error
                                        print('Failed connection to your database. Сheck the data you have entered:')
                                        print(db_config)
                            else:
                                print("Port cannot be empty.")
                        else:
                            print("Host cannot be empty.")
                    else:
                        print("Password cannot be empty.")
                else:
                    print("Username cannot be empty.")
            else:
                print("Database name cannot be empty.")
        else:
            print("URL cannot be empty.")
