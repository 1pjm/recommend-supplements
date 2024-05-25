import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Selenium 옵션 설정 (자동화 감지를 피하기 위해)
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
options.add_argument("--disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-webgl")
options.add_argument("--disable-logging")

# WebDriver 인스턴스 생성
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

# 랜덤 슬립 함수 (크롤링 감지를 피하기 위해)
def random_sleep(min_sleep=1, max_sleep=3):
    time.sleep(random.uniform(min_sleep, max_sleep))

# 웹 페이지 접근
url = "https://kr.iherb.com/c/supplements"
print(f"접속 중: {url}")
driver.get(url)
random_sleep()

# 페이지 로드 완료 대기 함수
def wait_for_element(selector, by=By.CSS_SELECTOR, timeout=60):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        print(f"요소 발견: {selector}")
        return element
    except Exception as e:
        print(f"요소 대기 중 오류 발생 {selector}: {e}")
        return None

# 페이지 로드 완료 대기
# div#mainContent 대신 여러 요소를 시도해봅니다.
if not (wait_for_element("div#mainContent") or wait_for_element("div.subCategory")):
    print("페이지 로드 중 오류 발생")
    driver.quit()
    exit()

# 각 카테고리 링크 가져오기
print("카테고리 링크 가져오는 중...")
try:
    categories = wait_for_element("div.subCategory a", timeout=10)
    if categories:
        category_links = [category.get_attribute("href") for category in driver.find_elements(By.CSS_SELECTOR, "div.subCategory a")]
        print(f"카테고리 링크 {len(category_links)}개 발견: {category_links}")
    else:
        print("카테고리 링크를 찾지 못했습니다.")
        driver.quit()
        exit()
except Exception as e:
    print(f"카테고리 링크 가져오기 중 오류 발생: {e}")
    driver.quit()
    exit()

# 각 카테고리를 순회하며 높은 평점 제품 가져오기
for category_link in category_links:
    print(f"카테고리 접속 중: {category_link}")
    driver.get(category_link)
    random_sleep()
    
    # 정렬을 '높은 평점'으로 변경
    try:
        sort_button = wait_for_element("button[data-testid='sort-by-button']", timeout=10)
        if sort_button:
            sort_button.click()
            print("정렬 옵션 클릭 중...")
            time.sleep(2)
            high_rating_option = wait_for_element("//li[@data-value='Rating']", by=By.XPATH, timeout=10)
            if high_rating_option:
                high_rating_option.click()
                print("높은 평점 옵션 선택 중...")
                random_sleep()
            else:
                print("높은 평점 옵션을 찾지 못했습니다.")
                continue
        else:
            print("정렬 버튼을 찾지 못했습니다.")
            continue
    except Exception as e:
        print(f"정렬 옵션 설정 중 오류 발생: {e}")
        continue

    # 상위 3개의 제품 가져오기
    try:
        products = wait_for_element("div.product-container", timeout=10)
        if products:
            products = driver.find_elements(By.CSS_SELECTOR, "div.product-container")[:3]
            print(f"상위 3개 제품 발견: {len(products)}개")
            for product in products:
                title = product.find_element(By.CSS_SELECTOR, "a.product-link").text
                rating = product.find_element(By.CSS_SELECTOR, "span.stars").get_attribute("title")
                link = product.find_element(By.CSS_SELECTOR, "a.product-link").get_attribute("href")
                print(f"제목: {title}, 평점: {rating}, 링크: {link}")
        else:
            print("제품 정보를 찾지 못했습니다.")
    except Exception as e:
        print(f"제품 정보 가져오기 중 오류 발생: {e}")

# 브라우저 닫기
driver.quit()
print("크롤링 완료, 브라우저 닫음.")


# DevTools listening on ws://127.0.0.1:4528/devtools/browser/9ebdee93-c0d2-42cd-b534-c9dc3a9ac834
# 접속 중: https://kr.iherb.com/c/supplements
# 요소 대기 중 오류 발생 div#mainContent: Message:
# Stacktrace:
#         GetHandleVerifier [0x00DFB793+45827]
#         (No symbol) [0x00D8DB74]
#         (No symbol) [0x00C8150F]
#         (No symbol) [0x00CC20BC]
#         (No symbol) [0x00CC216B]
#         (No symbol) [0x00CFE0F2]
#         (No symbol) [0x00CE2E44]
#         (No symbol) [0x00CFC034]
#         (No symbol) [0x00CE2B96]
#         (No symbol) [0x00CB6998]
#         (No symbol) [0x00CB751D]
#         GetHandleVerifier [0x010B43C3+2899763]
#         GetHandleVerifier [0x011077ED+3240797]
#         GetHandleVerifier [0x00E81264+593364]
#         GetHandleVerifier [0x00E8818C+621820]
#         (No symbol) [0x00D96F54]
#         (No symbol) [0x00D93658]
#         (No symbol) [0x00D937F7]
#         (No symbol) [0x00D858AE]
#         BaseThreadInitThunk [0x76C2FCC9+25]
#         RtlGetAppContainerNamedObjectPath [0x77DF7CBE+286]
#         RtlGetAppContainerNamedObjectPath [0x77DF7C8E+238]

# 요소 대기 중 오류 발생 div.subCategory: Message:
# Stacktrace:
#         GetHandleVerifier [0x00DFB793+45827]
#         (No symbol) [0x00D8DB74]
#         (No symbol) [0x00C8150F]
#         (No symbol) [0x00CC20BC]
#         (No symbol) [0x00CC216B]
#         (No symbol) [0x00CFE0F2]
#         (No symbol) [0x00CE2E44]
#         (No symbol) [0x00CFC034]
#         (No symbol) [0x00CE2B96]
#         (No symbol) [0x00CB6998]
#         (No symbol) [0x00CB751D]
#         GetHandleVerifier [0x010B43C3+2899763]
#         GetHandleVerifier [0x011077ED+3240797]
#         GetHandleVerifier [0x00E81264+593364]
#         GetHandleVerifier [0x00E8818C+621820]
#         (No symbol) [0x00D96F54]
#         (No symbol) [0x00D93658]
#         (No symbol) [0x00D937F7]
#         (No symbol) [0x00D858AE]
#         BaseThreadInitThunk [0x76C2FCC9+25]
#         RtlGetAppContainerNamedObjectPath [0x77DF7CBE+286]
#         RtlGetAppContainerNamedObjectPath [0x77DF7C8E+238]

# 페이지 로드 중 오류 발생