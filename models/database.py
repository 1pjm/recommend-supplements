import pandas as pd
from sqlalchemy import create_engine

def load_nutrition_data(file_path1, file_path2):
    df1 = pd.read_excel(file_path1)
    df2 = pd.read_excel(file_path2)
    df = pd.concat([df1, df2], ignore_index=True)
    df = df.drop_duplicates(subset=['식품명'])
    return df.fillna(0)  # NaN 값을 0으로 대체

def find_nutrition_values(menu, nutrition_data):
    nutrition_values = {}
    for food in menu:
        food_info = nutrition_data[nutrition_data['식품명'] == food.strip()]
        if not food_info.empty:
            for nutrient in ['에너지(kcal)', '단백질(g)', '지방(g)', '탄수화물(g)', '칼슘(mg)', '철(mg)', '인(mg)', '티아민(mg)', '리보플라빈(mg)', '니아신(mg)', '비타민 C(mg)']:
                nutrient_value = food_info[nutrient].iloc[0] if nutrient in food_info.columns and not pd.isna(food_info[nutrient].iloc[0]) else 0
                nutrition_values[nutrient] = nutrition_values.get(nutrient, 0) + nutrient_value
        else:
            print(f"Warning: No data found for {food}.")
            for nutrient in ['에너지(kcal)', '단백질(g)', '지방(g)', '탄수화물(g)', '칼슘(mg)', '철(mg)', '인(mg)', '티아민(mg)', '리보플라빈(mg)', '니아신(mg)', '비타민 C(mg)']:
                nutrition_values[nutrient] = nutrition_values.get(nutrient, 0)
    return nutrition_values
