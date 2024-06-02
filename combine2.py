import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import os
import json
import hmac
import hashlib
from time import gmtime, strftime
import csv

# BMI 지수 계산하는 함수
def calculate_bmi(weight, height):
    return weight / ((height / 100) ** 2)

# PA 지수 계산하는 함수
def calculate_pa_index(gender, pa_level):
    if gender == "여자":
        return [1.0, 1.12, 1.27, 1.45][pa_level-1]
    elif gender == "남자":
        return [1.0, 1.11, 1.25, 1.48][pa_level-1]
    return None

# 사용자로부터 정보를 입력받는 함수
def get_user_info():
    print("사용자 정보를 입력해주세요.")
    gender = input("성별을 입력하세요 (남자 or 여자): ")
    age = int(input("나이를 입력하세요: "))
    height = float(input("키를 입력하세요 (cm): "))
    weight = float(input("몸무게를 입력하세요 (kg): "))
    pa_level = int(input("PA 지수를 입력하세요 (1: 비활동적, 2: 저활동적, 3: 활동적, 4: 매우 활동적): "))
    
    # 질병 유무 입력 받기
    diseases = {
        "고혈압": False,
        "당뇨병": False,
        "위암": False,
        "대장암": False,
        "고지혈증": False,
        "골다공증": False
    }
    
    for disease in diseases.keys():
        response = input(f"{disease} 유무를 입력하세요 (유 or 무): ").strip().lower()
        diseases[disease] = response == "유"
    
    bmi = calculate_bmi(weight, height)
    pa_index = calculate_pa_index(gender, pa_level)
    
    return gender, age, height, weight, bmi, pa_index, diseases

