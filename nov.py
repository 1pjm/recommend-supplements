import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import pandas as pd

# BMI 지수 계산하는 함수
def calculate_bmi(weight, height):
    bmi = weight / ((height / 100) ** 2)
    return bmi

# PA 지수 계산하는 함수
def calculate_pa_index(gender, pa_level):
    if gender == "여자":
        if pa_level == 1:
            return 1.0
        elif pa_level == 2:
            return 1.12
        elif pa_level == 3:
            return 1.27
        elif pa_level == 4:
            return 1.45
    elif gender == "남자":
        if pa_level == 1:
            return 1.0
        elif pa_level == 2:
            return 1.11
        elif pa_level == 3:
            return 1.25
        elif pa_level == 4:
            return 1.48
    else:
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
        if response == "유":
            diseases[disease] = True
    
    bmi = calculate_bmi(weight, height)
    pa_index = calculate_pa_index(gender, pa_level)
    
    return gender, age, height, weight, bmi, pa_index, diseases
    
    
# 권장 섭취량 계산하는 함수 (논문표 참고. 평균필요량 수식 -> 섭취기준량 수식)
def calculate_average_requirements(gender, age, pa_index, weight, height,diseases):
    # 권장 섭취량 계산하는 함수 (논문표 참고. 평균필요량 수식 -> 섭취기준량 수식)
    if gender == "남자":
        energy = 662 - 9.53 * age + pa_index * (15.91 * weight + 539.6 * (height / 100))
    elif gender == "여자":
        energy = 354 - 6.91 * age + pa_index * (9.36 * weight + 726 * (height / 100))
    else:
        return None

    carbohydrate = (energy * 0.6) / 4
    protein = (energy * 0.135) / 4
    fat = (energy * 0.225) / 9
    if gender == "남자":
        if 1 <= age <= 2:
            calcium = 500
            iron = 6
            potassium = 2000
            vitamin_a = 250
            thiamine = 0.5
            niacin = 6
            vitamin_c = 40
            vitamin_d = 5
            magnesium = 80
            vitamin_b9 = 150
            vitamin_b12 = 0.9
        elif 3 <= age <= 5:
            calcium = 600
            iron = 7
            potassium = 2300
            vitamin_a = 300
            thiamine = 0.5
            niacin = 7
            vitamin_c = 45
            vitamin_d = 5
            magnesium = 100
            vitamin_b9 = 180
            vitamin_b12 = 1.1
        elif 6 <= age <= 8:
            calcium = 700
            iron = 9
            potassium = 2600
            vitamin_a = 450
            thiamine = 0.7
            niacin = 9
            vitamin_c = 50
            vitamin_d = 5
            magnesium = 160
            vitamin_b9 = 220
            vitamin_b12 = 1.3
        elif 9 <= age <= 11:
            calcium = 800
            iron = 11
            potassium = 3000
            vitamin_a = 600
            thiamine = 0.9
            niacin = 11
            vitamin_c = 70
            vitamin_d = 5
            magnesium = 230
            vitamin_b9 = 300
            vitamin_b12 = 1.7
        elif 12 <= age <= 14:
            calcium = 1000
            iron = 14
            potassium = 3500
            vitamin_a = 750
            thiamine = 1.1
            niacin = 15
            vitamin_c = 90
            vitamin_d = 10
            magnesium = 320
            vitamin_b9 = 360
            vitamin_b12 = 2.3
        elif 15 <= age <= 18:
            calcium = 900
            iron = 14
            potassium = 3500
            vitamin_a = 850
            thiamine = 1.3
            niacin = 17
            vitamin_c = 100
            vitamin_d = 10
            magnesium = 400
            vitamin_b9 = 400
            vitamin_b12 = 2.4
        elif 19 <= age <= 29:
            calcium = 800
            iron = 10
            potassium = 3500
            vitamin_a = 800
            thiamine = 1.2
            niacin = 16
            vitamin_c = 100
            vitamin_d = 10
            magnesium = 350
            vitamin_b9 = 400
            vitamin_b12 = 2.4
        elif 30 <= age <= 49:
            calcium = 800
            iron = 10
            potassium = 3500
            vitamin_a = 800
            thiamine = 1.2
            niacin = 16
            vitamin_c = 100
            vitamin_d = 10
            magnesium = 370
            vitamin_b9 = 400
            vitamin_b12 = 2.4
        elif 50 <= age <= 64:
            calcium = 750
            iron = 10
            potassium = 3500
            vitamin_a = 750
            thiamine = 1.2
            niacin = 16
            vitamin_c = 100
            vitamin_d = 10
            magnesium = 370
            vitamin_b9 = 400
            vitamin_b12 = 2.4
        elif 65 <= age <= 74:
            calcium = 700
            iron = 9
            potassium = 3500
            vitamin_a = 700
            thiamine = 1.2
            niacin = 14
            vitamin_c = 100
            vitamin_d = 15
            magnesium = 370
            vitamin_b9 = 400
            vitamin_b12 = 2.4
        elif 75 <= age:
            calcium = 700
            iron = 9
            potassium = 3500
            vitamin_a = 700
            thiamine = 1.2
            niacin = 13
            vitamin_c = 100
            vitamin_d = 15
            magnesium = 370
            vitamin_b9 = 400
            vitamin_b12 = 2.4
    if gender == "여자":
        if 1 <= age <= 2:
            calcium = 500
            iron = 6
            potassium = 2000
            vitamin_a = 250
            thiamine = 0.5
            niacin = 6
            vitamin_c = 40
            vitamin_d = 5
            magnesium = 70
            vitamin_b9 = 150
            vitamin_b12 = 0.9
        elif 3 <= age <= 5:
            calcium = 600
            iron = 7
            potassium = 2300
            vitamin_a = 300
            thiamine = 0.5
            niacin = 7
            vitamin_c = 45
            vitamin_d = 5
            magnesium = 110
            vitamin_b9 = 180
            vitamin_b12 = 1.1
        elif 6 <= age <= 8:
            calcium = 700
            iron = 9
            potassium = 2600
            vitamin_a = 400
            thiamine = 0.7
            niacin = 9
            vitamin_c = 50
            vitamin_d = 5
            magnesium = 150
            vitamin_b9 = 220
            vitamin_b12 = 1.3
        elif 9 <= age <= 11:
            calcium = 800
            iron = 10
            potassium = 3000
            vitamin_a = 550
            thiamine = 0.9
            niacin = 12
            vitamin_c = 70
            vitamin_d = 5
            magnesium = 220
            vitamin_b9 = 300
            vitamin_b12 = 1.7
        elif 12 <= age <= 14:
            calcium = 900
            iron = 16
            potassium = 3500
            vitamin_a = 650
            thiamine = 1.1
            niacin = 15
            vitamin_c = 90
            vitamin_d = 10
            magnesium = 290
            vitamin_b9 = 360
            vitamin_b12 = 2.3
        elif 15 <= age <= 18:
            calcium = 800
            iron = 14
            potassium = 3500
            vitamin_a = 650
            thiamine = 1.2
            niacin = 14
            vitamin_c = 100
            vitamin_d = 10
            magnesium = 340
            vitamin_b9 = 400
            vitamin_b12 = 2.4
        elif 19 <= age <= 29:
            calcium = 700
            iron = 14
            potassium = 3500
            vitamin_a = 650
            thiamine = 1.1
            niacin = 14
            vitamin_c = 100
            vitamin_d = 10
            magnesium = 280
            vitamin_b9 = 400
            vitamin_b12 = 2.4
        elif 30 <= age <= 49:
            calcium = 700
            iron = 14
            potassium = 3500
            vitamin_a = 650
            thiamine = 1.1
            niacin = 14
            vitamin_c = 100
            vitamin_d = 10
            magnesium = 280
            vitamin_b9 = 400
            vitamin_b12 = 2.4
        elif 50 <= age <= 64:
            calcium = 800
            iron = 8
            potassium = 3500
            vitamin_a = 600
            thiamine = 1.1
            niacin = 14
            vitamin_c = 100
            vitamin_d = 10
            magnesium = 280
            vitamin_b9 = 400
            vitamin_b12 = 2.4
        elif 65 <= age <= 74:
            calcium = 800
            iron = 8
            potassium = 3500
            vitamin_a = 600
            thiamine = 1.1
            niacin = 13
            vitamin_c = 100
            vitamin_d = 15
            magnesium = 280
            vitamin_b9 = 400
            vitamin_b12 = 2.4
        elif 75 <= age:
            calcium = 800
            iron = 8
            potassium = 3500
            vitamin_a = 600
            thiamine = 1.1
            niacin = 12
            vitamin_c = 100
            vitamin_d = 15
            magnesium = 280
            vitamin_b9 = 400
            vitamin_b12 = 2.4
        
        # 질병에 따른 조정
    if diseases["고혈압"]:
        if gender == "남자":
            if age >= 19:
                calcium = 1000
                potassium = 4700
                magnesium = 420
        if gender == "여자":
            if age >= 19:
                calcium = 1000
                potassium = 4700
                magnesium = 320       
    if diseases["당뇨병"]:
        if gender == "남자":
            if 19 <= age <= 50:
                calcium = 1000
                magnesium = 420
            if age >= 50:
                calcium = 1200
                magnesium = 420
                    
        if gender == "여자":
            if 19 <= age <= 50:
                calcium = 1000
                magnesium = 320
            if age >= 50:
                calcium = 1200
                magnesium = 420
    if diseases["위암"]:
        if gender == "남자":
            if 19 <= age <= 50:
                calcium = 1000
            if age >= 50:
                calcium = 1200
        if gender == "여자":
            if 19 <= age <= 50:
                calcium = 1000
            if age >= 50:
                calcium = 1200
    if diseases["대장암"]:
        if gender == "남자":
            if 19 <= age <= 50:
                calcium = 1000
            if age >= 50:
                calcium = 1200
        if gender == "여자":
            if 19 <= age <= 50:
                calcium = 1000
            if age >= 50:
                calcium = 1200           
                         
    return energy, carbohydrate, protein, fat, calcium, iron, potassium, vitamin_a, thiamine, niacin, vitamin_c, vitamin_d, magnesium, vitamin_b9, vitamin_b12

