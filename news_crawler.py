import os
os.chdir(r"C:\Users\wkdcj\pyworks\Practice\Naver") # csv 파일 저장 경로
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import time


BASE_URL = "https://news.naver.com/main/ranking/office.nhn?"
HEADER = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}

PRESS_ID = [["경향신문", "032"]]
            #[["강원일보", "087"], ["경향신문", "032"], ["국민일보", "005"], ["기자협회보", "127"], ["노컷뉴스", "079"], ["뉴스1", "421"], ["뉴스타파", "607"],
            #["뉴시스", "003"], ["더팩트", "629"], ["데일리안", "119"], ["동아사이언스", "584"], ["동아일보", "020"], ["디지털데일리", "138"], ["디지털타임스", "029"],
            #["레이디경향", "145"], ["매경이코노미", "024"], ["매일경제", "009"], ["매일신문", "088"], ["머니S", "417"], ["머니투데이", "008"], ["문화일보", "021"],
            #["미디어오늘", "006"], ["부산일보", "082"], ["블로터", "293"], ["비즈니스워치", "648"], ["서울경제", "011"], ["서울신문", "081"], ["세계일보", "022"],
            #["시사IN", "308"], ["시사저널", "586"], ["신동아", "262"], ["아시아경제", "277"], ["아이뉴스24", "031"], ["여성신문", "310"], ["연합뉴스", "001"],
            #["연합뉴스TV", "422"], ["오마이뉴스", "047"], ["월간 산", "094"], ["이데일리", "018"], ["이코노미스트", "243"], ["전자신문", "030"],
            #["조선비즈", "366"], ["조선일보", "023"], ["조세일보", "123"], ["주간경향", "033"], ["주간동아", "037"], ["주간조선", "053"],  ["중앙SUNDAY", "353"],
            #["중앙일보", "025"], ["채널A", "449"], ["코메디닷컴", "296"], ["파이낸셜뉴스", "014"], ["프레시안", "002"],
            #["한겨레", "028"], ["한겨레21", "036"], ["한경비즈니스", "050"], ["한국경제", "015"], ["한국경제TV", "215"], ["한국일보", "469"], ["헤럴드경제", "016"],
            #["헬스조선", "346"], ["JTBC", "437"], ["KBS", "056"], ["MBC", "214"], ["MBN", "057"], ["SBS", "055"],  ["SBS Biz", "347"],
            #["TV조선", "448"], ["YTN", "052"], ["ZDNet Korea", "092"]]


# '코리아중앙데일리', '코리아헤럴드', '일다' 영어기사라 제외

def get_date():
    date = time.strftime("%Y%m%d", time.localtime(time.time()))
    return date


def get_news(date):
    start_time = time.time()
    result =[]

    for id in PRESS_ID:
        res = requests.get(BASE_URL+"officeId="+id[1]+"&date="+date, headers=HEADER)
        soup = BeautifulSoup(res.text, "html.parser")

        ranking_box = soup.find_all("div", class_="rankingnews_box_inner")
        ranking = ranking_box[0].find_all(class_="list_ranking_num")
        url = ranking_box[0].find_all(class_="list_content")

        for rank in range(20):
            news = {}
            news["Date"] = int(date)
            news["Press"] = id[0]
            try:
                news["Rank"] = ranking[rank].get_text()
                news["URL"] = "https://news.naver.com" + url[rank].find("a")["href"]
                news["Title"] = url[rank].find('a').get_text()
                news["View"] = url[rank].find(class_="list_view").get_text()
            except IndexError:          # 기사가 20개가 안될 때
                continue

            res = requests.get(news["URL"], headers=HEADER)
            soup = BeautifulSoup(res.text, "html.parser")
            contents = text_clean(soup.find(id="articleBodyContents").get_text(), news["Press"])
            try:
                news["Category"] = soup.find(class_="guide_categorization_item").get_text()
            except AttributeError:      # 카테로리 태그가 없을 경우
                print(id[0], rank, "번째 기사 카테고리 없음")
                news["Category"] = "미분류"
            
            news["Content"] = contents

            result.append(news)
        print(id[0] + " 완료")

    df = pd.DataFrame(result)
    title = date + "_" + "ranking_news.csv"
    df.to_csv(title, sep=",", index=False, encoding="utf-8-sig")
    end_time = time.time()
    print(end_time - start_time)

