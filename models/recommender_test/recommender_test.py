import sqlite3
import pandas as pd
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

connection = sqlite3.connect("../../data/colleges.sqlite")
colleges_df = pd.read_sql_query("SELECT * FROM hd2021_summary", connection)

# number_columns = []
# 
# for index, dtype in enumerate(colleges_df.dtypes):
#     if dtype == np.int64 or dtype == np.float64:
#         number_columns.append(index)


is_num = [dtype == np.int64 or dtype == np.float64 for dtype in colleges_df.dtypes]
is_string = [dtype != np.int64 or dtype != np.float64 for dtype in colleges_df.dtypes]

number_colleges_df = colleges_df.loc[:, is_num]
string_colleges_df = colleges_df.loc[:, is_string]


MODEL_URL = "https://tfhub.dev/google/universal-sentence-encoder/4"
model = hub.load(MODEL_URL)

print(f"model {MODEL_URL} is loaded")

largest_program = list(string_colleges_df["Largest_Program"].head())

embedded_largest_program_names = model(largest_program)
for index, message_embedding in enumerate(np.array(embedded_largest_program_names).tolist()):
    print(f"Program: {largest_program[index]}")
    print(f"Embedding: {message_embedding}")