# 권장 섭취량 계산하는 함수 (논문표 참고. 평균필요량 수식 -> 섭취기준량 수식)
def calculate_average_requirements(gender, age, pa_index, weight, height, diseases):
    if gender not in ["남자", "여자"]:
        return None

    if gender == "남자":
        energy = 662 - 9.53 * age + pa_index * (15.91 * weight + 539.6 * (height / 100))
    elif gender == "여자":
        energy = 354 - 6.91 * age + pa_index * (9.36 * weight + 726 * (height / 100))

    carbohydrate = (energy * 0.6) / 4
    protein = (energy * 0.135) / 4
    fat = (energy * 0.225) / 9

    if gender == "남자":
        if 1 <= age <= 2:
            calcium, iron, potassium = 500, 6, 2000
            vitamin_a, thiamine, niacin = 250, 0.5, 6
            vitamin_c, vitamin_d, magnesium = 40, 5, 80
            vitamin_b9, vitamin_b12 = 150, 0.9
        elif 3 <= age <= 5:
            calcium, iron, potassium = 600, 7, 2300
            vitamin_a, thiamine, niacin = 300, 0.5, 7
            vitamin_c, vitamin_d, magnesium = 45, 5, 100
            vitamin_b9, vitamin_b12 = 180, 1.1
        elif 6 <= age <= 8:
            calcium, iron, potassium = 700, 9, 2600
            vitamin_a, thiamine, niacin = 450, 0.7, 9
            vitamin_c, vitamin_d, magnesium = 50, 5, 160
            vitamin_b9, vitamin_b12 = 220, 1.3
        elif 9 <= age <= 11:
            calcium, iron, potassium = 800, 11, 3000
            vitamin_a, thiamine, niacin = 600, 0.9, 11
            vitamin_c, vitamin_d, magnesium = 70, 5, 230
            vitamin_b9, vitamin_b12 = 300, 1.7
        elif 12 <= age <= 14:
            calcium, iron, potassium = 1000, 14, 3500
            vitamin_a, thiamine, niacin = 750, 1.1, 15
            vitamin_c, vitamin_d, magnesium = 90, 10, 320
            vitamin_b9, vitamin_b12 = 360, 2.3
        elif 15 <= age <= 18:
            calcium, iron, potassium = 900, 14, 3500
            vitamin_a, thiamine, niacin = 850, 1.3, 17
            vitamin_c, vitamin_d, magnesium = 100, 10, 400
            vitamin_b9, vitamin_b12 = 400, 2.4
        elif 19 <= age <= 29:
            calcium, iron, potassium = 800, 10, 3500
            vitamin_a, thiamine, niacin = 800, 1.2, 16
            vitamin_c, vitamin_d, magnesium = 100, 10, 350
            vitamin_b9, vitamin_b12 = 400, 2.4
        elif 30 <= age <= 49:
            calcium, iron, potassium = 800, 10, 3500
            vitamin_a, thiamine, niacin = 800, 1.2, 16
            vitamin_c, vitamin_d, magnesium = 100, 10, 370
            vitamin_b9, vitamin_b12 = 400, 2.4
        elif 50 <= age <= 64:
            calcium, iron, potassium = 750, 10, 3500
            vitamin_a, thiamine, niacin = 750, 1.2, 16
            vitamin_c, vitamin_d, magnesium = 100, 10, 370
            vitamin_b9, vitamin_b12 = 400, 2.4
        elif 65 <= age <= 74:
            calcium, iron, potassium = 700, 9, 3500
            vitamin_a, thiamine, niacin = 700, 1.2, 14
            vitamin_c, vitamin_d, magnesium = 100, 15, 370
            vitamin_b9, vitamin_b12 = 400, 2.4
        elif 75 <= age:
            calcium, iron, potassium = 700, 9, 3500
            vitamin_a, thiamine, niacin = 700, 1.2, 13
            vitamin_c, vitamin_d, magnesium = 100, 15, 370
            vitamin_b9, vitamin_b12 = 400, 2.4
        else:
            return None
    elif gender == "여자":
        if 1 <= age <= 2:
            calcium, iron, potassium = 500, 6, 2000
            vitamin_a, thiamine, niacin = 250, 0.5, 6
            vitamin_c, vitamin_d, magnesium = 40, 5, 70
            vitamin_b9, vitamin_b12 = 150, 0.9
        elif 3 <= age <= 5:
            calcium, iron, potassium = 600, 7, 2300
            vitamin_a, thiamine, niacin = 300, 0.5, 7
            vitamin_c, vitamin_d, magnesium = 45, 5, 110
            vitamin_b9, vitamin_b12 = 180, 1.1
        elif 6 <= age <= 8:
            calcium, iron, potassium = 700, 9, 2600
            vitamin_a, thiamine, niacin = 400, 0.7, 9
            vitamin_c, vitamin_d, magnesium = 50, 5, 150
            vitamin_b9, vitamin_b12 = 220, 1.3
        elif 9 <= age <= 11:
            calcium, iron, potassium = 800, 10, 3000
            vitamin_a, thiamine, niacin = 550, 0.9, 12
            vitamin_c, vitamin_d, magnesium = 70, 5, 220
            vitamin_b9, vitamin_b12 = 300, 1.7
        elif 12 <= age <= 14:
            calcium, iron, potassium = 900, 16, 3500
            vitamin_a, thiamine, niacin = 650, 1.1, 15
            vitamin_c, vitamin_d, magnesium = 90, 10, 290
            vitamin_b9, vitamin_b12 = 360, 2.3
        elif 15 <= age <= 18:
            calcium, iron, potassium = 800, 14, 3500
            vitamin_a, thiamine, niacin = 650, 1.2, 14
            vitamin_c, vitamin_d, magnesium = 100, 10, 340
            vitamin_b9, vitamin_b12 = 400, 2.4
        elif 19 <= age <= 29:
            calcium, iron, potassium = 700, 14, 3500
            vitamin_a, thiamine, niacin = 650, 1.1, 14
            vitamin_c, vitamin_d, magnesium = 100, 10, 280
            vitamin_b9, vitamin_b12 = 400, 2.4
        elif 30 <= age <= 49:
            calcium, iron, potassium = 700, 14, 3500
            vitamin_a, thiamine, niacin = 650, 1.1, 14
            vitamin_c, vitamin_d, magnesium = 100, 10, 280
            vitamin_b9, vitamin_b12 = 400, 2.4
        elif 50 <= age <= 64:
            calcium, iron, potassium = 800, 8, 3500
            vitamin_a, thiamine, niacin = 600, 1.1, 14
            vitamin_c, vitamin_d, magnesium = 100, 10, 280
            vitamin_b9, vitamin_b12 = 400, 2.4
        elif 65 <= age <= 74:
            calcium, iron, potassium = 800, 8, 3500
            vitamin_a, thiamine, niacin = 600, 1.1, 13
            vitamin_c, vitamin_d, magnesium = 100, 15, 280
            vitamin_b9, vitamin_b12 = 400, 2.4
        elif 75 <= age:
            calcium, iron, potassium = 800, 8, 3500
            vitamin_a, thiamine, niacin = 600, 1.1, 12
            vitamin_c, vitamin_d, magnesium = 100, 15, 280
            vitamin_b9, vitamin_b12 = 400, 2.4
        else:
            return None

    # 질병에 따른 조정
    if diseases["고혈압"]:
        if age >= 19:
            calcium, potassium = 1000, 4700
            magnesium = 420 if gender == "남자" else 320
    if diseases["당뇨병"]:
        if age <= 50:
            calcium = 1000
            magnesium = 420 if gender == "남자" else 320
        else:
            calcium = 1200
            magnesium = 420
    if diseases["위암"] or diseases["대장암"]:
        if age <= 50:
            calcium = 1000
        else:
            calcium = 1200

    return energy, carbohydrate, protein, fat, calcium, iron, potassium, vitamin_a, thiamine, niacin, vitamin_c, vitamin_d, magnesium, vitamin_b9, vitamin_b12
