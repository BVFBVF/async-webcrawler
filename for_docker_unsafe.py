import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import asyncio
import threading
from math import ceil
import requests
import contextlib


global_urls = []
processed_urls = []
error_printed = False
last_error = None


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
        time.sleep(2)
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
                    return await crawl_w_h(url, processed_urls)
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
        user_input = input()
        if user_input.lower() == 'info' and last_error:
            print(last_error)

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
        print('ITERATION:', iteration)
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
        iteration += 1

input_thread = threading.Thread(target=user_input_handler, daemon=True)
input_thread.start()
flag_thread = threading.Thread(target=reset_flag, daemon=True)
flag_thread.start()

if __name__ == '__main__':
    while True:
        print("Enter the initial URL for webcrawler to start working:")
        first_url = input().strip()
        if len(first_url) == 0:
            pass
        global_urls.append(first_url)
        break
    asyncio.run(main())