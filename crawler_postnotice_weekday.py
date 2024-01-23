# 진행상황 확인
from tqdm.auto import tqdm

# 데이터프레임 다루기 위함
import pandas as pd

# # 경고 메시지를 무시
# import warnings
# warnings.filterwarnings(action='ignore')

# 날짜데이터 다루기 위함
from datetime import datetime, timedelta

# 크롬 브라우저 다루기 위함
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

# Chrome driver 자동 업데이트
from webdriver_manager.chrome import ChromeDriverManager 

# Chrome driver Manager를 통해 크롬 드라이버 자동 설치 > 최신 버전을 설치 > Service에 저장
service = Service(excutable_path=ChromeDriverManager().install())
options = Options()
options.headless = True
driver = webdriver.Chrome(service=service, options=options)

# 키워드 리스트
key_words = ['데이터', 'AI', '인공지능', 'NAS', '환경성보장제']

# 키워드별로 생성된 데이터프레임을 담기위한 리스트
dfs = []

# 접수일자 조정
weekday = datetime.today().weekday()
today = datetime.today().strftime("%Y%m%d") # 오늘날짜
if weekday == 1:
    print('화요일')
    preday = (datetime.today() - timedelta(4)).strftime("%Y%m%d") # 지난 금요일부터 이번 화요일까지
elif weekday == 4:
    preday = (datetime.today() - timedelta(3)).strftime("%Y%m%d") # 지난 화요일부터 이번 금요일까지


def crawler(key_word):
    # 나라장터 용역 페이지로 이동
    driver.get("https://www.g2b.go.kr:8101/ep/tbid/tbidFwd.do?bidSearchType=1&taskClCds=5")

    # 사업명 검색어 입력
    search_box = driver.find_element(By.XPATH, '//*[@id="bidNm"]')
    search_box.clear()
    search_box.send_keys(key_word)

    start_date = driver.find_element(By.XPATH, '//*[@id="toBidDt"]')
    start_date.clear()
    start_date.send_keys(today)
    end_data = driver.find_element(By.XPATH, '//*[@id="fromBidDt"]')
    end_data.clear()
    end_data.send_keys(preday)

    # 출력목록수 최대로 조정
    ouput_counts = driver.find_element(By.XPATH, '//*[@id="recordCountPerPage"]')
    ouput_counts = Select(ouput_counts)
    ouput_counts.select_by_value('100')

    # 검색버튼 누르기
    search_button = driver.find_element(By.XPATH, '//*[@id="buttonwrap"]/div/a[1]/span')
    search_button.click()



    # 데이터프레임 틀 생성
    table_head = driver.find_element(By.XPATH, '//*[@id="resultForm"]/div[2]/table/thead')
    table_columns = table_head.text.split(' ')[:-1]

    df = pd.DataFrame(columns = table_columns) # 데이터프레임 및 컬럼 생성
    df = df.rename(columns={'입력일시\n(입찰마감일시)':'입력일시', '공동\n수급':'입찰마감일시'})

    # 행 단위 데이터 수집 함수
    def row_crawler():
        # 테이블 바디 부분
        table_body = driver.find_element(By.XPATH, '//*[@id="resultForm"]/div[2]/table/tbody')
        table_rows = table_body.text.split('\n')
        chunk_size = 9
        table_rows = [table_rows[i:i + chunk_size] for i in range(0, len(table_rows), chunk_size)]
        table_rows[5]

        # 데이터 프레임에 행단위로 삽입
        for row_data in tqdm(table_rows): # 행단위 데이터 삽입
            print(len(row_data))
            df.loc[len(df)] = row_data

        # 테이블 로우 단위의 공고 링크 수집
        link_list = []

        links = driver.find_elements(By.XPATH, '//*[@id="resultForm"]/div[2]/table/tbody/tr/td[4]/div/a')
        for i in range(len(links)):
            link_list.append(links[i].get_attribute('href'))

        df['공고링크'] = link_list

    # 다음 페이지로 이동하기 위한 함수 선언
    def next_page():
        try:
            while True:
                page_elements = driver.find_element(By.CSS_SELECTOR, '#pagination > a.default')
                page_elements.click()
        except:
            return 'error'

    # 데이터 수집 및 페이지 이동 수행
    while True:
        row_crawler()
        is_error = next_page()
        if is_error == 'error':
            break

    # 키워드 컬럼 추가
    df['키워드'] = key_word

    # 키워드별 데이터프레임 반환
    return df

# 실행부
for key_word in key_words:
    try:
        temp = crawler(key_word)
        dfs.append(temp)
    except:
        pass

result_df = pd.concat(dfs, axis=0)
result_df.to_csv(f'./본공고 {preday} ~ {today}.csv', encoding='utf-8-sig', index=False)
driver.quit()