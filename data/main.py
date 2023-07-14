from flask import Flask, jsonify, request, abort, url_for, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context

import pandas as pd
import numpy as np
import sqlite3

import functools
import os
import base64

#college data
colleges_df = pd.read_csv("data/single_college_data_completed.csv", low_memory=False)
colleges_df = colleges_df.set_index("UNITID")

colleges_df.fillna("NaN", inplace=True)

single_colleges_data = colleges_df.to_dict(orient='index')


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
# app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True

db = SQLAlchemy(app)

column_lookup = {
    # hd2021_summary
    "college name": ("College_Name", "hd2021_summary", "string"), 
    "college alias": ("College_Alias_Also_Known_As", "hd2021_summary", "string"), 
    "college address": ("Address", "hd2021_summary", "string"), 
    "closest city": ("City", "hd2021_summary", "string"), 
    "state": ("State", "hd2021_summary", "string"), 
    "zip code": ("Zip_Code", "hd2021_summary", "string"), 
    "current president": ("Name_of_Chief_Administrator_of_Institution", "hd2021_summary", "string"), 
    "current president title": ("Title_of_Chief_Administrator_of_Institution", "hd2021_summary", "string"), 
    "web address": ("Website_Address", "hd2021_summary", "string"), 
    "admissions office url": ("Admissions_Office_URL", "hd2021_summary", "string"), 
    "financial aid office url": ("Financial_Aid_Office_URL", "hd2021_summary", "string"), 
    "application url": ("Online_Application_URL", "hd2021_summary", "string"), 
    "price calculator url": ("Net_Price_Calculator_URL", "hd2021_summary", "string"), 
    "institution level": ("Level_of_institution", "hd2021_summary", "enum"), # in years
    "college type": ("Private_or_Public_Control_of_institution", "hd2021_summary", "enum"), 
    "highest degree level": ("Highest_Level_Offered", "hd2021_summary", "enum"), 
    "offers undergraduate degree": ("Offers_Undergraduate_Degrees", "hd2021_summary", "bool"), 
    "offers graduate degree": ("Offers_Graduate_Degrees", "hd2021_summary", "bool"), 
    "is degree granting": ("Degree_Granting_Status", "hd2021_summary", "enum"), 
    "is historically black": ("Is_Historically_Black_College_or_University", "hd2021_summary", "bool"), 
    "has hospital": ("Has_Hospital", "hd2021_summary", "bool"), 
    "offers medical degree": ("Offere_Medicine_Degrees", "hd2021_summary", "bool"), # on the table
    "is tribal college": ("Is_Tribal_College", "hd2021_summary", "bool"), 
    "size of city/town": ("Degree_of_urbanization", "hd2021_summary", "enum"), 
    "is out of business": ("Date_Institution_Closed", "hd2021_summary", "bool"), 
    "carnegie classification": ("Carnegie_Basic_Classification", "hd2021_summary", "enum"), #  <-- not sure tho
    "enrollment profile": ("'Carnegie Classification 2021': (Enrollment Profile", "hd2021_summary", "enum"), 
    "size and setting": ("'Carnegie Classification 2021': (Size and Setting", "hd2021_summary", "enum"), 
    "institution size": ("Institution_Size", "hd2021_summary", "enum"), #is in categories
    "multi campus": ("'Multi-institution or multi-campus organization'", "hd2021_summary", "string"), 
    "multi campus system name": ("'Name of multi-institution or multi-campus organization'", "hd2021_summary", "string"), 
    "longitude": ("Longitude", "hd2021_summary", "double"), 
    "latitude": ("Latitude", "hd2021_summary", "double"), 
    
    # ic2021_summary
    "can study abroad": ("Study_abroad", "ic2021_summary", "bool"), # IMPORTANT
    "is occupational": ("Occupational", "ic2021_summary", "bool"), 
    "is academic": ("Academic", "ic2021_summary", "bool"), 
    "is religious": ("Religious_affiliation", "ic2021_summary", "bool"), #  <--- make starts int if > 0
    "dual enrollment": ("Dual_enrollment", "ic2021_summary", "bool"), 
    "credit for life experiences": ("Credit_for_life_experiences", "ic2021_summary", "bool"), 
    "takes ap credits": ("Advanced_placement_AP_credits", "ic2021_summary", "bool"), 
    
    # ic2021_ay_summary
    "in district average tuition (undergraduate)": ("in_district_average_tuition_for_full_time_undergraduates", "ic2021_ay_summary", "int"), 
    "in district required fees (undergraduates)": ("in_district_required_fees_for_full_time_undergraduates", "ic2021_ay_summary", "int"), 
    
    # # ic2021_py_summary
    # "largest program": ("largest_program", "ic2021_py_summary", "string"), 
    # "second largest program": ("second_largest_program", "ic2021_py_summary", "string"), 
    # "third largest program": ("third_largest_program", "ic2021_py_summary", "string"), 
    # "fourth largest program": ("fourth_largest_program", "ic2021_py_summary", "string"), 
    # "fifth largest program": ("fifth_largest_program", "ic2021_py_summary", "string"), 
    # "sixth largest program": ("sixth_largest_program", "ic2021_py_summary", "string"), 
    # "number of programs": ("Number_of_program_offered", "ic2021_py_summary", "int"), 
    # # "cost of books and supplies for first largest program": ("Cost_of_books_and_supplies_of_1st_largest_program", "ic2021_py_summary", "int"), 
    # "cost of books and supplies for second largest program": ("Cost_of_books_and_supplies_of_2nd_largest_program", "ic2021_py_summary", "int"), 
    # "cost of books and supplies for third largest program": ("Cost_of_books_and_supplies_of_3rd_largest_program", "ic2021_py_summary", "int"), 
    # "cost of books and supplies for fourth largest program": ("Cost_of_books_and_supplies_of_4th_largest_program", "ic2021_py_summary", "int"), 
    # "cost of books and supplies for fifth largest program": ("Cost_of_books_and_supplies_of_5th_largest_program", "ic2021_py_summary", "int"), 
    # "cost of books and supplies for sixth largest program": ("Cost_of_books_and_supplies_of_6th_largest_program", "ic2021_py_summary", "int"), 
    
    # c2021_a_summary
    # "largest program": (""),

    # adm2021_summary
    "total applicants": ("Applicants_total", "adm2021_summary", "int"),
    "total offers": ("Admissions_total", "adm2021_summary", "int"),
    "total enrolled": ("Enrolled_total", "adm2021_summary", "int"),
    "sat english 25th percentile": ("SAT_Evidence_Based_Reading_and_Writing_25th_percentile_score", "adm2021_summary", "int"),
    "sat english 75th percentile": ("SAT_Evidence_Based_Reading_and_Writing_75th_percentile_score", "adm2021_summary", "int"),
    "sat math 25th percentile": ("SAT_Math_25th_percentile_score", "adm2021_summary", "int"),
    "sat math 75th percentile": ("SAT_Math_75th_percentile_score", "adm2021_summary", "int"),
    "act 25th percentile": ("ACT_Composite_25th_percentile_score", "adm2021_summary", "int"),
    "act 75th percentile": ("ACT_Composite_75th_percentile_score", "adm2021_summary", "int"),
    "act english 25th percentile": ("ACT_English_25th_percentile_score", "adm2021_summary", "int"),
    "act english 75th percentile": ("ACT_English_75th_percentile_score", "adm2021_summary", "int"),
    "act math 25th percentile": ("ACT_Math_25th_percentile_score", "adm2021_summary", "int"),
    "act math 75th percentile": ("ACT_Math_75th_percentile_score", "adm2021_summary", "int"),

    # crime_oncampus_2021
    "rapes 2021": ("RAPE21", "crime_oncampus_2021", "int"), 
    "rapes 2020": ("RAPE20", "crime_oncampus_2021", "int"), 
    "rapes 2019": ("RAPE19", "crime_oncampus_2021", "int"), 

    "fondlings 2021": ("FONDL21", "crime_oncampus_2021", "int"), 
    "fondlings 2020": ("FONDL20", "crime_oncampus_2021", "int"), 
    "fondlings 2019": ("FONDL19", "crime_oncampus_2021", "int"), 

    "murders 2021": ("MURD21", "crime_oncampus_2021", "int"), 
    "murders 2020": ("MURD20", "crime_oncampus_2021", "int"), 
    "murders 2019": ("MURD19", "crime_oncampus_2021", "int"), 

    "robberies 2021": ("ROBBE21", "crime_oncampus_2021", "int"), 
    "robberies 2020": ("ROBBE20", "crime_oncampus_2021", "int"), 
    "robberies 2019": ("ROBBE19", "crime_oncampus_2021", "int"), 
    
    "burglaries 2021": ("BURGLA21", "crime_oncampus_2021", "int"), 
    "burglaries 2020": ("BURGLA20", "crime_oncampus_2021", "int"), 
    "burglaries 2019": ("BURGLA19", "crime_oncampus_2021", "int"), 

    "murders 2021": ("MURD21", "crime_oncampus_2021", "int"), 
    "murders 2020": ("MURD20", "crime_oncampus_2021", "int"), 
    "murders 2019": ("MURD19", "crime_oncampus_2021", "int"), 

    "total crime": ("total", "crime_oncampus_2021", "int"), 

    # enrollment_summary
    "men enrolled": ("Enrollment_Men", "enrollment_summary", "int"), 
    "women enrolled": ("Enrollment_Women", "enrollment_summary", "int"), 
    "total enrollment": ("Enrollment_Total", "enrollment_summary", "int"), 
    "undergraduate enrollment": ("Enrollment_Undergraduate", "enrollment_summary", "int"), 
    "graduate enrollment": ("Enrollment_Graduate", "enrollment_summary", "int"), 
    "fulltime faculty": ("Fulltime_Faculty", "enrollment_summary", "int"), 
    "student faculty ratio": ("student_to_faculty_ratio", "enrollment_summary", "int"), 

    # us_news_2022
    "us_news_2022": ("us_news_2022",  "us_news_2022"),
    
    # rankings table
    "cost": ("cost", "rankings", {1: "cheap", 5: "expensive"}, False), # one
    "community safety": ("community_safety", "rankings", {1: "least safe", 5: "most safe"}, False), # one
    "traffic": ("traffic", "rankings", {1: "less traffic", 5: "most traffic"}, False), # one
    "community diversity": ("community_diversity", "rankings", {1: "least diverse", 5: "most diverse"}, False), # one
    "weather": ("weather", "rankings", {1: "cold", 5: "hot"}, True), # two
    "population density": ("population_density", "rankings", {1: "not crowded", 5: "crowded"}, True), # two
}


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email= db.Column(db.String(32), index=True, nullable=False)
    first_name = db.Column(db.String(32), nullable=False)
    last_name = db.Column(db.String(32), nullable=False)
    password_hash = db.Column(db.String(128))

    def hash_password(self, password):
        print(id)
        self.password_hash = pwd_context.hash(password)
    
    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