supplements = {
    '단백질(g)': ['뉴트리하루 프리미엄 초고함량 류신 단백질 타블렛 노인 보충제 120정 4개(25,900원)', '뉴트리하루 프리미엄 초고함량 류신 단백질 타블렛 노인 보충제 120정 1개(12,900원)', '뉴트리디데이 프리미엄 류신 단백질 54g 90정 1개(15,900원)', '[런칭 특가] 산양유 초유 류신 단백질 식약처 HACCP 인증 L-로이신 프로틴 정 입점 할인가 90정 1개(33,950원)', '웰핏 고단백 초유 산양유 콜라겐 단백질 500g 3개(34,000원)', '히이즈 류신 타블렛 단백질 60정 1개(47,600원)', '픽커스 류신 단백질 타블렛 프리미엄 정 1000mg 60정 60g 3개(25,900원)', '뉴트리하루 프리미엄 초고함량 류신 단백질 타블렛 노인 보충제 120정 1개(31,650원)', '하이뮨 마시는 프로틴 밸런스 125ml 36개(47,600원)', '[빌립푸드] 류신 단백질 프리미엄 6 000mg 60정 3개(52,200원)'],
    '칼슘(mg)': ['종근당 칼슘 앤 마그네슘 플러스 비타민D 180정 6개(40,200원)', '종근당 칼슘앤 마그네슘 플러스 비타민D (3개월분) 뼈건강 식물성 해조칼슘 3중복합 180정 4개(21,300원)', '종근당 칼슘 앤 마그네슘 비타민D 아연 180정 2개(11,400원)', '종근당 칼슘 앤 마그네슘 비타민D 아연 180정 1개(24,770원)', '센트룸 칼슘+D 미니 120g 120정 1개(78,630원)', '뉴트리원 흡수빠른 어골칼슘 칼슘 마그네슘 비타민D 아연 활력환 기획세트 60정 6개(31,830원)', '닥터린 WCS 관절연골엔 식물성 MSM 어골칼슘 DK 121.5g 1개(17,040원)', '한국야쿠르트 브이푸드 칼슘 120정 1개(41,100원)', '종근당 칼슘 앤 마그네슘 비타민D 아연 180정 4개(196,000원)', '뼈엔 엠비피 유단백추출물 MBP 30캡슐 30정 130mg 10ml 5개(19,800원)'],
    '철(mg)':  ['닥터루템 헤모어 철분 빈혈 비헴철 철분제 90정 2개(19,900원)', '올바른 프리미엄 철분 90정 2개(10,490원)', '종근당 철분 엽산 비타민D 플러스 60정 1개(28,000원)', '솔가 철분 25 90캡슐 1개(26,540원)', '종근당 철분 엽산 비타민D 플러스 60정 3개(24,900원)', '일양약품 리얼메디 엽산 철분 구리 헤모철 플러스 철분제 아연 엽산제 비타민 D B12 영양제 180정 1개(45,900원)', '여성 남성 빈혈 고함량 철분제 어지럼증에 좋은 영양제 3박스 90정(51,400원)', '솔가 철분 25 180캡슐 1개(10,130원)', '나우푸드 철분 18mg 베지 캡슐 120정 1개(94,120원)', '닥터웰퀸즈 알파 액상철분 10ml x 30포 300ml 6개(20,170원)'],
    '칼륨(mg)': ['뉴트리디데이 프리미엄 칼륨 포타슘 1400 120정 1개(37,900원)', '닥터하이 365 부기부기 칼륨 포타슘 1000mg x 90정 1개(12,200원)', 'JW중외제약 워터 밸런스 칼륨 포타슘 120g 120정 1개(10,900원)', '뉴트리디데이 프리미엄 칼륨 포타슘 1400 120정 1개(14,380원)', '비타민마을 와이즈 칼륨 120정 1개(21,900원)', '뉴트리디데이 프리미엄 포스파티딜세린 40g 50정 1개(13,000원)', '동화약품 하루 3알 수분 균형 구연산 칼륨 포타슘 영양제 144g 1개 90정(13,000원)', '나우푸드 포타슘 시트레이트 99mg 캡슐 1개 180정(22,910원)', '나우푸드 포타슘 시트레이트 99mg 캡슐 2개 180정(26,550원)', '얼라이브 원스데일리 포맨 멀티비타민 80정 1개(38,900원)'],
    '비타민 A(μg RAE)': ['GNM 건조한 눈엔 루테인오메가3 눈건강 비타민A 비타민E 150정 1개(27,300원)', '토비콤 안국약품 아이포커스 미니 헤마토코쿠스 추출물 비타민 A 2.4g 30정 3개(10,810원)', '스완슨 비타민 A 10000IU 소프트젤 250정 1개(7840원)', '나우푸드 A 10000IU & D 400IU 소프트젤 글루텐 프리 1개 100정(22,970원)', '뉴트리코스트 비타민 A 10000IU 소프트젤 글루텐 프리 500정 1개(26,550원)', '얼라이브 원스데일리 포맨 멀티비타민 80정 1개(18,700원)', '토비콤 안국약품 아이포커스 미니 헤마토코쿠스 추출물 비타민 A 2.4g 30정 2개(10,870원)', '스완슨 베타 카로틴 비타민 A 10000IU 소프트젤 1개 250정(37,800원)', '애플트리김약사네 눈건강 비타민A 2개 135g(23,900원)', '일양약품 눈건강 루테인 골드 15g 30정 4개(34,020원)'],
    '티아민(mg)': ['닥터트루 프리미엄 비타민B 컴플렉스 B1 B2 B6 B12 영양제 수용성 비타민비 5박스 60정(33,000원)', '고함량 마그네슘 비타민B 영양제 활력 에너지 보충 신경 근육 기능 유지 영양제 알약케이스 증정 90정 1개(9410원)', '나우푸드 B-1 100mg 타블렛 1개 100정(11,820원)', '종근당 활력 비타민B 플러스 60정 1개(9900원)', '뉴트리디데이 프리미엄 비타민B 컴플렉스 골드 90정 1개(66,000원)', 'YDY 오마비 세트 (오메가3+마그네슘+비타민B) 1개(68,900원)', '활력비타민b 고함량비타민b 8가지 복합 활력 비타민b b1 b2 b6 b12 비오틴 엽산 판토텐산 90정 3개(32,460원)', '종근당 활력 비타민B 플러스 60정 3개(12260원)', '셀트리온 이너랩 액티브 활력 비타민B 콤플렉스 30g 60정 1개(65,500원)', '미국산 고함량 마그네슘 비타민B 신경 근육 기능 유지 눈떨림 영양제 사은품 증정 90정 2개(24,900원)'],
    '니아신(mg)': ['YDY 액티브비큐텐 60정 x 2 비타민B군 코엔자임Q10 2개(48,000원)', '고려은단 메가도스B 비타민B 컴플렉스 60정 3개(20,400원)', '뉴트리코스트 나이아신아마이드 비타민 B3 500mg 글루텐 프리 캡슐 240정 1개(11,820원)', '종근당 활력 비타민B 플러스 60정 1개(21,600원)', '라이프익스텐션 비타민 B3 나이아신 500mg 100정 니아신 Vitamin B3 Niacin 2개 100캡슐(20,400원)', '뉴트리코스트 나이아신아마이드 비타민 B3 500mg 글루텐 프리 캡슐 240정 1개(24,900원)', '뉴트리디데이 프리미엄 비타민B 컴플렉스 골드 90정 3개(20,570원)', '뉴트리코스트 니아신 비타민B3 240정 1개(32,460원)', '종근당 활력 비타민B 플러스 60정 3개(23,900원)', '일양약품 눈건강 루테인 골드 15g 30정 4개(22,140원)'],
    '비타민 C(mg)': ['휴온스 메리트C산 3000mg 270g 2개(38,610원)', '바노 이왕재 박사 메가 비타민C 3000mg 90p 270g 1박스(10,700원)', '종근당 비타민C 200정 1개(18,000원)', '고려은단 비타민C 1000 + 쇼핑백 180정 1개(28,540원)', '종근당 비타민C 600정 1개(116,050원)', '닥터에스더 리포좀 비타민C 플러스 5개 30정 30개(45,900원)', '고려은단 비타민C1000 이지 + 비타민D UPGRADE 180정 3개(44,900원)', '고려은단 비타민C 1000 600정 1개(33,900원)', '고려은단 비타민C 1000 + 쇼핑백 180정 2개(143,600원)', '바노 이왕재 박사 메가 비타민C 2000mg (4박스) 12개월분 4박스 2g(21,160원)'],
    '비타민 D(μg)': ['뉴트리원 흡수율 높은 비타민D3 3000IU 초소형캡슐 DSM사 비타민D 활력환 기획세트 60정 6개(23,120원)', '뼈건강에 이롭 비타민D 5000IU 2개 180정(12,500원)', '뉴트리가든 비타민D3 5000IU 180정 1개(21,300원)', '종근당 칼슘 앤 마그네슘 비타민D 아연 180정 2개(21,470원)', '종근당건강 비타민D 2000IU 90정 2개(34,900원)', '차바이오 닥터프로그램 마더스 츄어블 비타민D 4000IU 12개월분 비타민D 60정 6개(25,900원)', 'JW중외제약 리얼메디 비타민D 4000IU 츄어블 총2통 총6개월 비타민D-3 비타민 D3 비타민디 비타민디3 2박스 90정(10,780원)', '종근당건강 90정 1개', '솔가 비타민 D3 1000 IU 90정 1개(22,500원)', '솔가 비타민 D3 1000 IU 90정 1개(23,900원)', '차바이오 닥터프로그램 마더스 츄어블 비타민D 4000IU 8개월분 비타민D 60정 4개(10,900원)'],
    '마그네슘(㎎)': ['한미양행 프리미엄 마그네슘400 90정 2개(51,500원)', '익스트림 트리플 마그네슘 1100mg (4개월분) 120정 2개(11,400원)', '종근당 칼슘 앤 마그네슘 비타민D 아연 180정 1개(14,610원)', '세노비스 마그네슘 90정 1개(21,300원)', '종근당 칼슘 앤 마그네슘 비타민D 아연 180정 2개(34,000원)', '뉴트리코어 WCS 마그네슘 비타민D NOCHESTEM 81g 60정 1개(14,610원)', '세노비스 마그네슘 90정 1개(16,720원)', '나우푸드 마그네슘 캡 400mg 베지 캡슐 180정 1개(25,900원)', '솔가 마그네슘 위드 비타민 B6 100정 1개(24,700원)', '일양약품 액티브 마그네슘 플러스 비타민D 96g 120정 2개(27,720원)'],
    '비타민 B9(μg)': '엽산 보충제',
    '비타민 B12(μg)': '비타민 B12 보충제'
}

