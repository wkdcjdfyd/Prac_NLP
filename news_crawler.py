import os
os.chdir(r"C:\Users\wkdcj\pyworks\Practice\Naver") # csv 파일 저장 경로
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import time


BASE_URL = "https://news.naver.com/main/ranking/office.nhn?"
HEADER = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}

PRESS_ID = [["강원일보", "087"], ["경향신문", "032"], ["국민일보", "005"], ["기자협회보", "127"], ["노컷뉴스", "079"], ["뉴스1", "421"], ["뉴스타파", "607"],
            ["뉴시스", "003"], ["더팩트", "629"], ["데일리안", "119"], ["동아사이언스", "584"], ["동아일보", "020"], ["디지털데일리", "138"], ["디지털타임스", "029"],
            ["레이디경향", "145"], ["매경이코노미", "024"], ["매일경제", "009"], ["매일신문", "088"], ["머니S", "417"], ["머니투데이", "008"], ["문화일보", "021"],
            ["미디어오늘", "006"], ["부산일보", "082"], ["블로터", "293"], ["비즈니스워치", "648"], ["서울경제", "011"], ["서울신문", "081"], ["세계일보", "022"],
            ["시사IN", "308"], ["시사저널", "586"], ["신동아", "262"], ["아시아경제", "277"], ["아이뉴스24", "031"], ["여성신문", "310"], ["연합뉴스", "001"],
            ["연합뉴스TV", "422"], ["오마이뉴스", "047"], ["월간 산", "094"], ["이데일리", "018"], ["이코노미스트", "243"], ["전자신문", "030"],
            ["조선비즈", "366"], ["조선일보", "023"], ["조세일보", "123"], ["주간경향", "033"], ["주간동아", "037"], ["주간조선", "053"],  ["중앙SUNDAY", "353"],
            ["중앙일보", "025"], ["채널A", "449"], ["코메디닷컴", "296"], ["파이낸셜뉴스", "014"], ["프레시안", "002"],
            ["한겨레", "028"], ["한겨레21", "036"], ["한경비즈니스", "050"], ["한국경제", "015"], ["한국경제TV", "215"], ["한국일보", "469"], ["헤럴드경제", "016"],
            ["헬스조선", "346"], ["JTBC", "437"], ["KBS", "056"], ["MBC", "214"], ["MBN", "057"], ["SBS", "055"],  ["SBS Biz", "347"],
            ["TV조선", "448"], ["YTN", "052"], ["ZDNet Korea", "092"]]

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
        try:
            ranking = ranking_box[0].find_all(class_="list_ranking_num")
            url = ranking_box[0].find_all(class_="list_content")
        except IndexError:
            pass

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
                break

            res = requests.get(news["URL"], headers=HEADER)
            soup = BeautifulSoup(res.text, "html.parser")
            contents = text_clean(soup.find(id="articleBodyContents").get_text(), news["Press"])
            try:
                news["Category"] = soup.find(class_="guide_categorization_item").get_text()
            except AttributeError:      # 카테로리 태그가 없을 경우
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
    text = text.replace("동영상 뉴스", "")

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
    elif(press == "미디어오늘"):
        text = text.replace("▶네이버에서 미디어오늘 구독하기◀", "")
        text = text.replace("▶️카르텔이 된 기자단 논란 기사 모아보기◀️", "")
        text = text.replace("▶️아침에 나온 신문 총정리가 필요해~! ‘아침신문 솎아보기’◀️", "")
        text = text.replace("<Copyright ⓒ 미디어오늘. 무단전재 및 재배포 금지>", "")
    elif(press == "부산일보"):
        text = text.replace("▶ 네이버에서 부산일보 구독하기 클릭!", "")
        text = text.replace("▶ 부산닷컴 회원가입. 회원 전환하면 부산일보 지면보기 무료이벤트", "")
        text = text.replace("▶ 부산일보 홈 바로가기", "")
    elif(press == "블로터"):
        text = text.replace("저작권자 ⓒ(주)블로터앤미디어, 무단 전재 및 재배포 금지", "")
    elif(press == "비즈니스워치"):
        text = text.replace("▶워치플레이 바이오산업 전략 ▶동학개미 지식창고 '공시줍줍'", "")
        text = text.replace("▶네이버에서 '비즈워치' 구독", "")
        text = text.replace("ⓒ비즈니스워치의 소중한 저작물입니다. 무단전재와 재배포를 금합니다.", "")
    elif(press == "서울경제"):
        text = text.replace("▶ [지구용] 투명해진 맥주병, 그런데 말입니다...", "")
        text = text.replace("▶ 서울경제 더 폴리틱스 뉴스를 만나보세요!", "")
        text = text.replace("▶ 미슐랭 가이드처럼 알찬 부동산 뉴스 '집슐랭'", "")
        text = text.replace("저작권자 ⓒ 서울경제, 무단 전재 및 재배포 금지", "")
    elif(press == "서울신문"):
        text = text.replace("▶ 네이버에서 서울신문 구독하기 클릭!", "")
        text = text.replace("▶ [인터랙티브] 코로나 청년 잔혹사", "")
        text = text.replace("▶ [나우뉴스] 세상에 이런 일이", "")
        text = text.replace("ⓒ 서울신문(www.seoul.co.kr), 무단전재 및 재배포금지", "")
    elif(press == "시사IN"):
        text = text.replace("▶독립언론을 지키는 자부심 [시사IN 구독 / 후원]", "")
        text = text.replace("▶네이버에서 시사IN 채널 구독하기", "")
        text = text.replace("©시사IN, 무단전재 및 재배포 금지", "")
    elif(press == "시사저널"):
        text = text.replace("<저작권자 ⓒ 시사저널, 무단 전재 및 재배포 금지>", "")
        text = text.replace("☞ 네이버에서 시사저널 뉴스를 받아 보세요", "")
        text = text.replace("▶ 시사저널 최신호 보기", "")
    elif(press == "신동아"):
        text = text.replace("▶ 네이버에서 [신동아] 채널 구독하기", "")
        text = text.replace("▶ 신동아 최신호 보기 / 정기구독 신청하기", "")
    elif(press == "아시아경제"):
        text = text.replace("▶ 속 시원한 풀이! 2021년 정통사주·운세·토정비결", "")
        text = text.replace("▶ 직장인을 위한 '빅데이터 분석' 국비 특화과정 모집", "")
        text = text.replace("▶ 투자 성공의 핵심은 기업분석! 'CORE' 바로가기", "")
        text = text.replace("<ⓒ경제를 보는 눈, 세계를 보는 창 아시아경제 무단전재 배포금지>", "")
    elif(press == "아이뉴스24"):
        text = text.replace("▶네이버 채널에서 '아이뉴스24'를 구독해주세요.", "")
        text = text.replace("▶재밌는 아이뉴스TV 영상보기 ▶아이뉴스24 바로가기", "")
        text = text.replace("[ⓒ 아이뉴스24 무단전재 및 재배포 금지]", "")
    elif(press == "여성신문"):
        text = text.replace("▶ 여성신문 후원하기", "")
        text = text.replace("▶ 기사제보/투고하기", "")
        text = text.replace("▶ 네이버에서 [여성신문] 채널 구독하기", "")
        text = text.replace("<Copyright ⓒ 여성신문. 무단전재 및 재배포 금지>", "")
    elif(press == "연합뉴스"):
        text = text.replace("▶네이버에서도 뉴스는 연합뉴스[구독 클릭]", "")
        text = text.replace("▶[팩트체크] 국립현충원에 태극기 반입 못한다?", "")
        text = text.replace("▶제보하기", "")
        text = text.replace("<저작권자(c) 연합뉴스(https://www.yna.co.kr/), 무단 전재-재배포 금지>", "")
    elif(press == "연합뉴스TV"):
        text = text.replace("연합뉴스TV 기사문의 및 제보 : 카톡/라인 jebo23", "")
        text = text.replace("▶ 네이버에서 연합뉴스TV를 구독하세요", "")
        text = text.replace("▶ 연합뉴스TV 생방송 만나보기", "")
        text = text.replace("▶ 균형있는 뉴스, 연합뉴스TV 앱 다운받기", "")
    elif(press == "연합뉴스TV"):
        text = text.replace("연합뉴스TV 기사문의 및 제보 : 카톡/라인 jebo23", "")
        text = text.replace("▶ 네이버에서 연합뉴스TV를 구독하세요", "")
        text = text.replace("▶ 연합뉴스TV 생방송 만나보기", "")
        text = text.replace("▶ 균형있는 뉴스, 연합뉴스TV 앱 다운받기", "")
    elif(press == "오마이뉴스"):
        text = text.replace("저작권자(c) 오마이뉴스(시민기자), 무단 전재 및 재배포 금지", "")
        text = text.replace("▶오마이뉴스 '시리즈'에서 연재하세요!", "")
        text = text.replace("▶이재명 경기도지사 추천 《이재명과 기본소득》", "")
        text = text.replace("▶오마이뉴스 취재 후원하기", "")
    elif(press == "월간 산"):
        text = text.replace("▶ 조선일보가 뽑은 뉴스, 확인해보세요", "")
        text = text.replace("▶ 최고 기자들의 뉴스레터 받아보세요", "")
        text = text.replace("▶ 1등 신문 조선일보, 앱으로 편하게 보세요", "")
        text = text.replace("- Copyrights ⓒ 조선일보 & chosun.com, 무단 전재 및 재배포 금지 -", "")
    elif(press == "이데일리"):
        text = text.replace("▶ #24시간 빠른 #미리보는 뉴스 #eNews+", "")
        text = text.replace("▶ 네이버에서 '이데일리 뉴스'를 만나보세요", "")
        text = text.replace("▶ 빡침해소, 청춘뉘우스 '스냅타임'", "")
        text = text.replace("＜ⓒ종합 경제정보 미디어 이데일리 - 무단전재 & 재배포 금지＞", "")
    elif(press == "이코노미스트"):
        text = text.replace("ⓒ이코노미스트(https://economist.co.kr) '내일을 위한 경제뉴스 이코노미스트' 무단 전재 및 재배포 금지", "")
    elif(press == "전자신문"):
        text = text.replace("▶ \"2021 스마트 디지털 워크스페이스 이노베이션\" 개최", "")
        text = text.replace("▶ \"AI·DX SUMMIT KOREA 2021\" 6월 24일 개최", "")
        text = text.replace("[Copyright ⓒ 전자신문 & 전자신문인터넷, 무단전재 및 재배포 금지]", "")
    elif(press == "조선비즈"):
        text = text.replace("▶네이버에서 '명품 경제뉴스' 조선비즈를 구독하세요", "")
        text = text.replace("▶오늘부터 외식 환급… 배달앱으로 1만원 돌려받으려면", "")
        text = text.replace("▶“통번역 인재 모십니다” 배민·쿠팡, 채용시장 큰손 됐다", "")
        text = text.replace("저작권자 ⓒ 조선비즈, 무단 전재 및 재배포 금지", "")
    elif(press == "조선일보"):
        text = text.replace("▶ 조선일보가 뽑은 뉴스, 확인해보세요", "")
        text = text.replace("▶ 최고 기자들의 뉴스레터 받아보세요", "")
        text = text.replace("▶ 1등 신문 조선일보, 앱으로 편하게 보세요", "")
    elif(press == "조세일보"):
        text = text.replace("▶ 조세일보 홈페이지", "")
        text = text.replace("▶ 조세일보 네이버 뉴스스탠드 구독(종합/경제)", "")
        text = text.replace("저작권자 ⓒ 조세일보(http://www.joseilbo.com). 무단전재 및 재배포 금지", "")
    elif(press == "주간경향"):
        text = text.replace("▶ 주간경향 표지이야기 더보기 ▶ 주간경향 특집 더보기", "")
        text = text.replace("▶ 네이버 채널에서 '주간경향' 구독하기", "")
        text = text.replace("© 주간경향 (weekly.khan.co.kr), 무단전재 및 재배포 금지", "")
        text = text.replace("〈경향신문은 한국온라인신문협회(www.kona.or.kr)의 디지털뉴스이용규칙에 따른 저작권을 행사합니다.〉", "")
    elif(press == "주간동아"):
        text = text.replace("▶ [주간동아]를 네이버채널에서 만나보세요", "")
        text = text.replace("▶ [주간동아] 투자섹션 ‘투벤저스’ 팔로잉하기", "")
        text = text.replace("▶ [주간동아] 정기구독 신청하기", "")
    elif(press == "주간조선"):
        text = text.replace("▶네이버 메인에서 [주간조선] 구독하기", "")
        text = text.replace("▶주간조선 홈페이지에서 더 많은 기사 보기", "")
        text = text.replace("- Copyrights ⓒ 조선뉴스프레스 - 주간조선, 무단 전재 및 재배포 금지 -", "")
    elif(press == "중앙SUNDAY"):
        text = text.replace("▶ 중앙SUNDAY [홈페이지]", "")
        text = text.replace("▶ [네이버포스트] [PDF열람]", "")
        text = text.replace("ⓒ중앙SUNDAY(https://news.joins.com/sunday) and 중앙일보(https://joongang.co.kr) 무단 전재 및 재배포 금지", "")
    elif(press == "중앙일보"):
        text = text.replace("▶ 그가 들려주는 이야기, 이상언의 '더 모닝'", "")
        text = text.replace("▶ 건강한 주식 맛집, 앤츠랩이 차린 메뉴", "")
        text = text.replace("▶ '실검'이 사라졌다, 이슈는 어디서 봐?", "")
        text = text.replace("ⓒ중앙일보(https://joongang.co.kr), 무단 전재 및 재배포 금지", "")
    elif(press == "채널A"):
        text = text.replace("▶ '채널A' LIVE 무료 보기", "")
        text = text.replace("▶ 네이버에서 '채널A' 구독하기", "")
        text = text.replace("▶[기사보기]故 손정민 씨 사건…양말 흙·한강공원 흙 분석하는 이유는?", "")
        text = text.replace("꿈을 담는 캔버스 채널A ⓒCHANNEL A(www.ichannela.com), 무단 전재 및 재배포 금지", "")
    elif(press == "코메디닷컴"):
        text = text.replace("▶ [코메디닷컴] 바로가기", "")
        text = text.replace("▶ [베닥] 질환별 최고의 의사 알고싶다면?", "")
        text = text.replace("저작권ⓒ '건강을 위한 정직한 지식' 코메디닷컴(kormedi.com) / 무단전재-재배포 금지", "")
    elif(press == "파이낸셜뉴스"):
        text = text.replace("▶ 날로먹고 구워먹는 금융이슈 [파인애플]", "")
        text = text.replace("▶ 모(毛)아 모아 [모아시스]", "")
        text = text.replace("▶ 헉! 소리나는 스!토리 뉴스 [헉스]", "")
        text = text.replace("※ 저작권자 ⓒ 파이낸셜뉴스. 무단 전재-재배포 금지", "")
    elif(press == "프레시안"):
        text = text.replace("▶프레시안 CMS 정기후원", "")
        text = text.replace("▶네이버 프레시안 채널 구독 ▶프레시안 기사제보", "")
        text = text.replace("Copyrightsⓒ PRESSian.com 무단전재 및 재배포금지", "")
    elif(press == "한겨레"):
        text = text.replace("▶한겨레가 ‘세번째 벗’을 찾아갑니다, 서포터즈 ‘벗’", "")
        text = text.replace("▶더불어 행복한 세상을 만드는 언론, 한겨레 구독하세요!▶코로나19 기사 보기", "")
        text = text.replace("[ⓒ한겨레신문 : 무단전재 및 재배포 금지]", "")
    elif(press == "한겨레21"):
        text = text.replace("심층 탐사보도의 대표 주자 <한겨레21>과 동행할 여러분을 기다립니다. [▶네이버 채널 구독하기]", "")
        text = text.replace("[▶후원 하기][▶디지털성범죄 아카이브 '너머n' 들어가기]", "")
    elif(press == "한경비즈니스"):
        text = text.replace("▶ 한경비즈니스 네이버 뉴스에서 [구독 클릭]", "")
        text = text.replace("▶ 잡지 정기구독 신청", "")
        text = text.replace("▶ ESG 개념부터 실무까지! 한경무크 ESG 주문 바로가기", "")
        text = text.replace("ⓒ 한경비즈니스, 무단전재 및 재배포 금지", "")
    elif(press == "한국경제"):
        text = text.replace("▶ 경제지 네이버 구독 첫 400만, 한국경제 받아보세요", "")
        text = text.replace("▶ 한경 고품격 뉴스레터, 원클릭으로 구독하세요", "")
        text = text.replace("▶ 한국경제신문과 WSJ, 모바일한경으로 보세요", "")
        text = text.replace("ⓒ 한국경제 & hankyung.com, 무단전재 및 재배포 금지", "")
    elif(press == "한국경제TV"):
        text = text.replace("▶네이버에서 경제·증권 전문방송의 한국경제TV를 구독하세요", "")
        text = text.replace("▶대한민국 No.1 재테크 - 증권정보 / 주식상담 / 부동산 [LIVE 보기]", "")
        text = text.replace("ⓒ 한국경제TV, 무단 전재 및 재배포 금지", "")
    elif(press == "한국일보"):
        text = text.replace("▶[화해] 남편의 반복된 외도와 폭행, 이혼만은...", "")
        text = text.replace("▶\"자식보다 하루만 더 살기를...\" 눈 못 감는 부모들", "")
        text = text.replace("▶한국일보닷컴 바로가기", "")
    elif(press == "헤럴드경제"):
        text = text.replace("▶환경적 대화기구 '헤럴드에코'", "")
        text = text.replace("▶밀리터리 전문 콘텐츠 ‘헤밀’", "")
        text = text.replace("▶헤럴드경제 네이버 채널 구독", "")
        text = text.replace("- Copyrights ⓒ 헤럴드경제 & heraldbiz.com, 무단 전재 및 재배포 금지 -", "")
    elif(press == "헬스조선"):
        text = text.replace("▶헬스조선에만 있다 1: 전 국민 당뇨 솔루션!", "")
        text = text.replace("▶헬스조선에만 있다 2: 국내 명의 600명 누구?", "")
        text = text.replace("▶헬스조선에만 있다 3: 세상의 모든 건강 정보!", "")
        text = text.replace("- Copyrights 헬스조선 & HEALTHCHOSUN.COM, 무단 전재 및 재배포 금지 -", "")
    elif(press == "JTBC"):
        text = text.replace("▶ 시청자와 함께! JTBC 뉴스 제보하기", "")
        text = text.replace("▶ 관점과 분석이 있는 뉴스, JTBC 뉴스룸", "")
        text = text.replace("Copyright by JTBC(https://jtbc.joins.com) All Rights Reserved. 무단 전재 및 재배포 금지", "")
    elif(press == "KBS"):
        text = text.replace("▶ 더 빠르고 정확한 소식을 원하시면 KBS뉴스 구독!", "")
        text = text.replace("▶코로나19 언제 어떤 백신을 누가 맞을까?", "")
        text = text.replace("▶ 제보는 KBS! 여러분이 뉴스를 만들어 갑니다", "")
    elif(press == "MBC"):
        text = text.replace("MBC 뉴스는 24시간 여러분의 제보를 기다립니다.", "")
        text = text.replace("▷ 전화 02-784-4000", "")
        text = text.replace("▷ 이메일 mbcjebo@mbc.co.kr", "")
        text = text.replace("▷ 카카오톡 @mbc제보", "")
        text = text.replace("[저작권자(c) MBC (https://imnews.imbc.com) 무단복제-재배포 금지]", "")
        text = text.replace("▶ 네이버 홈에서 [MBC뉴스] 채널 구독하기", "")
        text = text.replace("▶ 새로움을 탐험하다. \"엠빅뉴스\"", "")
        text = text.replace("Copyright(c) Since 1996, MBC&iMBC All rights reserved.", "")
    elif(press == "MBN"):
        text = text.replace("▶ 네이버에서 'MBN뉴스'를 구독하세요!", "")
        text = text.replace("▶ 김주하 앵커 'MBN 종합뉴스' 저녁 7시 20분 진행", "")
        text = text.replace("▶ MBN 무료 고화질 온에어 서비스 GO!", "")
        text = text.replace("< Copyright ⓒ MBN(www.mbn.co.kr) 무단전재 및 재배포 금지 >", "")
    elif(press == "SBS"):
        text = text.replace("▶ [제보하기] LH 땅 투기 의혹 관련 제보", "")
        text = text.replace("▶ SBS뉴스를 네이버에서 편하게 받아보세요", "")
        text = text.replace("※ ⓒ SBS & SBS Digital News Lab. : 무단복제 및 재배포 금지", "")
    elif(press == "SBS Biz"):
        text = text.replace("▶ 돈 세는 남자의 기업분석 '카운트머니' [네이버TV]", "")
        text = text.replace("▶ 경제를 실험한다~ '머니랩' [네이버TV]", "")
        text = text.replace("저작권자 SBS미디어넷 & SBS I&M 무단전재-재배포 금지", "")
    elif(press == "TV조선"):
        text = text.replace("☞ 네이버 메인에서 TV조선 구독하기", "")
        text = text.replace("☞ 더 많은 TV조선 뉴스 보기", "")
        text = text.replace("* 뉴스제보 : 이메일(tvchosun@chosun.com), 카카오톡(tv조선제보), 전화(1661-0190)", "")
        text = text.replace("- Copyrights ⓒ TV조선. 무단전재 및 재배포 금지 -", "")
    elif(press == "YTN"):
        text = text.replace("※ '당신의 제보가 뉴스가 됩니다' YTN은 여러분의 소중한 제보를 기다립니다.", "")
        text = text.replace("[카카오톡] YTN을 검색해 채널 추가 [전화] 02-398-8585 [메일] social@ytn.co.kr", "")
        text = text.replace("[온라인 제보] www.ytn.co.kr", "")
        text = text.replace("[저작권자(c) YTN & YTN plus 무단전재 및 재배포 금지]", "")
        text = text.replace("▶ 이 시각 코로나19 확진자 현황을 확인하세요.", "")
        text = text.replace("▶ 대한민국 대표 뉴스 채널 YTN 생방송보기", "")
        text = text.replace("▶ 매주 공개되는 YTN 알쓸퀴즈쇼! 추첨을 통해 에어팟, 갤럭시 버즈를 드려요.", "")
    elif(press == "ZDNet Korea"):
        text = text.replace("▶ 지디넷코리아 '홈페이지'", "")
        text = text.replace("▶ 네이버 채널 구독하기", "")
        text = text.replace("© 메가뉴스 & ZDNET, A RED VENTURES COMPANY, 무단전재-재배포 금지", "")

    text = re.sub('([a-zA-Z0-9_.+-]+@[a-zA-Z0-9]+\.[a-zA-Z0-9-.]+)', ' ', text) # 이메일 제거
    text = re.sub('[^\w\s]', ' ', text)     # 특수문자 제거
    text = text.strip()                     # 앞뒤 공백 제거
    
    return text


if __name__ == "__main__":
    date = get_date()
    get_news(date)