HOME_1_0 = "/lucid_degree/api/v1.0"
KEY = "$6$rounds=656000$43diYjLBFHznLrF8$lnc1128JQFlvAvNfLiuk/NWgv9o3LjLjEm1aE.Dz3oKFUZFIdmVkXmG3idsQ/NCd5.QHvgD0FSyfghy4T4y8u1"

def collapse_list(input_list):
    output_list = []
    for item in input_list:
        if type(item) == list:
            output_list.extend(collapse_list(item))
        else:
            output_list.extend(item)
    
    return output_list

def requires_user_authentication(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("authorization")
        if not auth_header:
            abort(401)
        
        auth_parts = auth_header.split() # splits the authentication header into the type of authentication and the actual authentication password/key
        if len(auth_parts) != 2:
            abort(401)

        if auth_parts[0].lower() != "basic":
            abort(401)
        
        # gets the credentials from the authentication header
        credentials = base64.b64decode(auth_parts[1]).decode("utf-8")
        email, password = credentials.split(":")

        # finds the user from the password
        user = User.query.filter_by(email = email).first()
        
        if not user or not user.verify_password(password):
            abort(403)
        else:
            return function(*args, **kwargs)     
                            
    return wrapper


def requires_token(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):

        auth_header = request.headers.get("www-authenticate")
        if not auth_header:
            abort(401)
        
        auth_parts = auth_header.split() # splits the authentication header into the type of authentication and the actual authentication password/key
        if len(auth_parts) != 2:
            abort(401)

        if auth_parts[0].lower() != "token":
            abort(401)
        credentials = base64.b64decode(auth_parts[1]).decode("utf-8")
        name, token = credentials.split(":")


        if name != "evan" or not pwd_context.verify(token, KEY):
            abort(403)
        else:
            return function(*args, **kwargs)
    
    return wrapper

    

# gets the college data by id
@requires_token
@app.route(f"{HOME_1_0}/single_college_data/<int:unit_id>", methods=["GET"])
def get_college_by_id(unit_id):
    if unit_id in single_colleges_data.keys():
        return jsonify({unit_id: single_colleges_data[unit_id]})
    else:
        print("no college with that id exists")
        abort(400)



@requires_token
@app.route(f"{HOME_1_0}/colleges/<int:unit_id>", methods=["POST"])
def get_single_college(unit_id):
    column_names = request.json.get("columns")
    
    requests = {}

    reverse_lookup = {}

    output = {}
    connection = sqlite3.connect("data/colleges.sqlite")
    connection.row_factory = sqlite3.Row
    cursor  = connection.cursor()
    for column_name in column_names:
        table_column_name = column_lookup[column_name][0]
        table_name = column_lookup[column_name][1]

        if requests.get(table_name):
            requests[table_name].append(table_column_name)
        else:
            requests[table_name] = [table_column_name]

        reverse_lookup[table_column_name] = column_name

    # print(requests)

    for table_name, table_column_names in requests.items():
        term = f"SELECT DISTINCT {', '.join(table_column_names)} FROM {table_name} WHERE UNITID={unit_id}"
        cursor.execute(term)

        sqlOutput = cursor.fetchone()
        if sqlOutput:
            # print("runs")
            for index, value in dict(sqlOutput).items():
                column_name = reverse_lookup[index]
                # data_type = reverse_lookup[index][1]
                output[column_name] = value
        # else:
            # print(cursor.fetchall())
        
        cursor.fetchall()

    return jsonify({f"{unit_id}": (output)})

@requires_token
@app.route(f"{HOME_1_0}/colleges/search", methods=["POST"])
def search_colleges():
    columns = request.json.get("columns")
     
    connection = sqlite3.connect("data/colleges.sqlite")
    # connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # search_columns = []
    search_terms = []
    joins = [] # JOIN {table} on {table}.UNITID

    output = []


    for column_name, search_parameter in columns.items():
        table_column_name = column_lookup[column_name][0]
        table_name = column_lookup[column_name][1]

        # can study abroad = bool
        if column_name == "can study abroad":
            table_search_parameter = (f"{table_column_name}='Yes'" if search_parameter else f"{table_column_name}'No' OR {table_column_name}='Not Applicable'")

        if column_name == "cost of books and supplies for second largest program":
            table_search_parameter = f"{table_column_name}{search_parameter[0]}={search_parameter[1]}" # <---- column_name >= number

        if column_name == "cost": # reversed
            rank = search_parameter["rank"]
            maximum_value = 6 - rank + 1
            ranges = ', '.join(list(map(str, range(maximum_value))))
            table_search_parameter = f"{table_column_name} IN ({ranges})" + (" OR cost=NULL" if rank==5 else "")
            # table_search_parameter = f"{table_column_name} IN ({', '.join(range(7-rank))})" + (" OR cost=NULL" if rank==5 else "")

        if column_name == "community safety":
            rank = search_parameter["rank"]
            maximum_value = rank + 1
            ranges = ', '.join(list(map(str, range(maximum_value))))
            table_search_parameter = f"{table_column_name} IN ({ranges})" + (" OR cost=NULL" if rank==1 else "")

        if column_name == "traffic": # reversed
            rank = search_parameter["rank"]
            maximum_value = 6 - rank + 1
            ranges = ', '.join(list(map(str, range(maximum_value))))
            table_search_parameter = f"{table_column_name} IN ({ranges})" + (" OR cost=NULL" if rank==5 else "")

        if column_name == "weather":
            rank = search_parameter["rank"]
            matters = 5 - search_parameter["matters"]
            minimum_value = max(rank-matters, 1)
            maximum_value = min(rank+matters, 5) + 1
            ranges = ', '.join(list(map(str, range(minimum_value, maximum_value))))
            table_search_parameter = f"{table_column_name} IN ({ranges})" # OR NULL
        
        if column_name == "population density":
            rank = search_parameter["rank"]
            matters = 5 - search_parameter["matters"]
            minimum_value = max(rank-matters, 1)
            maximum_value = min(rank+matters, 5) + 1
            ranges = ', '.join(list(map(str, range(minimum_value, maximum_value))))
            table_search_parameter = f"{table_column_name} IN ({ranges})" # OR NULL
            # table_search_parameter = f"{table_column_name} IN ({', '.join(range(max(rank-matters, 1), min(rank+matters, 5) + 1))})" # OR NULL


        # search_columns.append(table_column_name)
        search_terms.append(table_search_parameter)
        if table_name not in joins:
            joins.append(table_name)

    join_string = ""
    for index, table_name in enumerate(joins):
        if index == 0:
            join_string += f"{table_name}"
        else:
            join_string += f" JOIN {table_name} ON {table_name}.UNITID = {joins[0]}.UNITID"

    term = f"SELECT DISTINCT {joins[0]}.UNITID FROM {join_string} WHERE {' AND '.join(search_terms)}"
    print(term)
    cursor.execute(term)
    output.append(cursor.fetchall())

    output = collapse_list(output)

    return output


@requires_token
@app.route(f"{HOME_1_0}/colleges/search/<string:college_name>", methods=["POST"])
def search_with_name(college_name):
    print(college_name)
    
    columns = request.json.get("columns")
     
    connection = sqlite3.connect("data/colleges.sqlite")
    # connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # search_columns = []
    search_terms = []
    joins = ["hd2021_summary"] # JOIN {table} on {table}.UNITID

    output = []

    if columns:
        for column_name, search_parameter in columns.items():
            table_column_name = column_lookup[column_name][0]
            table_name = column_lookup[column_name][1]

            # can study abroad = bool
            if column_name == "can study abroad":
                table_search_parameter = (f"{table_column_name}='Yes'" if search_parameter else f"{table_column_name}'No' OR {table_column_name}='Not Applicable'")

            if column_name == "cost of books and supplies for second largest program":
                table_search_parameter = f"{table_column_name}{search_parameter[0]}={search_parameter[1]}" # <---- column_name >= number

            if column_name == "cost": # reversed
                rank = search_parameter["rank"]
                maximum_value = 6 - rank + 1
                ranges = ', '.join(list(map(str, range(maximum_value))))
                table_search_parameter = f"{table_column_name} IN ({ranges})" + (" OR cost=NULL" if rank==5 else "")
                # table_search_parameter = f"{table_column_name} IN ({', '.join(range(7-rank))})" + (" OR cost=NULL" if rank==5 else "")

            if column_name == "community safety":
                rank = search_parameter["rank"]
                maximum_value = rank + 1
                ranges = ', '.join(list(map(str, range(maximum_value))))
                table_search_parameter = f"{table_column_name} IN ({ranges})" + (" OR cost=NULL" if rank==1 else "")

            if column_name == "traffic": # reversed
                rank = search_parameter["rank"]
                maximum_value = 6 - rank + 1
                ranges = ', '.join(list(map(str, range(maximum_value))))
                table_search_parameter = f"{table_column_name} IN ({ranges})" + (" OR cost=NULL" if rank==5 else "")

            if column_name == "weather":
                rank = search_parameter["rank"]
                matters = 5 - search_parameter["matters"]
                minimum_value = max(rank-matters, 1)
                maximum_value = min(rank+matters, 5) + 1
                ranges = ', '.join(list(map(str, range(minimum_value, maximum_value))))
                table_search_parameter = f"{table_column_name} IN ({ranges})" # OR NULL
            
            if column_name == "population density":
                rank = search_parameter["rank"]
                matters = 5 - search_parameter["matters"]
                minimum_value = max(rank-matters, 1)
                maximum_value = min(rank+matters, 5) + 1
                ranges = ', '.join(list(map(str, range(minimum_value, maximum_value))))
                table_search_parameter = f"{table_column_name} IN ({ranges})" # OR NULL
                # table_search_parameter = f"{table_column_name} IN ({', '.join(range(max(rank-matters, 1), min(rank+matters, 5) + 1))})" # OR NULL

            # search_columns.append(table_column_name)
            search_terms.append(table_search_parameter)
            if table_name not in joins:
                joins.append(table_name)

    join_string = ""
    for index, table_name in enumerate(joins):
        if index == 0:
            join_string += f"{table_name}"
        else:
            join_string += f" JOIN {table_name} ON {table_name}.UNITID = {joins[0]}.UNITID"

    term = f"SELECT DISTINCT {joins[0]}.UNITID FROM {join_string} WHERE {' AND '.join(search_terms)} {'AND' if columns else ''} \
            hd2021_summary.College_Name LIKE \"%{college_name}%\" ORDER BY hd2021_summary.College_Name LIMIT 50"
    print(term)
    cursor.execute(term)
    output.append(cursor.fetchall())

    output = collapse_list(output)

    return output


@requires_token
@app.route(f"{HOME_1_0}/college/search_by_name/<string:college_name>", methods=["GET"])
def search_by_name(college_name):

    

    connection = sqlite3.connect("data/colleges.sqlite")
    cursor = connection.cursor()



    # print("SELECT UNITID, College_Name FROM hd2021_summary WHERE College_Name LIKE \"%{college_name}%\"")

    cursor.execute(f"SELECT DISTINCT UNITID FROM hd2021_summary WHERE College_Name LIKE \"%{college_name}%\" ORDER BY College_Name")

    raw_output = cursor.fetchall()

    output = []
    for nested_unitid in raw_output:
        output.append(str(nested_unitid[0]))

    return jsonify(output)

@app.route(f'{HOME_1_0}/images/<path:path>')
def serve_image(path):
    all_images = os.listdir("images/")
    # print(path)
    
    if path in all_images:
        return send_from_directory('images', path)
    else:
        if str(path).split("_")[-1] == "tn.jpg":
            return send_from_directory('images', "default_tn.jpg")
        else:
            return send_from_directory('images', "default.jpg")

@requires_token
@requires_user_authentication
@app.route(f"{HOME_1_0}/users/<int:id>", methods=["GET"])
def get_user(id):
    user = User.query.get(id)
    if user:
        return jsonify(
            {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            }
        )
    else:
        print("no user with that id exists")
        abort(400)


# makes a new user
@requires_token
@app.route(f"{HOME_1_0}/users", methods=["POST"])
def post_user():
    first_name = request.json.get("first_name")
    last_name = request.json.get("last_name")
    email = request.json.get("email")
    password = request.json.get("password")

    if None in (first_name, last_name, email, password):
        print("does not have all required elements")
        abort(400)
    if User.query.filter_by(email = email).first() != None:
        print("email already exists")
        abort(400)
    
    user = User(first_name=first_name, last_name=last_name, email=email)
    user.hash_password(password)


    db.session.add(user)
    db.session.commit()

    print(user.__dict__)

    return (jsonify({"id": user.id, "first_name": user.first_name, "last_name": user.last_name, "email": user.email}), 
            {"Location": url_for('get_user', id=user.id)})


@requires_token
@requires_user_authentication
@app.route(f"{HOME_1_0}/test", methods=["GET"])
def get_resource():
    return jsonify({"data": "Hello"})


# @requires_token
# @app.route(f"{HOME_1_0}/<str:quiz_type>/<int:index>", methods=["GET"])
# def get_quiz_question(quiz_type, index):
#     return 


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)