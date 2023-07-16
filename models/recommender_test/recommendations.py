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
            column_with_unitid = table_df[["UNITID", column_name]].dropna() # this is for joining the column back into the database
            column_closeness_embeddings = find_embeddings_closeness(list(column_with_unitid[column_name]), use)

            column_with_unitid.replace({column_name: column_closeness_embeddings}, inplace=True)
            
            columns.append(column_with_unitid)    
    
    return columns



def recommend_from_keyword(key_word, column_name, table_name):
    connection = sqlite3.connect("../../data/colleges.sqlite")
    use = hub.load(USE_URL)

    table_df = pd.read_sql_query(f"SELECT * FROM {table_name}", connection)

    column_with_unitid = table_df[["UNITID", column_name]].dropna()
    closeness = find_embeddings_closeness(list(column_with_unitid[column_name]) + key_word, use)


    

# # find top 10 for specific embedding
# values_for_specific = list(result.values())[2]
# top_values = list(values_for_specific.keys())
# top_values.sort(reverse=True)
# print(top_values[:10])
# print([values_for_specific[value] for value in top_values[:10]])


