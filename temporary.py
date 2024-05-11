import pandas as pd

# CSV 파일을 로드하는 함수
def load_nutrient_data(csv_file):
    # 'cp949' 인코딩을 사용하여 한국어가 포함된 파일을 올바르게 읽어옵니다.
    return pd.read_csv(csv_file, encoding='cp949')

# CSV 파일의 위치를 지정
csv_file = r'C:\Users\samsung\Desktop\s\캡디\capstone-design-2024\식품영양성분DB_음식_20240416.CSV'
# 식품 영양 정보 데이터 로드
nutrient_data = load_nutrient_data(csv_file)

# 사용자로부터 받은 식단 정보를 처리하여 일일 실제 영양소 섭취량을 계산하는 함수
def process_diet_log(diet_log, nutrient_data):
    daily_intake = {}  # 각 영양소별 섭취량을 저장할 딕셔너리

    # 사용자의 식단 로그를 반복 처리
    for food_item, amount in diet_log.items():
        # 데이터베이스에서 해당 식품명을 찾아 해당 식품의 영양 정보를 추출
        nutrient_info = nutrient_data[nutrient_data['식품명'] == food_item]
        if not nutrient_info.empty:
            # 필요한 영양소의 정보를 추출하여 계산
            for nutrient in ['에너지(kcal)', '단백질(g)', '칼슘(mg)', '인(mg)', '철(mg)', '티아민(mg)', '리보플라빈(mg)', '니아신(mg)', '비타민 C(mg)', '탄수화물(g)', '지방(g)']:
                if nutrient not in daily_intake:
                    daily_intake[nutrient] = 0
                # NaN 값 처리와 실제 섭취량 계산
                nutrient_value = nutrient_info[nutrient].values[0] if nutrient_info[nutrient].values.size > 0 and not pd.isna(nutrient_info[nutrient].values[0]) else 0
                daily_intake[nutrient] += nutrient_value * amount

    return daily_intake

# 사용자 식단 정보 예시
diet_log = {
    '국밥_돼지머리': 1,
    '김밥': 2,
    '도넛_찹쌀': 5,
    '햄버거_불고기버거': 1,
    '기타차_샤인머스캣 티플레저': 1,
    '커피_아메리카노': 2,
    '갓김치': 3,
    '깍두기': 5
}

# 실제 영양소 섭취량 처리
actual_intakes = process_diet_log(diet_log, nutrient_data)

# 일일 권장 섭취량을 계산하는 함수
def calculate_daily_intakes(age, gender, weight, height, pa_index, condition_additions={}):
    # 성별에 따른 에너지 및 단백질 필요량 계산
    if gender.lower() == 'male':
        energy = 662 - 9.53 * age + pa_index * (15.91 * weight + 539.6 * height)
        protein = (energy * 14 / 100) / 4
    else:
        energy = 354 - 6.91 * age + pa_index * (9.36 * weight + 726 * height)
        protein = (energy * 14 / 100) / 4

    # 임신 등의 특수 상황을 고려한 추가 에너지 계산
    if 'pregnancy' in condition_additions:
        energy += condition_additions['pregnancy']

    # 기타 영양소 계산
    calcium = 9.39 * weight
    phosphorus = 580
    iron = (0.014 * weight / 0.12) if gender.lower() == 'male' else ((0.014 * weight + 0.5) / 0.12)
    thiamin = 1.0 if age < 65 else 1.0 * (weight / 68.9)
    riboflavin = 1.3 if age < 65 else 1.3 * (weight / 68.9)
    niacin = 12 if age < 65 else 11
    vitamin_c = 75

    # 탄수화물 및 지방 계산
    carbohydrate = (energy * 60 / 100) / 4
    fat = (energy * 23 / 100) / 9

    return {
        '에너지': energy,
        '단백질': protein,
        '칼슘': calcium,
        '인': phosphorus,
        '철분': iron,
        '티아민': thiamin,
        '리보플라빈': riboflavin,
        '니아신': niacin,
        '비타민C': vitamin_c,
        '탄수화물': carbohydrate,
        '지방': fat
    }

# 사용자 데이터 예시
age = 50
gender = 'Female'
weight = 65
height = 1.60
pa_index = 1.27

# 일일 권장 섭취량 계산
recommended_intakes = calculate_daily_intakes(
    age, gender, weight, height, pa_index)

# 권장 섭취량과 실제 섭취량을 비교하여 영양소 부족, 과잉, 적정 상태를 계산하는 함수
def compare_nutrients(recommended, actual):
    result = {}
    for nutrient, rec_amount in recommended.items():
        actual_amount = actual.get(nutrient, 0)
        difference = actual_amount - rec_amount
        status = '부족' if difference < 0 else '과잉' if difference > 0 else '적정'
        result[nutrient] = (status, difference)
    return result

# 비교 실행
comparison_results = compare_nutrients(recommended_intakes, actual_intakes)

# 결과 출력
for nutrient, (status, diff) in comparison_results.items():
    print(f"{nutrient}: {status} ({diff:.2f})")


# 웹페이지 상에서 음식을 선택할 수 있도록
# 식품 영양 성분 db를 웹페이지 상에서 불러오는 방법
# 가공식품 db도 불러오는 방법
# 권장 섭취량 계산 식 확인(현재 부족으로만 나옴)