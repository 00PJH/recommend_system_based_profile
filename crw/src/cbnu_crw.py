import requests
from bs4 import BeautifulSoup
import pandas as pd

# 크롤링할 목표 URL
url = "https://www.cbnu.ac.kr/www/selectBbsNttList.do?key=815&bbsNo=8&pageUnit=10&searchCtgry=%ED%95%99%EC%82%AC%2F%EC%9E%A5%ED%95%99&searchCnd=SJ&searchKrwd=%EC%9E%A5%ED%95%99"
base_url = "https://www.cju.ac.kr" # 상대 경로를 절대 경로로 만들기 위한 기본 URL

# HTTP 요청 및 HTML 파싱
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# 게시글 목록이 있는 tbody 태그를 찾음
# class가 'tb'는 아니지만, tbody를 직접 찾아도 괜찮습니다.
article_body = soup.find("tbody", class_= "text_center")

# tbody 안에서 class가 'subject'인 모든 td 태그를 찾음
# 이 부분은 사용자님께서 작성하신 코드와 동일합니다.
subject_cells = article_body.find_all("td", class_="p-subject")

# 최종 결과를 담을 빈 리스트 생성
results_list = []

# --- 여기서부터가 핵심 로직입니다 ---
# find_all로 찾은 각 'subject' 셀을 하나씩 순회합니다.
for cell in subject_cells:
    # 각 셀 안에서 'a' 태그를 찾습니다.
    link_tag = cell.find("a")
    
    # 'a' 태그가 존재하는지 확인합니다 (없는 경우를 방지)
    if link_tag:
        # 1. 'href' 속성 값을 가져와 URL을 추출합니다.
        #    './'로 시작하는 상대 경로이므로 base_url과 합쳐줍니다.
        relative_url = link_tag['href']
        full_url = base_url + relative_url.lstrip('.') # './' 에서 '.' 제거 후 합치기

        # 2. 'a' 태그 안의 순수한 텍스트를 가져옵니다.
        #    .text를 사용하고 .strip()으로 양쪽의 불필요한 공백과 줄바꿈을 제거합니다.
        title_text = link_tag.text.strip()
        
        # 추출한 데이터를 딕셔너리로 저장
        data_dict = {
            "text": title_text,
            "url": full_url
        }
        # 최종 리스트에 추가
        results_list.append(data_dict)

# --- pandas로 DataFrame 만들고 저장하기 ---
# 위에서 만든 리스트를 바탕으로 DataFrame을 생성합니다.
df = pd.DataFrame(results_list)

# 결과 출력
print("--- 크롤링 및 데이터 추출 결과 ---")
print(df)

# 엑셀 파일로 저장
output_filename = "results\cbnu_scholarships.xlsx"
df.to_excel(output_filename, index=False)
print(f"\n✅ 결과가 '{output_filename}' 파일로 저장되었습니다.")