# 사용자 정보 받기
gender, age, height, weight, bmi, pa_index, diseases = get_user_info()

# 영양소별 권장 섭취량 산출
energy_avg, carbohydrate_avg, protein_avg, fat_avg, calcium_avg, iron_avg, potassium_avg, vitamin_a_avg, thiamine_avg, niacin_avg, vitamin_c_avg, vitamin_d_avg, magnesium_avg, vitamin_b9_avg, vitamin_b12_avg = calculate_average_requirements(gender, age, pa_index, weight, height,diseases)

# 결과 출력
print("\n<사용자 정보>")
print("1)성별: {}".format(gender))
print("2)나이: {}세".format(age))
print("3)키: {}cm".format(height))
print("4)몸무게: {}kg".format(weight))
print("5)BMI 지수: {:.2f}".format(bmi))
print("6)PA 지수: {}".format(pa_index))
print("7)질병 유무")
for disease, is_present in diseases.items():
    print(f"{disease}: {'유' if is_present else '무'}")

# 결과 출력
print("\n<권장 섭취량> (단, 에너지는 필요추정량 산출값)")
print("1)에너지(kcal): {:.2f}".format(energy_avg))
print("2)단백질(g): {:.2f}".format(protein_avg))
print("3)지방(g): {:.2f}".format(fat_avg))
print("4)탄수화물(g): {:.2f}".format(carbohydrate_avg))
print("5)칼슘(mg): {:.2f}".format(calcium_avg))
print("6)철(mg): {:.2f}".format(iron_avg))
print("7)칼륨(mg): {:.2f}".format(potassium_avg))
print("7)비타민 A(μg RAE): {:.2f}".format(vitamin_a_avg))
print("8)티아민(mg): {:.2f}".format(thiamine_avg))
print("9)니아신(mg): {:.2f}".format(niacin_avg))
print("10)비타민C(mg): {:.2f}".format(vitamin_c_avg))
print("11)비타민D(mg): {:.2f}".format(vitamin_d_avg))
print("12)마그네슘(mg): {:.2f}".format(magnesium_avg))
print("13)비타민 B9(μg): {:.2f}".format(vitamin_b9_avg))
print("14)비타민 B12(μg): {:.2f}".format(vitamin_b12_avg))

