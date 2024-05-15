from flask import Flask, request, render_template
from utils.calculations import calculate_bmi, calculate_pa_index, calculate_average_requirements
from models.database import load_nutrition_data, find_nutrition_values
import os

app = Flask(__name__)

# 엑셀 파일 경로 지정
file_path1 = os.path.join(os.path.dirname(__file__), 'data', '식품영양성분DB_음식_20240416.xlsx')
file_path2 = os.path.join(os.path.dirname(__file__), 'data', '식품영양성분DB_가공식품_20240416.xlsx')

# 식품 영양 정보 불러오기
nutrition_data = load_nutrition_data(file_path1, file_path2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    gender = request.form['gender']
    age = int(request.form['age'])
    height = float(request.form['height'])
    weight = float(request.form['weight'])
    pa_level = int(request.form['pa_level'])
    diseases = request.form.getlist('diseases')

    # BMI 계산
    bmi = calculate_bmi(weight, height)

    # PA 지수 계산
    pa_index = calculate_pa_index(gender, pa_level)

    # 권장 섭취량 계산
    requirements = calculate_average_requirements(gender, age, pa_index, weight, height)

    # 7일치 식단 입력 받기
    total_nutrition_values = {}
    for i in range(7):
        menu = request.form.get(f'day{i+1}_menu').split(', ')
        # 각 영양소의 값을 찾아서 누적합니다.
        nutrition_values = find_nutrition_values(menu, nutrition_data)
        for nutrient, value in nutrition_values.items():
            total_nutrition_values[nutrient] = total_nutrition_values.get(nutrient, 0) + value

    # 평균 값 계산
    average_nutrition_values = {nutrient: value / 7 for nutrient, value in total_nutrition_values.items()}

    return render_template('result.html', bmi=bmi, pa_index=pa_index, requirements=requirements, average_nutrition_values=average_nutrition_values)

if __name__ == '__main__':
    app.run(debug=True)
