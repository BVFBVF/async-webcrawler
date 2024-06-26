import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import psycopg2
import re
import keyboard
import asyncio
import threading
from math import ceil


"""# SQL
db_config = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'marenmiroyazza12345',
    'host': 'localhost',
    'port': '5432'
}
connection = psycopg2.connect(**db_config)
cursor = connection.cursor()
table = 'urls_keywords'"""


global_urls = []
processed_urls = []
error_printed = False
last_error = None

def check_robots(url):
    url = get_main_url(get_http(url))
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--lang=en')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = uc.Chrome(options=options)
    if url[-1] == '/':
        url_robots = url + 'robots.txt'
    else:
        url_robots = url + '/robots.txt'
    dis_masks = []
    try:
        driver.get(url_robots)
        time.sleep(5)
        if driver.title == 'Доступ ограничен':
            time.sleep(10)
            driver.refresh()
            robots_txt = driver.page_source
            robots_txt = robots_txt.split('\n')
            robots_txt += ['\n'] * 100
        else:
            robots_txt = driver.page_source
            robots_txt = robots_txt.split('\n')
            robots_txt += ['\n'] * 100
            disallow_pattern = re.compile(r'Disallow: *(.*)')
            for i in range(len(robots_txt)):
                if robots_txt[i] == 'User-agent: *':
                    for x in range(1, 100):
                        match_disallowed = disallow_pattern.match(robots_txt[i + x])
                        if match_disallowed is not None:
                            disallowed_url_mask = match_disallowed.group(1)
                            disallowed_url_mask = re.escape(disallowed_url_mask)
                            disallowed_url_mask = disallowed_url_mask.replace(r'\*', '.*')
                            d_u_m = url + disallowed_url_mask
                            if d_u_m.count('//') > 1:
                                d_u_m = d_u_m[::-1]
                                d_u_m = d_u_m.replace('//', '/', d_u_m.count('//') - 1)
                                d_u_m = d_u_m[::-1]
                            dis_masks.append(d_u_m)
        driver.close()
        driver.quit()
        return dis_masks
    except Exception as error:
        print('check_robots: ', error)
        driver.close()
        driver.quit()
def check_safety(url):
    options = uc.ChromeOptions()
    options.add_argument('--lang=en')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = uc.Chrome(options=options)
    url = get_http(url)
    driver.get(url)
    time.sleep(5)
    if driver.current_url.startswith('https://'):
        url = driver.current_url
        vt_verdict_l = []
        driver.get('https://www.virustotal.com/gui/home/url')
        time.sleep(3)
        s_h_h = driver.find_element(By.CSS_SELECTOR, 'home-view')
        s_r = driver.execute_script('return arguments[0].shadowRoot', s_h_h)
        vt_url_input_field = s_r.find_element(By.CSS_SELECTOR, '#urlSearchInput')
        vt_url_input_field.send_keys(url)
        vt_url_input_field.send_keys(Keys.ENTER)
        time.sleep(7)
        shadow_host_check_page = driver.find_element(By.CSS_SELECTOR, 'url-view')
        shadow_root_from_shadow_host_check_page = driver.execute_script('return arguments[0].shadowRoot', shadow_host_check_page)
        shadow_host_nested1 = shadow_root_from_shadow_host_check_page.find_element(By.CSS_SELECTOR, 'url-card')
        shadow_root_nested1 = driver.execute_script('return arguments[0].shadowRoot', shadow_host_nested1)
        vt_verdict = shadow_root_nested1.find_element(By.CSS_SELECTOR, 'span')
        vt_verdict_text = driver.execute_script('return arguments[0].textContent', vt_verdict)
        vt_verdict_l.append(vt_verdict_text.strip())
        if vt_verdict_l[0] == 'No security vendors flagged this URL as malicious':
            driver.close()
            driver.quit()
            return 'Website must be safe'
        else:
            driver.close()
            driver.quit()
            print('Website is considered undesirable or dangerous')
            print('VirusTotal: ', vt_verdict_text)
            return 'Website is considered undesirable or dangerous'
    else:
        driver.close()
        driver.quit()
        print('Website is considered undesirable or dangerous')
        return 'Website is considered undesirable or dangerous'
async def crawl(urls, processed_urls):
    global error_printed, last_error
    results = []
    for url in urls:
        if url not in processed_urls:
            if check_safety(url) == 'Website must be safe':
                processed_urls.append(url)
                while True:
                    options = uc.ChromeOptions()
                    options.add_argument('--headless')
                    options.add_argument('--lang=en')
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    driver = uc.Chrome(options=options)
                    time.sleep(5)
                    try:
                        driver.get(url)
                        time.sleep(7)
                        last_height = driver.execute_script('return document.body.scrollHeight')
                        while True:
                            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                            time.sleep(2)
                            new_height = driver.execute_script('return document.body.scrollHeight')
                            if last_height == new_height:
                                break
                            last_height = new_height
                        tags = driver.find_elements(By.XPATH, '//*')
                        dismasks = check_robots(url)
                        for tag in tags:
                            if tag.get_attribute('href') is not None and (all(re.fullmatch(mask, tag.get_attribute('href')) for mask in dismasks if len(dismasks) != 0) is False or dismasks == False) and tag.get_attribute('href') not in processed_urls:
                                results.append(tag.get_attribute('href'))
                                processed_urls.append(tag.get_attribute('href'))
                        break
                    except Exception as error:
                        driver.close()
                        driver.quit()
                        if error_printed == False:
                            print('Error while getting to url, trying one more time. to learn more about the error, type: "info".')
                            error_printed = True
                        last_error = error
                        time.sleep(15)
                    finally:
                        driver.close()
                        driver.quit()
            else:
                print('This website can be dangerous: ', url)
                break
    return results
def confirmation():
    print('Are you sure to stop the programm? (y/n | y - yes; n - no)')
    sure = input()
    if sure.lower() == 'y':
        return True
    elif sure.lower() == 'n':
        return False

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
async def main(urlss):
    iteration = 1
    while True:
        print('ITERATION', iteration)
        start_time = time.time()
        tasks = []
        task_num = 0
        for url in urlss:
            task_num += 1
            tasks.append(crawl([url], processed_urls))
            print('Task', task_num, url)
        global_urls.clear()
        rslts = await asyncio.gather(*tasks)
        flat_results = [item for sublist in rslts for item in sublist]
        filtered_results = [url for url in flat_results if not url.startswith('http://')]
        global_urls.extend(i for i in filtered_results)
        flat_results.clear()
        filtered_results.clear()
        end_time = time.time()
        print('Elapsed time: ', ceil(end_time - start_time))
        iteration += 1
        print('If you want to stop the program -> press End')
        if keyboard.is_pressed('end'):
            confirm = await asyncio.to_thread(confirmation)
            if confirm:
                exit('Exiting...')
            else:
                pass
input_thread = threading.Thread(target=user_input_handler, daemon=True)
input_thread.start()
flag_thread = threading.Thread(target=reset_flag, daemon=True)
flag_thread.start()
if __name__ == '__main__':
    while True:
        print("Enter the initial URL or group of URL's (you need to put the url with a space) for webcrawler to start working:")
        first_url = input().strip()
        if not first_url:
            continue
        urls_list = first_url.split()
        if not urls_list:
            continue
        for url in urls_list:
            global_urls.append(url)
    asyncio.run(main(global_urls))