# 사용자 정보 받기
gender, age, height, weight, bmi, pa_index, diseases = get_user_info()

# 영양소별 권장 섭취량 산출
requirements = calculate_average_requirements(gender, age, pa_index, weight, height, diseases)
if requirements is None:
    print("잘못된 입력 값으로 인해 권장 섭취량을 계산할 수 없습니다.")
    exit()

energy_avg, carbohydrate_avg, protein_avg, fat_avg, calcium_avg, iron_avg, potassium_avg, vitamin_a_avg, thiamine_avg, niacin_avg, vitamin_c_avg, vitamin_d_avg, magnesium_avg, vitamin_b9_avg, vitamin_b12_avg = requirements

# 권장 섭취량 결과값들을 need 리스트에 저장
need = [
    energy_avg,
    protein_avg,
    fat_avg,
    carbohydrate_avg,
    calcium_avg,
    iron_avg,
    potassium_avg,
    vitamin_a_avg,
    thiamine_avg,
    niacin_avg,
    vitamin_c_avg,
    vitamin_d_avg,
    magnesium_avg,
    vitamin_b9_avg,
    vitamin_b12_avg
]

# 엑셀 파일에서 식품 영양 정보를 불러오는 함수
def load_nutrition_data(file_path):
    if not os.path.exists(file_path):
        print(f"파일이 존재하지 않습니다: {file_path}")
        return None
    return pd.read_excel(file_path)

