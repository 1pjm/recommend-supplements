def calculate_bmi(weight, height):
    return weight / ((height / 100) ** 2)

def calculate_pa_index(gender, pa_level):
    if gender == "여자":
        return [1.0, 1.12, 1.27, 1.45][pa_level - 1]
    elif gender == "남자":
        return [1.0, 1.11, 1.25, 1.48][pa_level - 1]
    else:
        return None

def calculate_average_requirements(gender, age, pa_index, weight, height):
    if gender == "남자":
        energy = 662 - 9.53 * age + pa_index * (15.91 * weight + 539.6 * (height / 100))
    elif gender == "여자":
        energy = 354 - 6.91 * age + pa_index * (9.36 * weight + 726 * (height / 100))
    else:
        return None
    
    carbohydrate = (energy * 0.6) / 4
    protein = (energy * 0.135) / 4
    fat = (energy * 0.225) / 9
    calcium = 9.39 * weight * 1.2
    phosphorus = 580 * 1.2
    iron = ((0.014 * weight + (0.5 if gender == "여자" else 0)) / 0.12) * 1.3
    
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
            niacin = 11 * 1.3 if age >= 75 else 12 * 1.3
        elif gender == "여자":
            thiamine = 0.9 * (weight / 55.9) * 1.2
            riboflavin = 1.0 * (weight / 55.9) * 1.2
            niacin = 9 * 1.3 if age >= 75 else 11 * 1.3
    else:
        thiamine, riboflavin, niacin = None, None, None
    
    vitamin_c = 75 * 1.3
    
    return energy, carbohydrate, protein, fat, calcium, phosphorus, iron, thiamine, riboflavin, niacin, vitamin_c
