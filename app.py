from flask import Flask, request, render_template, jsonify, redirect, url_for, session, send_file
import pandas as pd
import os
import csv
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# 엑셀 파일에서 식품 영양 정보를 불러오는 함수
def load_nutrition_data(file_path):
    if not os.path.exists(file_path):
        print(f"파일이 존재하지 않습니다: {file_path}")
        return None
    return pd.read_excel(file_path)

# 엑셀 파일에서 식품 영양 정보를 불러오기
file_path = 'data/식품영양성분DB_음식_20240416.xlsx'
nutrition_data = load_nutrition_data(file_path)
additional_file_path = 'data/식품영양성분DB_가공식품_20240416.xlsx'
additional_nutrition_data = load_nutrition_data(additional_file_path)
combined_nutrition_data = pd.concat([nutrition_data, additional_nutrition_data], ignore_index=True)

# BMI 지수 계산 함수
def calculate_bmi(weight, height):
    return weight / ((height / 100) ** 2)

# PA 지수 계산 함수
def calculate_pa_index(gender, pa_level):
    if gender == "여자":
        return [1.0, 1.12, 1.27, 1.45][int(pa_level)-1]
    elif gender == "남자":
        return [1.0, 1.11, 1.25, 1.48][int(pa_level)-1]
    return None

# 권장 섭취량 계산 함수
def calculate_average_requirements(gender, age, pa_index, weight, height, diseases):
    print(f"Calculating requirements for: Gender={gender}, Age={age}, PA Index={pa_index}, Weight={weight}, Height={height}, Diseases={diseases}")
    
    if gender not in ["남자", "여자"]:
        print("Invalid gender")
        return None

    if gender == "남자":
        energy = 662 - 9.53 * age + pa_index * (15.91 * weight + 539.6 * (height / 100))
    elif gender == "여자":
        energy = 354 - 6.91 * age + pa_index * (9.36 * weight + 726 * (height / 100))
    else:
        print("Gender not recognized")
        return None

    carbohydrate = (energy * 0.6) / 4
    protein = (energy * 0.135) / 4
    fat = (energy * 0.225) / 9

    print("Energy:", energy)
    print("Carbohydrate:", carbohydrate)
    print("Protein:", protein)
    print("Fat:", fat)

    try:
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
                print("Age out of range for recommendations")
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
                print("Age out of range for recommendations")
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
    except Exception as e:
        print(f"Error in calculate_average_requirements: {e}")
        return None

def calculate_actual_intake(meals, combined_nutrition_data):
    nutrition_totals = {
        '에너지(kcal)': 0, '단백질(g)': 0, '지방(g)': 0, '탄수화물(g)': 0,
        '칼슘(mg)': 0, '철(mg)': 0, '칼륨(mg)': 0, '비타민 A(μg RAE)': 0,
        '티아민(mg)': 0, '니아신(mg)': 0, '비타민 C(mg)': 0, '비타민 D(μg)': 0,
        '마그네슘(㎎)': 0, '비타민 B9(μg)': 0, '비타민 B12(μg)': 0
    }

    for meal in meals:
        try:
            food, quantity = meal.split('_')
            quantity = float(quantity)
            food_info = combined_nutrition_data[combined_nutrition_data['식품명'] == food]
            if not food_info.empty:
                for nutrient in nutrition_totals.keys():
                    if nutrient in food_info.columns:
                        nutrient_value = food_info[nutrient].iloc[0]
                        if isinstance(nutrient_value, str):
                            nutrient_value = pd.to_numeric(nutrient_value, errors='coerce')
                        if pd.notnull(nutrient_value):
                            adjusted_value = nutrient_value * (quantity / 100)
                            nutrition_totals[nutrient] += adjusted_value
        except ValueError:
            print(f"식단 항목 형식이 잘못되었습니다: {meal}")

    return list(nutrition_totals.values())

def calculate_gap(nutrients, recommended_intake, actual_intake):
    return [recommended - actual for recommended, actual in zip(recommended_intake, actual_intake)]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['gender'] = request.form.get('gender')
        session['age'] = int(request.form.get('age'))
        session['height'] = float(request.form.get('height'))
        session['weight'] = float(request.form.get('weight'))
        session['pa_level'] = request.form.get('pa_level')
        session['diseases'] = {
            "고혈압": request.form.get('disease_hypertension') == '유',
            "당뇨병": request.form.get('disease_diabetes') == '유',
            "위암": request.form.get('disease_stomach_cancer') == '유',
            "대장암": request.form.get('disease_colon_cancer') == '유',
            "고지혈증": request.form.get('disease_hyperlipidemia') == '유',
            "골다공증": request.form.get('disease_osteoporosis') == '유'
        }
        return redirect(url_for('confirm'))
    return render_template('index.html')