# 엑셀 파일에서 식품 영양 정보를 불러오기
file_path = 'data/식품영양성분DB_음식_20240416.xlsx'
nutrition_data = load_nutrition_data(file_path)
if nutrition_data is None:
    print("영양성분 데이터를 불러올 수 없습니다.")
    exit()

# 추가적인 영양 정보가 있는 엑셀 파일 불러오기
additional_file_path = 'data/식품영양성분DB_가공식품_20240416.xlsx'
additional_nutrition_data = load_nutrition_data(additional_file_path)
if additional_nutrition_data is None:
    print("추가 영양성분 데이터를 불러올 수 없습니다.")
    exit()

# 두 데이터 프레임을 합침
combined_nutrition_data = pd.concat([nutrition_data, additional_nutrition_data], ignore_index=True)

def get_daily_menu():
    menu = re.split(r',\s*|\s*,\s*', input("식단을 입력하세요 (예: 김밥_참치, 짬뽕밥, 오므라이스): "))
    quantities = []
    for food in menu:
        quantity = float(input(f"{food}의 섭취량을 입력하세요 (g): "))
        quantities.append(quantity)
    return menu, quantities

# 식단의 각 영양소 값을 찾아내는 함수
def find_nutrition_values(menu, quantities, combined_nutrition_data):
    nutrition_values = {}
    for food, quantity in zip(menu, quantities):
        food_info = combined_nutrition_data[combined_nutrition_data['식품명'] == food]
        if not food_info.empty:
            for nutrient in ['에너지(kcal)', '단백질(g)', '지방(g)', '탄수화물(g)', '칼슘(mg)', '철(mg)', '칼륨(mg)', '비타민 A(μg)', '티아민(mg)', '니아신(mg)', '비타민 C(mg)', '비타민 D(μg)', '마그네슘(㎎)','비타민 B9(μg)', '비타민 B12(μg)']:
                if nutrient in food_info.columns:
                    nutrient_value = food_info[nutrient].iloc[0]
                    if isinstance(nutrient_value, str):
                        nutrient_value = pd.to_numeric(nutrient_value, errors='coerce')
                    if pd.notnull(nutrient_value):
                        adjusted_value = nutrient_value * (quantity / 100)
                        nutrition_values[nutrient] = nutrition_values.get(nutrient, 0) + adjusted_value
        else:
            food_info = additional_nutrition_data[additional_nutrition_data['식품명'] == food]
            if not food_info.empty:
                for nutrient in ['에너지(kcal)', '단백질(g)', '지방(g)', '탄수화물(g)', '칼슘(mg)', '철(mg)', '칼륨(mg)', '비타민 A(μg)', '티아민(mg)', '니아신(mg)', '비타민 C(mg)', '비타민 D(μg)', '마그네슘(㎎)','비타민 B9(μg)', '비타민 B12(μg)']:
                    if nutrient in food_info.columns:
                        nutrient_value = food_info[nutrient].iloc[0]
                        if isinstance(nutrient_value, str):
                            nutrient_value = pd.to_numeric(nutrient_value, errors='coerce')
                        if pd.notnull(nutrient_value):
                            adjusted_value = nutrient_value * (quantity / 100)
                            nutrition_values[nutrient] = nutrition_values.get(nutrient, 0) + adjusted_value
    return nutrition_values

