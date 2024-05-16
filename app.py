from flask import Flask, request, render_template
from utils.calculations import calculate_bmi, calculate_pa_index, calculate_average_requirements
from models.database import initialize_db
from sqlalchemy import create_engine
import pandas as pd

app = Flask(__name__)
engine = create_engine('sqlite:///nutrition.db')

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
        nutrition_values = find_nutrition_values(menu)
        for nutrient, value in nutrition_values.items():
            total_nutrition_values[nutrient] = total_nutrition_values.get(nutrient, 0) + value

    # 평균 값 계산
    average_nutrition_values = {nutrient: value / 7 for nutrient, value in total_nutrition_values.items()}

    # 차이 값 계산
    gap = [req - avg for req, avg in zip(requirements, average_nutrition_values.values())]

    return render_template('result.html', bmi=bmi, pa_index=pa_index, requirements=requirements,
                           average_nutrition_values=average_nutrition_values, gap=gap)

def find_nutrition_values(menu):
    nutrition_values = {}
    df = pd.read_sql('nutrition', engine)
    for food in menu:
        food_info = df[df['식품명'] == food.strip()]
        if not food_info.empty:
            for nutrient in ['에너지(kcal)', '단백질(g)', '지방(g)', '탄수화물(g)', '칼슘(mg)', '철(mg)', '인(mg)', '티아민(mg)', '리보플라빈(mg)', '니아신(mg)', '비타민 C(mg)']:
                nutrient_value = food_info[nutrient].iloc[0] if nutrient in food_info.columns and not pd.isna(food_info[nutrient].iloc[0]) else 0
                nutrition_values[nutrient] = nutrition_values.get(nutrient, 0) + nutrient_value
    return nutrition_values

if __name__ == '__main__':
    initialize_db()
    app.run(debug=True, host='0.0.0.0')
