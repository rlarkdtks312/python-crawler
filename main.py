# 메일 보내기 위한 라이브러리
import os
import smtplib
from email.encoders import encode_base64
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

# 날짜 데이터를 다루기 위함
from datetime import datetime, timedelta

# 사전규격 및 본 공고 수집 및 파일 생성
exec(open("crawler_prenotice_weekday.py", encoding='UTF8').read())
exec(open("crawler_postnotice_weekday.py", encoding='UTF8').read())

# 접수일자 조정
weekday = datetime.today().weekday()
today = datetime.today().strftime("%Y%m%d") # 오늘날짜
if weekday == 1:
    print('화요일')
    preday = (datetime.today() - timedelta(4)).strftime("%Y%m%d") # 지난 금요일부터 이번 화요일까지
elif weekday == 4:
    preday = (datetime.today() - timedelta(3)).strftime("%Y%m%d") # 지난 화요일부터 이번 금요일까지

msg = MIMEMultipart()

msg['From'] = '보내는주소'
msg['To'] = '받는주소'
msg['Date'] = formatdate(localtime=True)
msg['Subject'] = Header(s=f'나라장터 크롤링 결과({preday}~{today}) 공유 드립니다.', charset='utf-8')
body = MIMEText('첨부된 파일 2개를 확인해 주세요.', _charset='utf-8')
msg.attach(body)



files = list()
files.append(f'./본공고 {preday} ~ {today}.csv')
files.append(f'./사전규격 {preday} ~ {today}.csv')

for f in files:
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(f, "rb").read())
    encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename= os.path.basename(f))
    msg.attach(part)

mailServer = smtplib.SMTP_SSL('smtp.naver.com')
mailServer.login('보내는주소', '비밀번호')  # 본인 계정과 비밀번호 사용.
mailServer.send_message(msg)
mailServer.quit()