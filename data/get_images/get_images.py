import time
import sqlite3
import requests
from bs4 import BeautifulSoup
import WikiCommons
import resize_and_crop as rc

# List of queries
# search_queries = ["Harvard University", "MIT"]
# search_queries = {'1': "Harvard University campus photo", '2': "Auburn University campus photo"}

# connect to the database
conn = sqlite3.connect('../colleges.sqlite')

# Execute SQL script and fetch all rows
cursor = conn.cursor()
cursor.execute('SELECT UNITID as id, College_Name || " campus photo" as search_query FROM hd2021_summary')
search_queries = cursor.fetchall()

# Close the connection
conn.close()

# Directory to save images
download_directory = "images"
thumbnail_size = (340, 270)

# Make sure that the download directory exists
# os.makedirs(download_directory, exist_ok=True)

count = 1
# Iterate through each search query
for id, query in search_queries:
    print(f"{count}\t{query}: ", end="")
    # Construct search URL
    search_url = f"https://commons.wikimedia.org/w/index.php?search={query}&title=Special:MediaSearch&type=image"
    # print(f"Searching: {search_url}")

    # Send HTTP request to the URL
    response = requests.get(search_url)

    # Parse HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the first image. Note: This may change if Wikimedia changes their HTML structure
    # img_tag = soup.find("img")
    a_tag = soup.find("a", class_="sdms-image-result")

    # Extract and save the image
    if a_tag and 'title' in a_tag.attrs:
        image_title = a_tag.attrs['title']
        print(f"Found image: {image_title}")
        WikiCommons.download_commons_image(image_title, download_directory, str(id))

        # create a thumbnail
        image_path = f"{download_directory}/{id}.jpg"
        rc.resize_and_crop(image_path, thumbnail_size)

    else:
        print(f"No image title attribute not found for {query}\n")

    # Sleep for 5 seconds
    count += 1
    time.sleep(5)

print("Finished")