def text_clean(text, press):
    text = text.replace(" flash 오류를 우회하기 위한 함수 추가", "")
    text = text.replace("function _flash_removeCallback() {}", "")

    if(press == "강원일보"):
        text = text.replace("▶ 네이버에서 강원일보 구독하기", "")
        text = text.replace("▶ 강원일보 네이버TV 바로가기", "")
        text = text.replace("ⓒ 강원일보 - www.kwnews.co.kr", "")
    elif(press == "경향신문"):
        text = text.replace("[경향신문]", "")
        text = text.replace("▶ [인터랙티브] 김진숙을 만나다", "")
        text = text.replace("▶ 경향신문 바로가기", "")
        text = text.replace("▶ 경향신문 프리미엄 유료 콘텐츠가 한 달간 무료~", "")
        text = text.replace("©경향신문(www.khan.co.kr), 무단전재 및 재배포 금지", "")
    elif(press == "국민일보"):
        text = text.replace("▶ 네이버에서 국민일보를 구독하세요(클릭)", "")
        text = text.replace("▶ 국민일보 홈페이지 바로가기", "")
        text = text.replace("▶ ‘치우침 없는 뉴스’ 국민일보 신문 구독하기(클릭)", "")
        text = text.replace("GoodNews paper ⓒ 국민일보(www.kmib.co.kr), 무단전재 및 수집, 재배포금지", "")
    elif(press == "기자협회보"):
        text = text.replace("ⓒ 한국기자협회(http://www.journalist.or.kr) 무단전재 및 재배포금지", "")
    elif(press == "노컷뉴스"):
        text = text.replace("▶ 확 달라진 노컷뉴스", "")
        text = text.replace("▶ 클릭 한 번이면 노컷뉴스 구독!", "")
        text = text.replace("▶ 보다 나은 세상, 노컷브이와 함께", "")
        text = text.replace("저작권자 © CBS 노컷뉴스 무단전재 및 재배포 금지", "")
    elif(press == "뉴스1"):
        text = text.replace("▶ 네이버 메인에서 [뉴스1] 구독하기!", "")
        text = text.replace("▶ 뉴스1&BBC 한글 뉴스 ▶ 코로나19 뉴스", "")
        text = text.replace("© 뉴스1코리아(news1.kr), 무단 전재 및 재배포 금지", "")
    elif(press == "뉴스타파"):
        text = text.replace("▶️ 뉴스타파 후원하기", "")
        text = text.replace("▶️ 네이버에서 뉴스타파 구독하기", "")
        text = text.replace("▶️ 뉴스레터 받아보기", "")
    elif(press == "뉴시스"):
        text = text.replace("▶ 네이버에서 뉴시스 구독하기", "")
        text = text.replace("▶ K-Artprice, 유명 미술작품 가격 공개", "")
        text = text.replace("▶ 뉴시스 빅데이터 MSI 주가시세표 바로가기", "")
        text = text.replace("<ⓒ 공감언론 뉴시스통신사. 무단전재-재배포 금지>", "")
    elif(press == "더팩트"):
        text = text.replace("- BTS 공연 비하인드 사진 얻는 방법? [팬버십 가입하기▶]", "")
        text = text.replace("- 내 아이돌 순위는 내가 정한다! [팬앤스타 투표하기]", "")
        text = text.replace("저작권자 ⓒ 특종에 강한 더팩트 & tf.co.kr 무단 전재 및 재배포 금지", "")
    elif(press == "데일리안"):
        text = text.replace("▶ 데일리안 네이버 구독하기", "")
        text = text.replace("★ 구독만 해도 스타벅스쿠폰이 쏟아진다!", "")
        text = text.replace("▶ 제보하기", "")
        text = text.replace("ⓒ (주)데일리안 - 무단전재, 변형, 무단배포 금지", "")
    elif(press == "동아사이언스"):
        text = text.replace("▶코로나19 백신 치료제의 모든 것", "")
        text = text.replace("▶네이버에서 동아사이언스 구독하기", "")
        text = text.replace("▶'동아사이언스'에서 더 많은 뉴스 보기", "")
        text = text.replace("ⓒ 동아사이언스 콘텐츠 무단 전재 및 재배포 금지", "")
    elif(press == "동아사이언스"): 
        text = text.replace("▶ 네이버에서 [동아일보] 채널 구독하기", "")
        text = text.replace("▶ 당신의 소중한 순간을 신문으로 만들어 드립니다", "")
        text = text.replace("▶ 멀티미디어 스토리텔링 ‘The Original’", "")
        text = text.replace("ⓒ 동아일보 & donga.com, 무단 전재 및 재배포 금지", "")
    elif(press == "디지털데일리"): 
        text = text.replace("▶ 네이버에서 디지털데일리 채널 구독하기", "")
        text = text.replace("▶ IT정보의 즐거운 업그레이드 [딜라이트닷넷]", "")
        text = text.replace("<저작권자 © 디지털데일리 무단전재-재배포금지>", "")
    elif(press == "디지털타임스"):
        text = text.replace("▶[ 네이버 메인에서 디지털타임스 구독 ] / ▶[ 뉴스스탠드 구독 ]", "")
        text = text.replace("▶디지털타임스 홈페이지 바로가기’", "")
    elif(press == "레이디경향"):
        text = text.replace("▶ 레이디경향 바로가기", "")
        text = text.replace("▶ 기사제보", "")
        text = text.replace("© 레이디경향 (lady.khan.co.kr), 무단전재 및 재배포 금지", "")
    elif(press == "매경이코노미"):
        text = text.replace("▶ 네이버 메인에서 '매경이코노미'를 받아보세요", "")
        text = text.replace("▶ 고품격 자영업자 심폐소생 프로젝트 '창업직썰' 유튜브", "")
        text = text.replace("▶ 주간지 정기구독 신청", "")
        text = text.replace("[ⓒ 매일경제 & mk.co.kr, 무단전재 및 재배포 금지]", "")
    elif(press == "매일경제"):
        text = text.replace("▶ '경제 1위' 매일경제, 네이버에서 구독하세요", "")
        text = text.replace("▶ 이 제품은 '이렇게 만들죠' 영상으로 만나요", "")
        text = text.replace("▶ 부동산의 모든것 '매부리TV'가 펼칩니다", "")
        text = text.replace("[ⓒ 매일경제 & mk.co.kr, 무단전재 및 재배포 금지]", "")
    elif(press == "매일신문"):
        text = text.replace("▶ 네이버에서 매일신문 구독하기", "")
        text = text.replace("▶ 매일신문 네이버TV 바로가기", "")
        text = text.replace("▶ 나눔의 기적, 매일신문 이웃사랑", "")
        text = text.replace("ⓒ매일신문 - www.imaeil.com", "")
    elif(press == "머니S"):
        text = text.replace("▶뜨거운 증시, 오늘의 특징주는? ▶여론확인 '머니S설문'", "")
        text = text.replace("▶머니S, 네이버 메인에서 보세요", "")
        text = text.replace("<저작권자 ⓒ '성공을 꿈꾸는 사람들의 경제 뉴스' 머니S, 무단전재 및 재배포 금지>", "")
    elif(press == "머니투데이"):
        text = text.replace("▶부동산 투자는 [부릿지]", "")
        text = text.replace("▶주식 투자는 [부꾸미TALK]", "")
        text = text.replace("▶부자되는 뉴스, 머니투데이 구독하기", "")
        text = text.replace("<저작권자 ⓒ '돈이 보이는 리얼타임 뉴스' 머니투데이, 무단전재 및 재배포 금지>", "")
    elif(press == "문화일보"):
        text = text.replace("[ 문화닷컴 | 네이버 뉴스 채널 구독 | 모바일 웹 | 슬기로운 문화생활 ]", "")
        text = text.replace("[Copyrightⓒmunhwa.com '대한민국 오후를 여는 유일석간 문화일보' 무단 전재 및 재배포 금지(구독신청:02)3701-5555)]", "")

    text = re.sub('([a-zA-Z0-9_.+-]+@[a-zA-Z0-9]+\.[a-zA-Z0-9-.]+)', ' ', text) # 이메일 제거
    text = re.sub('[^\w\s]', ' ', text)     # 특수문자 제거
    text = text.strip()                     # 앞뒤 공백 제거
    
    return text


if __name__ == "__main__":
    date = get_date()
    get_news(date)