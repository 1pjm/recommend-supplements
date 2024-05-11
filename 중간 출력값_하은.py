# BMI 지수 계산하는 함수
import pandas as pd


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
    pa_level = int(
        input("PA 지수를 입력하세요 (1: 비활동적, 2: 저활동적, 3: 활동적, 4: 매우 활동적): "))

    # 질병 유무 입력 받기
    diseases = {
        "고혈압": False,
        "당뇨병": False,
        "위암과 대장암": False,
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


# 사용자 정보 받기
gender, age, height, weight, bmi, pa_index, diseases = get_user_info()

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

 # 권장 섭취량 계산하는 함수 (논문표 참고. 평균필요량 수식 -> 섭취기준량 수식)


def calculate_average_requirements(gender, age, pa_index, weight, height):
    if gender == "남자":
        energy = 662 - 9.53 * age + pa_index * \
            (15.91 * weight + 539.6 * (height / 100))
    elif gender == "여자":
        energy = 354 - 6.91 * age + pa_index * \
            (9.36 * weight + 726 * (height / 100))
    else:
        return None

    carbohydrate = (energy * 0.6) / 4
    protein = (energy * 0.135) / 4
    fat = (energy * 0.225) / 9
    calcium = 9.39 * weight * 1.2
    phosphorus = 580 * 1.2
    if gender == "남자":
        iron = ((0.014 * weight) / 0.12) * 1.3
    elif gender == "여자":
        iron = ((0.014 * weight + 0.5) / 0.12) * 1.3
    else:
        iron = None

    if age >= 19 and age <= 64:
        if gender == "남자":
            thiamine = 1.0 * 1.2
            riboflavin = 1.3 * 1.2
            niacin = 12 * 1.3
        elif gender == "여자":
            thiamine = 0.9 * 1.2
            riboflavin = 1.0 * 1.2
            niacin = 11 * 1.3
    elif age >= 65:
        if gender == "남자":
            thiamine = 1.0 * (weight / 68.9) * 1.2
            riboflavin = 1.3 * (weight / 68.9) * 1.2
            if age >= 75:
                niacin = 11 * 1.3
            else:
                niacin = 12 * 1.3
        elif gender == "여자":
            thiamine = 0.9 * (weight / 55.9) * 1.2
            riboflavin = 1.0 * (weight / 55.9) * 1.2
            if age >= 75:
                niacin = 9 * 1.3
            else:
                niacin = 11 * 1.3
    else:
        thiamine, riboflavin, niacin = None, None, None

    vitamin_c = 75 * 1.3

    return energy, carbohydrate, protein, fat, calcium, phosphorus, iron, thiamine, riboflavin, niacin, vitamin_c


# 영양소별 권장 섭취량 산출
energy_avg, carbohydrate_avg, protein_avg, fat_avg, calcium_avg, phosphorus_avg, iron_avg, thiamine_avg, riboflavin_avg, niacin_avg, vitamin_c_avg = calculate_average_requirements(
    gender, age, pa_index, weight, height)

# 결과 출력
print("\n<권장 섭취량> (단위: g, 단, 에너지는 필요추정량 산출값)")
print("1)에너지(kcal): {:.2f}".format(energy_avg))
print("2)탄수화물(g): {:.2f}".format(carbohydrate_avg))
print("3)단백질(g): {:.2f}".format(protein_avg))
print("4)지방(g): {:.2f}".format(fat_avg))
print("5)칼슘(mg): {:.2f}".format(calcium_avg))
print("6)인(mg): {:.2f}".format(phosphorus_avg))
print("7)철(mg): {:.2f}".format(iron_avg))
print("8)티아민(mg): {:.2f}".format(thiamine_avg)
      if thiamine_avg is not None else "8)티아민: 성별 또는 연령에 따른 값 없음")
print("9)리보플라빈(mg): {:.2f}".format(riboflavin_avg)
      if riboflavin_avg is not None else "9)리보플라빈: 성별 또는 연령에 따른 값 없음")
print("10)니아신(mg NE): {:.2f}".format(niacin_avg)
      if niacin_avg is not None else "10)니아신: 성별 또는 연령에 따른 값 없음")
print("11)비타민C(mg): {:.2f}".format(vitamin_c_avg)
      if vitamin_c_avg is not None else "11)비타민C: 성별 또는 연령에 따른 값 없음")

# 권장 섭취량 결과값들을 need라는 리스트에 넣어주기
need = [
    energy_avg,
    carbohydrate_avg,
    protein_avg,
    fat_avg,
    calcium_avg,
    phosphorus_avg,
    iron_avg,
    thiamine_avg,
    riboflavin_avg,
    niacin_avg,
    vitamin_c_avg
]

# 권장 섭취량의 단위를 mg에서 g로 변환하여 출력
need_g = [value * 0.001 if value is not None else None for value in need]
print(need_g)


# 엑셀 파일에서 식품 영양 정보를 불러오는 함수

def load_nutrition_data(file_path):
    df = pd.read_excel(file_path)
    return df

# 식단의 각 영양소 값을 찾아내는 함수


def find_nutrition_values(menu, nutrition_data):
    nutrition_values = {}
    for food in menu:
        food_info = nutrition_data[nutrition_data['식품명'] == food]
        if not food_info.empty:
            for nutrient in ['에너지(kcal)', '단백질(g)', '지방(g)', '탄수화물(g)', '칼슘(mg)', '철(mg)', '인(mg)', '티아민(mg)', '리보플라빈(mg)', '니아신(mg)', '비타민 C(mg)']:
                nutrition_values[nutrient] = nutrition_values.get(
                    nutrient, 0) + food_info[nutrient].iloc[0]
    return nutrition_values


# 엑셀 파일에서 식품 영양 정보를 불러오기
file_path = "C:/Users/김하은/OneDrive/바탕 화면/식품영양성분DB_음식_20240416.xlsx"
nutrition_data = load_nutrition_data(file_path)

# 7일치 식단 입력 받기
total_nutrition_values = {}
for i in range(7):
    menu = input(f"{i+1}일차 식단을 입력하세요 (예: 김밥_참치, 짬뽕밥, 오므라이스): ").split(', ')
    # 각 영양소의 값을 찾아서 누적합니다.
    nutrition_values = find_nutrition_values(menu, nutrition_data)
    for nutrient, value in nutrition_values.items():
        total_nutrition_values[nutrient] = total_nutrition_values.get(
            nutrient, 0) + value

# 평균 값 계산
average_nutrition_values = {
    nutrient: value / 7 for nutrient, value in total_nutrition_values.items()}

# 결과 출력
print("\n<하루 실제 영양소 섭취량>")
for nutrient, value in average_nutrition_values.items():
    print(f"{nutrient}: {value:.2f}g")

# 실제 영양소 섭취량 결과값들을 real 이라는 리스트에 넣어주기
real = list(average_nutrition_values.values())
print(real)

# need 리스트 값
need = [
    energy_avg,
    carbohydrate_avg,
    protein_avg,
    fat_avg,
    calcium_avg,
    phosphorus_avg,
    iron_avg,
    thiamine_avg,
    riboflavin_avg,
    niacin_avg,
    vitamin_c_avg
]

# real 리스트 값
real = list(average_nutrition_values.values())

# gap 리스트 값
gap = [need_val - real_val for need_val, real_val in zip(need, real)]
print(gap)

for nutrient, diff in zip(['에너지(kcal)', '탄수화물(g)', '단백질(g)', '지방(g)', '칼슘(mg)', '인(mg)', '철(mg)', '티아민(mg)', '리보플라빈(mg)', '니아신(mg)', '비타민 C(mg)'], gap):
    if diff > 0:
        print(f"{nutrient}을(를) {diff:.2f}g 부족하게 섭취했습니다.")
    elif diff < 0:
        print(f"{nutrient}을(를) {abs(diff):.2f}g 과도하게 섭취했습니다.")
    else:
        print(f"{nutrient}을(를) 적절하게 섭취했습니다.")