# 하루 식단과 섭취량 입력받기
total_nutrition_values = {}
for i in range(7):
    print(f"{i+1}일차 식단을 입력하세요.")
    menu, quantities = get_daily_menu()
    nutrition_values = find_nutrition_values(menu, quantities, combined_nutrition_data)
    for nutrient, value in nutrition_values.items():
        total_nutrition_values[nutrient] = total_nutrition_values.get(nutrient, 0) + value

# 평균 값 계산
average_nutrition_values = {nutrient: value / 7 for nutrient, value in total_nutrition_values.items()}

# 실제 영양소 섭취량 결과값들을 real 리스트에 저장
real = list(average_nutrition_values.values())

# gap 리스트 값 계산
gap = [need_val - real_val for need_val, real_val in zip(need, real)]

def get_deficient_nutrients(gap, nutrients):
    deficient_nutrients = []
    for nutrient, diff in zip(['에너지(kcal)', '단백질(g)', '지방(g)', '탄수화물(g)', '칼슘(mg)', '철(mg)', '칼륨(mg)', '비타민 A(μg RAE)', '티아민(mg)', '니아신(mg)', '비타민 C(mg)', '비타민 D(μg)', '마그네슘(㎎)','비타민 B9(μg)', '비타민 B12(μg)'], gap):
        if diff > 0:
            if nutrient in supplements:
                supplement_info = supplements[nutrient]
                if isinstance(supplement_info, list):  # 보충제 정보가 리스트 형태일 경우
                    print(f"{nutrient}을(를) {diff:.2f} 부족하게 섭취했습니다. 고로 {nutrient}와 관련된 영양제 TOP10을 추천해드리겠습니다. 추천 영양제는 아래와 같습니다.")
                    for supplement in supplement_info:  # 리스트 내의 각 항목을 별도로 출력
                        print(supplement)
                else:  # 보충제 정보가 단일 문자열일 경우
                    print(f"{nutrient}을(를) {diff:.2f} 부족하게 섭취했습니다. 고로 {nutrient}와 관련된 영양제 TOP10을 추천해드리겠습니다. 추천 영양제는 아래와 같습니다.\n{supplement_info}")
            else:
                print(f"{nutrient}을(를) {diff:.2f} 부족하게 섭취했습니다. 해당 영양소에 대한 보충제는 없습니다.")
            deficient_nutrients.append(nutrient)  # 부족한 영양소 리스트에 추가
        elif diff < 0:
            print(f"{nutrient}을(를) {abs(diff):.2f} 과도하게 섭취했습니다.")
        else:
            print(f"{nutrient}을(를) 적절하게 섭취했습니다.")
            print()
    return deficient_nutrients  # 부족한 영양소 리스트 반환

