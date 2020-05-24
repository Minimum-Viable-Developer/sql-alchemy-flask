import csv
import requests
import json
import names
import random


with open("head-data.csv", encoding="utf-16") as csvfile:
    reader = csv.DictReader(csvfile)
    list_of_dicts = []
    for row_ in reader:

        print(row_)
        
        row =      {"name": names.names_random(),
                    "birth_date_time": random.randint(1543536000, 1575072000),
                    "species": {
                        "scientific_name": row_["species"],
                        "common_name": row_["common_name"],
                        "genus": {"scientific_name": row_["species"].split()[0]}
                            }
                }
        list_of_dicts.append(row)

headers = {"Content-Type": "application/json"}
url = "http://127.0.0.1:5000/specimens"
response = requests.post(url, json=list_of_dicts, headers=headers)
print(response.headers)
