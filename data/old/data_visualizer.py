import sqlite3

import matplotlib.pyplot as plt
import numpy as np

connection = sqlite3.connect("data/colleges.sqlite")

cursor = connection.cursor()



searches = {
    # hd2021_summary
    "college name": ("College_Name", "hd2021_summary"), # string
    "college alias": ("College_Alias_Also_Known_As", "hd2021_summary"), # string
    "college address": ("Address", "hd2021_summary"), # string
    "closest city": ("City", "hd2021_summary"), # string
    "state": ("State", "hd2021_summary"), # string
    "zip code": ("Zip_Code", "hd2021_summary"), # string
    "current president": ("Name_of_Chief_Administrator_of_Institution", "hd2021_summary"), # string
    "current president title": ("Title_of_Chief_Administrator_of_Institution", "hd2021_summary"), # string
    "web address": ("Website_Address", "hd2021_summary"), # string
    "admissions office url": ("Admissions_Office_URL", "hd2021_summary"), # string
    "financial aid office url": ("Financial_Aid_Office_URL", "hd2021_summary"), # string
    "application url": ("Online_Application_URL", "hd2021_summary"), # string
    "price calculator url": ("Net_Price_Calculator_URL", "hd2021_summary"), # string
    "institution level": ("Level_of_institution", "hd2021_summary"), # in years # enum
    "college type": ("Private_or_Public_Control_of_institution", "hd2021_summary"), # enum
    "highest degree level": ("Highest_Level_Offered", "hd2021_summary"), # enum
    "offers undergraduate degree": ("Offers_Undergraduate_Degrees", "hd2021_summary"), # bool
    "offers graduate degree": ("Offers_Graduate_Degrees", "hd2021_summary"), # bool
    "is degree granting": ("Degree_Granting_Status", "hd2021_summary"), # enum
    "is historically black": ("Is_Historically_Black_College_or_University", "hd2021_summary"), # bool
    "has hospital": ("Has_Hospital", "hd2021_summary"), # bool
    "offers medical degree": ("Offere_Medicine_Degrees", "hd2021_summary"), # misspelled on the table
    "is tribal college": ("Is_Tribal_College", "hd2021_summary"), # bool
    "size of city/town": ("Degree_of_urbanization", "hd2021_summary"), # enum
    "is out of business": ("Date_Institution_Closed", "hd2021_summary"), # bool
    "carnegie classification": ("Carnegie_Basic_Classification", "hd2021_summary"), # enum <-- not sure tho
    "enrollment profile": ("Carnegie Classification 2021: (Enrollment Profile", "hd2021_summary"), # enum
    "size and setting": ("Carnegie Classification 2021: (Size and Setting", "hd2021_summary"), # enum
    "institution size": ("Institution Size", "hd2021_summary"), # is in categories # enum
    "multi campus": ("Multi-institution or multi-campus organization", "hd2021_summary"), # string
    "multi campus system name": ("Name of multi-institution or multi-campus organization", "hd2021_summary"), # string
    "longitude": ("Longitude", "hd2021_summary"), # double
    "latitude": ("Latitude", "hd2021_summary"), # double
    
    # ic2021_summary
    "can study abroad": ("Study_abroad", "ic2021_summary"), # bool IMPORTANT
    "is occupational": ("Occupational", "ic2021_summary"), # bool
    "is academic": ("Academic", "ic2021_summary"), # bool
    "is religious": ("Religious_affiliation", "ic2021_summary"), # bool <--- make starts int if > 0
    "dual enrollment": ("Dual_enrollment", "ic2021_summary"), # bool
    "credit for life experiences": ("Credit_for_life_experiences", "ic2021_summary"), # bool
    "takes ap credits": ("Advanced_placement_AP_credits", "ic2021_summary"), # bool
    
    # ic2021_ay_summary
    "in district average tuition (undergraduate)": ("in_district_average_tuition_for_full_time_undergraduates", "ic2021_ay_summary"), # int
    "in district required fees (undergraduates)": ("in_district_required_fees_for_full_time_undergraduates", "ic2021_ay_summary"), # int
    
    # ic2021_py_summary
    "largest program": ("largest_program", "ic2021_py_summary"),  # string
    "second largest program": ("second_largest_program", "ic2021_py_summary"), # string
    "third largest program": ("third_largest_program", "ic2021_py_summary"), # string
    "fourth largest program": ("fourth_largest_program", "ic2021_py_summary"), # string
    "fifth largest program": ("fifth_largest_program", "ic2021_py_summary"), # string
    "sixth largest program": ("sixth_largest_program", "ic2021_py_summary"), # string
    "number of programs": ("Number_of_program_offered", "ic2021_py_summary"), # int
    "cost of books and supplies for first largest program": ("Cost_of_books_and_supplies_of_1st_largest_program", "ic2021_py_summary"), # int
    "cost of books and supplies for second largest program": ("Cost_of_books_and_supplies_of_2nd_largest_program", "ic2021_py_summary"), # int
    "cost of books and supplies for third largest program": ("Cost_of_books_and_supplies_of_3rd_largest_program", "ic2021_py_summary"), # int
    "cost of books and supplies for fourth largest program": ("Cost_of_books_and_supplies_of_4th_largest_program", "ic2021_py_summary"), # int
    "cost of books and supplies for fifth largest program": ("Cost_of_books_and_supplies_of_5th_largest_program", "ic2021_py_summary"), # int
    "cost of books and supplies for sixth largest program": ("Cost_of_books_and_supplies_of_6th_largest_program", "ic2021_py_summary"), # int
    
    # crime_oncampus_2021
    "rapes in 2021": ("RAPE21", "crime_oncampus_2021"), # int
    "rapes in 2020": ("RAPE20", "crime_oncampus_2021"), # int
    "rapes in 2019": ("RAPE19", "crime_oncampus_2021"), # int

    "fondlings 2021": ("FONDL21", "crime_oncampus_2021"), # int
    "fondlings 2020": ("FONDL20", "crime_oncampus_2021"), # int
    "fondlings 2019": ("FONDL19", "crime_oncampus_2021"), # int

    "murders 2021": ("MURD21", "crime_oncampus_2021"), # int
    "murders 2020": ("MURD20", "crime_oncampus_2021"), # int
    "murders 2019": ("MURD19", "crime_oncampus_2021"), # int

    "robberies 2021": ("ROBBE21", "crime_oncampus_2021"), # int
    "robberies 2020": ("ROBBE20", "crime_oncampus_2021"), # int
    "robberies 2019": ("ROBBE19", "crime_oncampus_2021"), # int
    
    "burglaries 2021": ("BURGLA21", "crime_oncampus_2021"), # int
    "burglaries 2020": ("BURGLA20", "crime_oncampus_2021"), # int
    "burglaries 2019": ("BURGLA19", "crime_oncampus_2021"), # int

    "murders 2021": ("MURD21", "crime_oncampus_2021"), # int
    "murders 2020": ("MURD20", "crime_oncampus_2021"), # int
    "murders 2019": ("MURD19", "crime_oncampus_2021"), # int

    "total": ("total", "crime_oncampus_2021"), # int

    # enrollment_summary
    "men enrolled": ("Enrollment_Men", "enrollment_summary"), # int
    "women enrolled": ("Enrollment_Women", "enrollment_summary"), # int
    "total enrollment": ("Enrollment_Total", "enrollment_summary"), # int
    "undergraduate enrollment": ("Enrollment_Undergraduate", "enrollment_summary"), # int

    # us_news_2022
    "us_news_2022": ("us_news_2022",  "us_news_2022"),
}

# def make_reference_table(column_values):
#     value_reference = {
#         True: "",
#         False: "",
#     }

#     index = 0
#     while index < len(column_values):
#         if column_values[index].lower().strip() not in {"not applicable", "na", "n/a", "none"}:


#         index += 1
    
#     if column_values[index].lower().strip() == "yes":
#         value_reference[True] = column_values[index]

    
        


cursor.execute('SELECT DISTINCT in_district_average_tuition_for_full_time_undergraduates FROM ic2021_ay_summary')

print(cursor.fetchall())

for key, table_reference_names in searches.items():
    table_column_name = table_reference_names[0]
    table_name = table_reference_names[1]

    cursor.execute(f"SELECT DISTINCT {table_column_name} FROM {table_name}")
    bad_distinct_values = cursor.fetchall()
    
    distinct_values = []
    for value in distinct_values:
        distinct_values.append(value[0])
    
    if distinct_values[0].type == int:
        searches[key].append(None)
    elif distinct_values[0].type == str:
        if 