# 권장 섭취량 결과값들을 need라는 리스트에 넣어주기
need = [
    energy_avg,
    protein_avg,
    fat_avg,
    carbohydrate_avg,
    calcium_avg,
    iron_avg,
    potassium_avg,
    thiamine_avg,
    vitamin_a_avg,
    niacin_avg,
    vitamin_c_avg,
    vitamin_d_avg,
    magnesium_avg,
    vitamin_b9_avg,
    vitamin_b12_avg
]

# 엑셀 파일에서 식품 영양 정보를 불러오는 함수
def load_nutrition_data(file_path):
    df = pd.read_excel(file_path)
    return df

# 새로운 엑셀 파일에서 식품 영양 정보를 불러오는 함수
def load_additional_nutrition_data(file_path):
    df = pd.read_excel(file_path)
    return df

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
                        adjusted_value = nutrient_value * (quantity / 100)  # 실제 섭취량으로 조정
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
                            adjusted_value = nutrient_value * (quantity / 100)  # 실제 섭취량으로 조정
                            nutrition_values[nutrient] = nutrition_values.get(nutrient, 0) + adjusted_value
    return nutrition_values

# 엑셀 파일에서 식품 영양 정보를 불러오기
file_path = '/Users/whoru/new/식품영양성분DB_음식_20240416.xlsx'
nutrition_data = load_nutrition_data(file_path)