nutrients = ['에너지(kcal)', '단백질(g)', '지방(g)', '탄수화물(g)', '칼슘(mg)', '철(mg)', '칼륨(mg)', '비타민 A(μg RAE)', '티아민(mg)', '니아신(mg)', '비타민 C(mg)', '비타민 D(μg)', '마그네슘(㎎)','비타민 B9(μg)', '비타민 B12(μg)']
# 부족한 영양소 구하기
deficient_nutrients = get_deficient_nutrients(gap, nutrients)

print("\n<부족한 영양소>")
for nutrient in deficient_nutrients:
    print(f"{nutrient}을(를) 부족하게 섭취했습니다.")


# 특정 영양소만 검색어로 변환
searchable_nutrients = {
    '단백질(g)': '단백질 영양제',
    '칼슘(mg)': '칼슘 영양제',
    '티아민(mg)': '티아민 영양제',
    '니아신(mg)': '니아신 영양제',
    '비타민 A(μg RAE)': '비타민 A 영양제',
    '비타민 B9(μg)': '비타민 B 영양제',
    '비타민 B12(μg)': '비타민 B 영양제',
    '비타민 C(mg)': '비타민 C 영양제',
    '비타민 D(μg)': '비타민 D 영양제',
    '마그네슘(㎎)': '마그네슘 영양제',
    '칼륨(mg)': '칼륨 영양제'
}

