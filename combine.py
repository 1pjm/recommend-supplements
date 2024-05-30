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
    for nutrient, diff in zip(nutrients, gap):
        if diff > 0:
            deficient_nutrients.append(nutrient)
    return deficient_nutrients

nutrients = ['에너지(kcal)', '단백질(g)', '지방(g)', '탄수화물(g)', '칼슘(mg)', '철(mg)', '칼륨(mg)', '비타민 A(μg RAE)', '티아민(mg)', '니아신(mg)', '비타민 C(mg)', '비타민 D(μg)', '마그네슘(㎎)','비타민 B9(μg)', '비타민 B12(μg)']
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
