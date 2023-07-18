# %%
# install dependencies
import sqlite3
import pandas as pd
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

# connect to database
USE_URL = "https://tfhub.dev/google/universal-sentence-encoder/4"

def find_embeddings_closeness(column, model):
    unique_items = list(set(column))
    embedded_items = np.array(model(unique_items)).tolist()

    reverse_lookup = dict(zip(unique_items, embedded_items))

    全体のcloseness = {}
    for item, embedding in reverse_lookup.items():
        closeness = {}
        for other_item, other_embedding in reverse_lookup.items():
            # the closeness in relation to the other categories
            closeness[np.inner(embedding, other_embedding)] = other_item

        全体のcloseness[item] = closeness
    
    return 全体のcloseness


def find_closeness(table_columns: dict):
    connection = sqlite3.connect("../../data/colleges.sqlite")
    use = hub.load(USE_URL)
    
    columns = []

    for table_name, column_names in table_columns.items():
        table_df = pd.read_sql_query(f"SELECT * FROM {table_name}", connection)

        for column_name in column_names:
            # column_with_unitid = table_df[["UNITID", column_name]].dropna() # this is for joining the column back into the database
            column_with_unitid = table_df[["codes", column_name]].dropna() # this is for joining the column back into the database
            column_closeness_embeddings = find_embeddings_closeness(list(column_with_unitid[column_name]), use)

            column_with_unitid.replace({column_name: column_closeness_embeddings}, inplace=True)
            
            columns.append(column_with_unitid)    
    
    return columns


def recommend_from_keyword(keyword, column_name, table_name):
    connection = sqlite3.connect("../../data/colleges.sqlite")
    use = hub.load(USE_URL)

    table_df = pd.read_sql_query(f"SELECT * FROM {table_name}", connection)

    # gets the needed colum with the unitid so it can be merged back
    # column_with_unitid = table_df[["UNITID", column_name]].dropna()
    column_with_unitid = table_df[["code", column_name]].dropna()

    unique_items = list(set(column_with_unitid[column_name]))
    unique_items.insert(0, keyword)
    embedded_items = np.array(use(unique_items)).tolist()

    # gets the keyword out of the dictionary later because it is needed for later
    keyword_data = (unique_items.pop(0), embedded_items.pop(0))
    embeddings_dict = dict(zip(unique_items, embedded_items))

    近さ = {}

    # get the closeness and add it to a list
    for item, embedding in embeddings_dict.items():
        closeness = np.inner(keyword_data[1], embedding)
        近さ[item] = closeness

    column_with_unitid[f"{column_name}_embeddings"] = column_with_unitid.loc[:, column_name]

    return column_with_unitid.replace({f"{column_name}_embeddings": 近さ}).sort_values(f"{column_name}_embeddings", ascending=False)

# print(recommend_from_keyword(input("Enter a keyword: "), "title", "cipcodes"))

print(find_closeness({"cipcodes": "title"}))

    

# # find top 10 for specific embedding
# values_for_specific = list(result.values())[2]
# top_values = list(values_for_specific.keys())
# top_values.sort(reverse=True)
# print(top_values[:10])
# print([values_for_specific[value] for value in top_values[:10]])