keywords = [searchable_nutrients[nutrient] for nutrient in deficient_nutrients if nutrient in searchable_nutrients]

def coupang_search(keyword):
    target_url = f'https://www.coupang.com/np/search?component=&q={keyword}&channel=user'
    headers = {
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6,zh;q=0.5',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
        'Accept-Encoding': 'gzip'
    }
    res = requests.get(url=target_url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    products = soup.select('li.search-product')
    results = []

    for product in products[:10]:
        name = product.select_one('div > div.name').text.strip()
        price = product.select_one('div.price-wrap > div.price > em > strong').text.strip().replace(",", "")
        review = re.sub("[()]", "", product.select_one('div.other-info > div > span.rating-total-count').text.strip())
        link = "https://www.coupang.com" + product.select_one('a.search-product-link')['href'].strip()
        image = product.select_one('dt > img').get('data-img-src') or product.select_one('dt > img').get('src').replace("//", "")
        
        results.append([keyword, name, price, review, image, link])

    # 파일 저장
    output_dir = 'C:/Users/samsung/Desktop/s/capstone/capstone-design-2024'
    output_file = os.path.join(output_dir, 'search_results.csv')

    os.makedirs(output_dir, exist_ok=True)

    with open(output_file, 'a', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        for result in results:
            writer.writerow(result)

# CSV 파일 초기화
output_dir = 'C:/Users/samsung/Desktop/s/capstone/capstone-design-2024'
output_file = os.path.join(output_dir, 'search_results.csv')
with open(output_file, 'w', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(["검색어", "상품명", "상품가격", "상품 리뷰수", "상품 이미지", "판매 링크"])

# 각 부족 영양소에 대해 검색 수행 및 결과 저장
for keyword in keywords:
    coupang_search(keyword)

print("최종 검색 결과가 CSV 파일에 저장되었습니다.")