@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    if request.method == 'POST':
        if 'confirm' in request.form:
            return redirect(url_for('day'))
        elif 'edit' in request.form:
            key = request.form['edit']
            value = request.form['value']
            if key in ['age', 'height', 'weight']:
                session[key] = float(value) if '.' in value else int(value)
            elif key == 'pa_level':
                session[key] = value
            elif key == 'diseases':
                session['diseases'] = {
                    "고혈압": '고혈압' in value,
                    "당뇨병": '당뇨병' in value,
                    "위암": '위암' in value,
                    "대장암": '대장암' in value,
                    "고지혈증": '고지혈증' in value,
                    "골다공증": '골다공증' in value
                }
            else:
                session[key] = value
            return redirect(url_for('confirm'))
    return render_template('confirm.html', data=session)

@app.route('/day', methods=['GET', 'POST'])
def day():
    if request.method == 'POST':
        meals = request.form.getlist('meals[]')
        session['meals'] = meals
        return redirect(url_for('result'))
    return render_template('day.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if query:
        results = combined_nutrition_data[combined_nutrition_data['식품명'].str.contains(query)]
        suggestions = results['식품명'].tolist()
    else:
        suggestions = []
    return jsonify(suggestions)

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
        review = product.select_one('div.other-info > div > span.rating-total-count')
        review = re.sub("[()]", "", review.text.strip()) if review else '0'
        link = "https://www.coupang.com" + product.select_one('a.search-product-link')['href'].strip()
        image = product.select_one('dt > img').get('data-img-src') or product.select_one('dt > img').get('src').replace("//", "")
        
        results.append([keyword, name, price, review, image, link])

    return results

@app.route('/result')
def result():
    gender = session.get('gender')
    age = session.get('age')
    height = session.get('height')
    weight = session.get('weight')
    pa_level = session.get('pa_level')
    diseases = session.get('diseases')
    meals = session.get('meals')

    print("Gender:", gender)
    print("Age:", age)
    print("Height:", height)
    print("Weight:", weight)
    print("PA Level:", pa_level)
    print("Diseases:", diseases)
    print("Meals:", meals)

    bmi = calculate_bmi(weight, height)
    pa_index = calculate_pa_index(gender, pa_level)
    print("BMI:", bmi)
    print("PA Index:", pa_index)

    recommended_intake = calculate_average_requirements(gender, age, pa_index, weight, height, diseases)
    print("Recommended Intake:", recommended_intake)

    if recommended_intake is None:
        return "추천 섭취량을 계산할 수 없습니다. 입력 값을 확인해주세요.", 400

    actual_intake = calculate_actual_intake(meals, combined_nutrition_data)
    print("Actual Intake:", actual_intake)

    nutrients = ['에너지(kcal)', '단백질(g)', '지방(g)', '탄수화물(g)', '칼슘(mg)', '철(mg)', '칼륨(mg)', '비타민 A(μg RAE)', '티아민(mg)', '니아신(mg)', '비타민 C(mg)', '비타민 D(μg)', '마그네슘(㎎)', '비타민 B9(μg)', '비타민 B12(μg)']
    gap = calculate_gap(nutrients, recommended_intake, actual_intake)
    print("Gap:", gap)

    keywords = {
        '단백질(g)': '단백질 영양제',
        '칼슘(mg)': '칼슘 영양제',
        '철(mg)': '철분 영양제',
        '칼륨(mg)': '칼륨 영양제',
        '비타민 A(μg RAE)': '비타민 A 영양제',
        '티아민(mg)': '비타민 B1 영양제',
        '니아신(mg)': '비타민 B3 영양제',
        '비타민 C(mg)': '비타민 C 영양제',
        '비타민 D(μg)': '비타민 D 영양제',
        '마그네슘(㎎)': '마그네슘 영양제',
        '비타민 B9(μg)': '엽산 보충제',
        '비타민 B12(μg)': '비타민 B12 보충제'
    }

    supplements = {}
    for nutrient, keyword in keywords.items():
        supplements[nutrient] = coupang_search(keyword)

    nutrition_status = []
    for nutrient, diff in zip(nutrients, gap):
        if diff > 0:
            status = f"{nutrient}을(를) {diff:.2f} 부족하게 섭취했습니다. 고로 {nutrient}와 관련된 영양제 TOP10을 추천해드리겠습니다."
        elif diff < 0:
            status = f"{nutrient}을(를) {abs(diff):.2f} 과도하게 섭취했습니다."
        else:
            status = f"{nutrient}을(를) 적절하게 섭취했습니다."
        nutrition_status.append(status)

    return render_template('result.html', nutrition_status=nutrition_status, supplements=supplements)


@app.route('/download')
def download():
    path = 'search_results.csv'
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