# 새로운 엑셀 파일에서 식품 영양 정보를 불러오기
additional_file_path = '/Users/whoru/new/식품영양성분DB_음식_20240416.xlsx'
additional_nutrition_data = load_additional_nutrition_data(additional_file_path)

# 두 데이터 프레임을 합침
combined_nutrition_data = pd.concat([nutrition_data, additional_nutrition_data], ignore_index=True)

def get_daily_menu():
    menu = input("식단을 입력하세요 (예: 김밥_참치, 짬뽕밥, 오므라이스): ").split(', ')
    quantities = []
    for food in menu:
        quantity = float(input(f"{food}의 섭취량을 입력하세요 (g): "))
        quantities.append(quantity)
    return menu, quantities

# 하루 식단과 섭취량 입력받기
total_nutrition_values = {}
for i in range(7):
    print(f"{i+1}일차 식단을 입력하세요.")
    menu, quantities = get_daily_menu()
    # 각 영양소의 값을 찾아서 누적
    nutrition_values = find_nutrition_values(menu, quantities, combined_nutrition_data)
    for nutrient, value in nutrition_values.items():
        total_nutrition_values[nutrient] = total_nutrition_values.get(nutrient, 0) + value

# 평균 값 계산
average_nutrition_values = {nutrient: value / 7 for nutrient, value in total_nutrition_values.items()}

# 결과 출력
print("\n<하루 실제 영양소 섭취량>")
for nutrient, value in average_nutrition_values.items():
    print(f"{nutrient}: {value:.2f}")

# 실제 영양소 섭취량 결과값들을 real 이라는 리스트에 넣어주기
real = list(average_nutrition_values.values())
print(real)

# gap 리스트 값
gap = [need_val - real_val for need_val, real_val in zip(need, real)]
print(gap)

for nutrient, diff in zip(['에너지(kcal)', '단백질(g)', '지방(g)', '탄수화물(g)', '칼슘(mg)', '철(mg)', '칼륨(mg)', '비타민 A(μg RAE)', '티아민(mg)', '니아신(mg)', '비타민 C(mg)', '비타민 D(μg)', '마그네슘(㎎)','비타민 B9(μg)', '비타민 B12(μg)'], gap):
    if diff > 0:
        print(f"{nutrient}을(를) {diff:.2f} 부족하게 섭취했습니다.")
    elif diff < 0:
        print(f"{nutrient}을(를) {abs(diff):.2f} 과도하게 섭취했습니다.")
    else:
        print(f"{nutrient}을(를) 적절하게 섭취했습니다.")

def recommend_supplements(diseases):
    # 질병에 따른 영양소 부족 정보 및 권장 영양제
    deficiency_info = {
        "고혈압": {"영양소": ["비타민D", "비타민 B6", "비타민 B12", "마그네슘", "비타민 C", "칼륨", "칼슘", "아연", "비타민 C"], "영양제": "칼륨 보충제"},
        "당뇨병": {"영양소": ["마그네슘", "코엔자임Q10", "비타민 B6", "비타민 B12", "비타민 D", "비타민 C", "식이섬유", "크롬"], "영양제": "마그네슘 보충제"},
        "위암": {"영양소": ["오메가-3 지방산", "셀레늄", "아연", "비타민 A", "비타민 C"], "영양제": "섬유소 보충제"},
        "대장암": {"영양소": ["단백질", "비타민D", "칼슘", "철", "마그네슘", "수분", "오메가-3 지방산"]},
        "고지혈증": {"영양소": ["오메가3 지방산", "코엔자임Q10", "비타민 D"], "영양제": "오메가3 보충제"},
        "골다공증": {"영양소": ["칼슘", "비타민 D", "비타민 K"], "영양제": "칼슘 및 비타민 D 보충제"}
    }
    
    recommendations = []
    for disease, has_disease in diseases.items():
        if has_disease:
            nutrient = deficiency_info[disease]["영양소"]
            supplement = deficiency_info[disease]["영양제"]
            recommendations.append(f"{disease}으로 인해 {nutrient}이 부족할 수 있으므로 {supplement}를 섭취하는 것이 좋습니다.")
    
    return recommendations
# 권장 영양제 목록 얻기
recommendations = recommend_supplements(diseases)

# 권장 영양제 목록 출력
for recommendation in recommendations:
    print(recommendation)
