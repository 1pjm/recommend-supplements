import pandas as pd
from sqlalchemy import create_engine

def load_nutrition_data(file_path1, file_path2):
    df1 = pd.read_excel(file_path1)
    df2 = pd.read_excel(file_path2)
    combined_df = pd.concat([df1, df2], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset=['식품명']).fillna(0)
    return combined_df

def save_to_db(dataframe, db_name='nutrition.db'):
    engine = create_engine(f'sqlite:///{db_name}')
    dataframe.to_sql('nutrition', engine, if_exists='replace', index=False)

def initialize_db():
    file_path1 = 'data/식품영양성분DB_음식_20240416.xlsx'
    file_path2 = 'data/식품영양성분DB_가공식품_20240416.xlsx'
    combined_df = load_nutrition_data(file_path1, file_path2)
    save_to_db(combined_df)

if __name__ == "__main__":
    initialize_db()
