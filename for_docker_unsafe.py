import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import asyncio
import threading
from math import ceil
import requests
import contextlib
import psycopg2
import re
import queue


global_urls = []
processed_urls = []
error_printed = False
changedata_flag = False
last_error = None
user_input_queue = queue.Queue()


SQL_INSERT_K = 'INSERT INTO keywords (url, keyword) VALUES (%s, %s)'

def changedata():
    print('Enter your database name:')
    db_name = input().strip()
    if len(db_name) != 0:
        print('Enter username:')
        user = input().strip()
        if len(user) != 0:
            print('Enter password:')
            password = input().strip()
            if len(password) != 0:
                print('Enter host:  (If you want to run it in docker - enter "host.docker.internal)"')
                host = input().strip()
                if len(host) != 0:
                    print('Enter port:')
                    port = input().strip()
                    if len(port) != 0:
                        global_urls.append(first_url)
                        db_config = {
                            'dbname': db_name,
                            'user': user,
                            'password': password,
                            'host': host,
                            'port': port
                        }
                        return db_config
                    else:
                        pass
                else:
                    pass
            else:
                pass
        else:
            pass
    else:
        pass


async def get_keywords(url) -> None:
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
            time.sleep(5)
            last_height = driver.execute_script('return document.body.scrollHeight')
            while True:
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(2)
                new_height = driver.execute_script('return document.body.scrollHeight')
                if last_height == new_height:
                    break
                last_height = new_height
            kws = driver.find_elements(By.CSS_SELECTOR, '.sc-bTmccw.kpSNBr.MuiTableCell-root.MuiTableCell-body.MuiTableCell-sizeMedium')
            for kw in kws:
                if '$' not in kw.text and kw.text != 'Low' and not re.fullmatch(r'([0-9]+(,)*)+', kw.text) and kw.text != '-':
                    keywords.append(kw.text)
            l = [url for _ in range(len(keywords))]
            for k in range(len(l)):
                cursor.execute(SQL_INSERT_K, (l[k], keywords[k]))
        except Exception as error:
            if error_printed == False:
                print('Error while extracting keywords, trying one more time. to learn more about the error, type: "info".')
                error_printed = True
            last_error = error
            await get_keywords(url)
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
            return results

async def crawl(urls, processed_urls):
    global error_printed, last_error
    results = []
    for url in urls:
        if url not in processed_urls:
            try:
                await get_keywords(url)
            except Exception as e:
                print(e)
                continue
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

def input_reader():
    while True:
        user_input = input()
        user_input_queue.put(user_input)

def user_input_handler():
    global last_error
    while True:
        user_input = user_input_queue.get()
        if user_input.lower() == 'info' and last_error:
            print(last_error)

def user_input_handler_1() -> None:
    global changedata_flag
    while True:
        user_input = user_input_queue.get()
        if user_input.lower() == 'changedata':
            changedata_flag = True

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

async def main():
    global global_urls
    filtered_results = []
    iteration = 1
    while True:
        print('ITERATION', iteration)
        start_time = time.time()
        tasks = []
        for url in global_urls:
            tasks.append(crawl([url], processed_urls))
        global_urls.clear()
        rslts = await asyncio.gather(*tasks)
        flat_results = [item for sublist in rslts if sublist is not None for item in sublist if item is not None]
        for url in flat_results:
            if url.startswith('http://') == False:
                if not any(url.endswith(end) for end in skip_extensions):
                    filtered_results.append(url)
        global_urls.extend(filtered_results)
        print('COUNT OF FOUNDED URLS:', len(global_urls))
        flat_results.clear()
        filtered_results.clear()
        end_time = time.time()
        print('ELAPSED TIME: ', ceil(end_time - start_time))
        if len(global_urls) == 0:
            quit(0)
        else:
            iteration += 1

input_thread = threading.Thread(target=input_reader, daemon=True)
input_thread.start()
input_thread = threading.Thread(target=user_input_handler, daemon=True)
input_thread.start()
flag_thread = threading.Thread(target=reset_flag, daemon=True)
flag_thread.start()

if __name__ == '__main__':
    input_thread1 = threading.Thread(target=user_input_handler_1, daemon=True)
    input_thread1.start()
    while True:
        print("Enter the initial URL for webcrawler to start working:")
        first_url = user_input_queue.get()
        if len(first_url) != 0:
            print('Enter your database name:')
            db_name = input().strip()
            if len(db_name) != 0:
                print('Enter username:')
                user = input().strip()
                if len(user) != 0:
                    print('Enter password:')
                    password = input().strip()
                    if len(password) != 0:
                        print('Enter host:  (If you want to run it in docker - enter "host.docker.internal)"')
                        host = input().strip()
                        if len(host) != 0:
                            print('Enter port:')
                            port = input().strip()
                            if len(port) != 0:
                                global_urls.append(first_url)
                                db_config = {
                                    'dbname': db_name,
                                    'user': user,
                                    'password': password,
                                    'host': host,
                                    'port': port
                                }
                                while True:
                                    try:
                                        connection = psycopg2.connect(**db_config)
                                        cursor = connection.cursor()
                                        print("Successfully connected to the database.")
                                        asyncio.run(main())
                                        break
                                    except Exception as error:
                                        last_error = error
                                        print('Failed connection to your database. Сheck the data you have entered:')
                                        print(db_config)
                                        print('If you want to change it - print "changedata"/If you want to check error - print "info".')
                                        if changedata_flag:
                                            db_config = changedata()
                                            changedata_flag = False
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
