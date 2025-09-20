import pandas as pd
import os
import time

# 셀레니움 라이브러리에서 필요한 모듈들을 가져옵니다.
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def crawl_cbnu_with_selenium():
    """
    Selenium을 사용하여 충북대학교 공지사항을 크롤링합니다.
    """
    # 크롤링할 목표 URL (충북대학교)
    list_page_url = "https://www.cbnu.ac.kr/www/selectBbsNttList.do?key=815&bbsNo=8&pageUnit=10&searchCtgry=%ED%95%99%EC%82%AC%2F%EC%9E%A5%ED%95%99&searchCnd=SJ&searchKrwd=%EC%9E%A5%ED%95%99"
    
    # URL을 조합하기 위한 기본 URL (충북대학교)
    base_url = "https://www.cbnu.ac.kr/www/"
    
    # 셀레니움 브라우저 옵션 설정
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized") # 브라우저 창 최대화

    print("💻 셀레니움 웹 드라이버를 설정합니다...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    results_list = []
    try:
        # 웹페이지 접속
        print(f"🔗 웹페이지에 접속합니다: {list_page_url}")
        driver.get(list_page_url)

        # 페이지가 완전히 로드되고, 목표 요소가 클릭 가능해질 때까지 최대 10초 대기
        wait = WebDriverWait(driver, 10)
        wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "td.p-subject a"))
        )
        print("✅ 페이지 로딩 및 상호작용 준비 완료!")
        
        # 렌더링된 최종 HTML 소스 가져오기
        html_source = driver.page_source
        soup = BeautifulSoup(html_source, "html.parser")
        
        # 데이터 추출 (사용자님이 분석하신 HTML 구조 기반)
        article_body = soup.find("tbody", class_="text_center")
        if not article_body:
            print("[오류] 게시글 목록(tbody.text_center)을 찾을 수 없습니다.")
            return None
            
        subject_cells = article_body.find_all("td", class_="p-subject")
        
        print("📊 데이터를 추출합니다...")
        for cell in subject_cells:
            link_tag = cell.find("a")
            if link_tag and 'href' in link_tag.attrs:
                relative_url = link_tag['href']
                
                # 상대 경로를 완전한 절대 경로로 만듭니다.
                # (예: /www/select... -> https://www.cbnu.ac.kr/www/select...)
                full_url = base_url + relative_url
                
                title_text = link_tag.text.strip()
                
                results_list.append({
                    "text": title_text,
                    "url": full_url
                })
        
        print("✅ 데이터 추출 완료!")
        return pd.DataFrame(results_list)

    except Exception as e:
        print(f"❌ 크롤링 중 오류가 발생했습니다: {e}")
        return None
    
    finally:
        # 모든 작업이 끝나면 브라우저 종료
        print("💻 브라우저를 종료합니다.")
        driver.quit()

# --- 메인 코드 실행 부분 ---
if __name__ == "__main__":
    print("--- 충북대학교 공지사항 셀레니움 크롤러를 시작합니다 ---")
    
    scholarship_df = crawl_cbnu_with_selenium()
    
    if scholarship_df is not None and not scholarship_df.empty:
        print("\n--- 크롤링 결과 ---")
        print(scholarship_df)
        
        output_folder = "../crawled_data"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        output_filename = os.path.join(output_folder, "cbnu_scholarships_selenium.xlsx")
        scholarship_df.to_excel(output_filename, index=False)
        
        print(f"\n✅ 결과가 '{output_filename}' 파일로 성공적으로 저장되었습니다.")
    else:
        print("\n[실패] 크롤링 과정에서 오류가 발생했거나 데이터가 없습니다.")
