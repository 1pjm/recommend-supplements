import pandas as pd

def find_nutrition_values(menu, quantities, combined_nutrition_data):
    nutrition_values = {}
    for food, quantity in zip(menu, quantities):
        food_info = combined_nutrition_data[combined_nutrition_data['식품명'] == food.strip()]
        if not food_info.empty:
            for nutrient in ['에너지(kcal)', '단백질(g)', '지방(g)', '탄수화물(g)', '칼슘(mg)', '철(mg)', '인(mg)', '티아민(mg)', '리보플라빈(mg)', '니아신(mg)', '비타민 C(mg)']:
                nutrient_value = food_info[nutrient].iloc[0] if nutrient in food_info.columns and not pd.isna(food_info[nutrient].iloc[0]) else 0
                nutrition_values[nutrient] = nutrition_values.get(nutrient, 0) + nutrient_value
    return nutrition_values
