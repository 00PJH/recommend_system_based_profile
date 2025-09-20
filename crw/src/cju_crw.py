import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def crawl_cju_scholarships_updated_url():
    """
    수정된 URL을 사용하여 청주대학교 장학/대출 공지사항을 크롤링합니다.
    Referer 헤더를 포함하여 접근 권한 문제를 해결합니다.
    """
    # --- 여기가 핵심 수정 부분입니다! ---
    # 사용자님께서 요청하신 최종 URL로 변경합니다.
    list_page_url = "https://www.cju.ac.kr/www/selectBbsNttList.do?bbsNo=881&key=4577&searchCtgry=%EC%9E%A5%ED%95%99%E3%86%8D%EB%8C%80%EC%B6%9C"
    
    # URL 구조가 같으므로 base_url은 그대로 유지합니다.
    base_url = "https://www.cju.ac.kr/www/"
    
    # '정상 방문객'처럼 보이게 하기 위한 Referer 및 User-Agent 정보
    headers = {
        'Referer': list_page_url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # 요청 시 헤더 정보를 함께 전달
        response = requests.get(list_page_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        article_body = soup.find("tbody")
        if not article_body:
            print("[오류] 게시글 목록(tbody)을 찾을 수 없습니다.")
            return None

        subject_cells = article_body.find_all("td", class_="subject")
        
        results_list = []
        for cell in subject_cells:
            link_tag = cell.find("a")
            if link_tag:
                relative_url = link_tag['href']
                
                # HTML 엔티티(&amp;)를 일반 문자(&)로 변환
                decoded_url = relative_url.replace('&amp;', '&')
                
                # 상대 경로를 절대 경로로 생성
                cleaned_path = decoded_url.lstrip('./')
                full_url = base_url + cleaned_path
                
                title_text = link_tag.text.strip()
                
                results_list.append({
                    "text": title_text,
                    "url": full_url
                })

        return pd.DataFrame(results_list)

    except requests.exceptions.RequestException as e:
        print(f"HTTP 요청 중 오류가 발생했습니다: {e}")
        return None
    except Exception as e:
        print(f"크롤링 중 알 수 없는 오류가 발생했습니다: {e}")
        return None

# --- 메인 코드 실행 부분 ---
if __name__ == "__main__":
    print("청주대학교 장학/대출 공지사항 크롤링을 시작합니다 (URL 수정 완료)...")
    
    scholarship_df = crawl_cju_scholarships_updated_url()
    
    if scholarship_df is not None and not scholarship_df.empty:
        print("\n--- 크롤링 결과 ---")
        print(scholarship_df)
        
        # 결과를 저장할 폴더 생성 (없는 경우)
        output_folder = "results"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        output_filename = os.path.join(output_folder, "cju_scholarships_final.xlsx")
        scholarship_df.to_excel(output_filename, index=False)
        
        print(f"\n✅ 결과가 '{output_filename}' 파일로 성공적으로 저장되었습니다.")
    else:
        print("\n[실패] 크롤링 과정에서 오류가 발생했거나 데이터가 없습니다.")
