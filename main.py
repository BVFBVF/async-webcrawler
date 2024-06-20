from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import multiprocessing
import asyncio
import time
import psycopg2
import re


count_cores = multiprocessing.cpu_count


global_urls = []
processed_urls = []

# SQL
db_config = {
}
connection = psycopg2.connect(**db_config)
cursor = connection.cursor()
table = 'urls_keywords'

def check_robots(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = uc.Chrome(options=options)
    url_robots = url + '/robots.txt'
    dis_masks = []
    try:
        driver.get(url_robots)
        time.sleep(7)
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
    except Exception as ex:
        print(ex)
        driver.quit()
    finally:
        driver.quit()
        return dis_masks
def check_safety(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--lang=en')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
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
    vt_verdict_text = vt_verdict_text.strip()
    driver.get('https://transparencyreport.google.com/safe-browsing/search')
    time.sleep(2)
    gsb_url_input_field = driver.find_element(By.TAG_NAME, 'input')
    gsb_url_input_field.send_keys(url)
    search_button = driver.find_element(By.CSS_SELECTOR, 'i.material-icons')
    search_button.click()
    time.sleep(2)
    gsb_verdict = driver.find_element(By.CSS_SELECTOR, 'span[_ngcontent-ng-c3157161489]').text
    if gsb_verdict == 'No available data':
        driver.refresh()
        search_button.click()
        gsb_verdict = driver.find_element(By.CSS_SELECTOR, 'span[_ngcontent-ng-c3157161489]').text
    if vt_verdict_text.strip() == 'No security vendors flagged this URL as malicious' and gsb_verdict == 'No unsafe content found':
        driver.quit()
        return 'Website must be safe'
    else:
        driver.quit()
        print('VirusTotal: ', vt_verdict_text)
        print('GoogleSafeBrowsing: ', gsb_verdict)
        return 'Website is considered undesirable or dangerous'

async def crawl(boxes):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = uc.Chrome(options=options)
    time.sleep(7)
    driver.get(boxes[i])
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
        if tag.get_attribute('href') is not None and all(re.fullmatch(mask, tag.get_attribute('href')) for mask in check_robots(tag.get_attribute('href'))) is False:
            global_urls.append(tag.get_attribute('href'))
            processed_urls.append(tag.get_attribute('href'))
    driver.quit()
def worker(urls):
    _urls_ = []
    for x in range(count_cores):  # 0
        __urls__ = []
        for process in range(len(processes)):  # 0 core
            for i in range(x + process, len(urls), count_cores):  # (0, 19, 4) = (1, 5, 9), (1, 19, 4) = (2, 6, 10), (2, 19, 4) = (3, 7, 11)
                if check_safety(urls[i]) == 'Website must be safe' and urls[i] not in processed_urls:
                    __urls__.append(urls[i])
        _urls_.append(__urls__)
    return _urls_
for i in range(count_cores):
    processes = [multiprocessing.Process(target=crawl, args=(worker(global_urls)[i],)) for j in range(count_cores)]
if __name__ == '__main__':
    print('Enter URL from webcrawler should start')
    first_url = input()
    global_urls.append(first_url)
