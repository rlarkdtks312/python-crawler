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

# 크롤링 수행 함수
def crawler(key_word):
    # 나라장터 용역 페이지로 이동
    driver.get("https://www.g2b.go.kr:8081/ep/preparation/prestd/preStdSrch.do?taskClCd=5")

    # 사업명 검색어 입력
    search_box = driver.find_element(By.XPATH, '//*[@id="prodNm"]')
    search_box.clear()
    search_box.send_keys(key_word)

    start_date = driver.find_element(By.XPATH, '//*[@id="toRcptDt"]')
    start_date.clear()
    start_date.send_keys(today)
    end_data = driver.find_element(By.XPATH, '//*[@id="fromRcptDt"]')
    end_data.clear()
    end_data.send_keys(preday)

    # 출력목록수 최대로 조정
    ouput_counts = driver.find_element(By.XPATH, '//*[@id="recordCountPerPage"]')
    ouput_counts = Select(ouput_counts)
    ouput_counts.select_by_value('100')

    # 검색버튼 누르기
    search_button = driver.find_element(By.XPATH, '//*[@id="frmSearch1"]/div[3]/div/a[1]/span')
    search_button.click()

    # 데이터프레임 틀 생성
    table_head = driver.find_element(By.XPATH, '//*[@id="container"]/div/table/thead')
    table_columns = table_head.text.split(' ')

    df = pd.DataFrame(columns = table_columns) # 데이터프레임 및 컬럼 생성
    df.shape

    # 행 단위 데이터 수집 함수
    def row_crawler():
        # 테이블 바디 부분
        table_body = driver.find_element(By.XPATH, '//*[@id="container"]/div/table/tbody')
        table_rows = table_body.text.split('\n')
        chunk_size = len(table_columns)
        table_rows = [table_rows[i:i + chunk_size] for i in range(0, len(table_rows), chunk_size)]

        # 데이터 프레임에 행단위로 삽입
        for row_data in tqdm(table_rows): # 행단위 데이터 삽입
            print(len(row_data))
            df.loc[len(df)] = row_data

        # 테이블 로우 단위의 공고 링크 수집
        link_list = []
        links = driver.find_elements(By.XPATH, '//*[@id="container"]/div/table/tbody/tr/td[4]/div/a')
        
        for i in range(len(links)):
            links[i].click()
            link_list.append(driver.current_url)
            driver.back()
            links = driver.find_elements(By.XPATH, '//*[@id="container"]/div/table/tbody/tr/td[4]/div/a')
        df['공고링크'] = link_list

    # 첫 페이지 크롤링, df변수에 행단위 크롤링 후 데이터 삽입 함수 실행
    row_crawler()

    # 반복작업을 위한 페이지 수 확인
    try:
        page_elements = driver.find_element(By.XPATH, '//*[@id="pagination"]')
        page_list = page_elements.text.split(' ')
        page_list

        # 크롤링
        if len(page_list) < 12:
            # 페이지 이동을 위한 인덱스 리스트 생성
            index_list = [1] + [i for i in range(3,len(page_list),1)]
            
            # 페이지 이동및 행 단위 데이터 크롤링 후 df변수에 데이터 삽입
            for i in index_list:
                next_page = driver.find_element(By.XPATH, f'//*[@id="pagination"]/a[{i}]')
                next_page.click()
                row_crawler()
        else:
            # 페이지 이동을 위한 인덱스 리스트 생성
            index_list = [1] + [i for i in range(3,len(page_list),1)]
            
            # 페이지 이동및 행 단위 데이터 크롤링 후 df변수에 데이터 삽입
            for i in index_list:
                next_page = driver.find_element(By.XPATH, f'//*[@id="pagination"]/a[{i}]')
                next_page.click()
                row_crawler()

                if i == 11:
                    # 반복작업을 위한 페이지 수 확인 
                    page_elements = driver.find_element(By.XPATH, '//*[@id="pagination"]')
                    page_list = page_elements.text.split(' ')
                    index_list = [i for i in range(3,len(page_list)-1,1)]

                    for i in index_list:
                        next_page = driver.find_element(By.XPATH, f'//*[@id="pagination"]/a[{i}]')
                        next_page.click()
                        row_crawler()
    except:
        pass

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
df_deduplicated = result_df.drop_duplicates(subset=result_df.columns.difference(['키워드']))
df_deduplicated.to_csv(f'./사전규격 {preday} ~ {today}.csv', encoding='utf-8-sig', index=False)
driver.quit()