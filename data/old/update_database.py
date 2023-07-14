import pandas as pd

# Assuming you have two DataFrames: crime_oncampus_2021 and enrollment_summary
# For example, they could be read from a database like this:
# crime_oncampus_2021 = pd.read_sql('SELECT * FROM crime_oncampus_2021', connection)
# enrollment_summary = pd.read_sql('SELECT * FROM enrollment_summary', connection)

# Merging the two DataFrames on UNITID
data = pd.merge(crime_oncampus_2021, enrollment_summary, on='UNITID')

# Calculating the weighted total
data['weighted_total'] = data['total'] * data['Enrollment_Total']

# Calculating mean and standard deviation of the weighted total
mean_total = data['weighted_total'].mean()
std_dev = data['weighted_total'].std()

# Calculating the Z-score
data['z_score'] = (data['weighted_total'] - mean_total) / std_dev

# Assigning ranks based on Z-score
data['rank'] = pd.cut(data['z_score'],
                      bins=[-float('inf'), -1.5, -0.5, 0.5, 1.5, float('inf')],
                      labels=[1, 2, 3, 4, 5])

# Updating the original crime_oncampus_2021 DataFrame with the rank
crime_oncampus_2021['rank'] = data['rank']

# At this point, the crime_oncampus_2021 DataFrame has the rank column updated based on the criteria.
# If you want to update the original database, you can write the DataFrame back to the SQLite database.



import sqlite3
import pandas as pd

# Assuming the DataFrame crime_oncampus_2021 is already updated with the rank column as shown in the previous example

# Connect to the SQLite database
connection = sqlite3.connect("your_database_name.db")

# Iterate through each row in the DataFrame and update the rank column in the SQLite table
for index, row in crime_oncampus_2021.iterrows():
    unitid = row['UNITID']
    rank = row['rank']
    
    # SQL query to update the rank column
    sql_query = "UPDATE crime_oncampus_2021 SET rank = ? WHERE UNITID = ?"
    
    # Execute the query
    connection.execute(sql_query, (rank, unitid))

# Commit the changes to the database
connection.commit()

# Close the connection
connection.close()