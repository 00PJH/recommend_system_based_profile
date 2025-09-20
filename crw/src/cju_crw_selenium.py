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

def crawl_cju_with_selenium_stable():
    """
    안정성을 강화한 Selenium 크롤러로, 명시적 대기(WebDriverWait)를 사용하여
    타이밍 문제를 해결하고 청주대학교 장학/대출 공지사항을 크롤링합니다.
    """
    list_page_url = "https://www.cju.ac.kr/www/selectBbsNttList.do?key=4577&bbsNo=881&integrDeptCode=&searchCtgry=%EC%9E%A5%ED%95%99%E3%86%8D%EB%8C%80%EC%B6%9C"
    base_url = "https://www.cju.ac.kr/www/"

    # --- 1. 셀레니움 웹 드라이버 설정 ---
    # 최신 셀레니움(4.X 이상)에서는 Options 객체를 사용하여 브라우저 설정을 관리합니다.
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # 이 줄의 주석을 풀면 브라우저 창이 보이지 않는 백그라운드에서 실행됩니다.
    options.add_argument("--start-maximized") # 브라우저 창 최대화
    
    print("💻 셀레니움 웹 드라이버를 설정합니다...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    results_list = []
    try:
        # --- 2. 웹페이지 접속 ---
        print(f"🔗 웹페이지에 접속합니다: {list_page_url}")
        driver.get(list_page_url)

        # --- 3. 페이지 로딩 대기 (핵심 수정 부분!) ---
        # 페이지가 완전히 로드되고, 우리가 찾으려는 'subject' 클래스를 가진
        # 첫 번째 'td' 태그가 '클릭 가능한 상태'가 될 때까지 최대 10초간 기다립니다.
        # 'presence_of_element_located'보다 더 안정적인 조건입니다.
        wait = WebDriverWait(driver, 10)
        wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "td.subject a"))
        )
        print("✅ 페이지 로딩 및 상호작용 준비 완료!")
        
        # --- 4. 렌더링된 HTML 소스 가져오기 및 데이터 추출 ---
        # 페이지가 완전히 로드된 것이 보장된 후에 HTML을 가져옵니다.
        html_source = driver.page_source
        soup = BeautifulSoup(html_source, "html.parser")
        
        article_body = soup.find("tbody")
        subject_cells = article_body.find_all("td", class_="subject")
        
        print("📊 데이터를 추출합니다...")
        for cell in subject_cells:
            link_tag = cell.find("a")
            if link_tag:
                relative_url = link_tag['href']
                decoded_url = relative_url.replace('&amp;', '&')
                cleaned_path = decoded_url.lstrip('./')
                full_url = base_url + cleaned_path
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
        # --- 5. 브라우저 종료 ---
        print("💻 브라우저를 종료합니다.")
        driver.quit()

# --- 메인 코드 실행 부분 ---
if __name__ == "__main__":
    print("--- 셀레니움 기반 크롤러를 시작합니다 (안정성 강화 버전) ---")
    
    scholarship_df = crawl_cju_with_selenium_stable()
    
    if scholarship_df is not None and not scholarship_df.empty:
        print("\n--- 크롤링 결과 ---")
        print(scholarship_df)
        
        output_folder = "../crawled_data"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        output_filename = os.path.join(output_folder, "cju_scholarships.xlsx")
        scholarship_df.to_excel(output_filename, index=False)
        
        print(f"\n✅ 결과가 '{output_filename}' 파일로 성공적으로 저장되었습니다.")
    else:
        print("\n[실패] 크롤링 과정에서 오류가 발생했거나 데이터가 없습니다.")
