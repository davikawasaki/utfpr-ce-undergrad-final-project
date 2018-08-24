#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from classes.DatabaseManipulation import DatabaseManipulation
import json

# QC-BD: 2115 questions
# RDC-BD: 2334 questions
# BD Total: 4449 questions

# QC-RC: 2615 questions
# RDC-RC: 2868 questions
# RC Total: 5483 questions

main_folder = '../crawlers/output/iteration-01/'
input_files_db = [
    'questao-certa-crawler-banco-de-dados-resultados.json',
    'rota-dos-concursos-crawler-banco-de-dados-resultados.json'
]
input_files_rc = [
    'questao-certa-crawler-redes-de-computadores-resultados.json',
    'rota-dos-concursos-crawler-redes-de-computadores-resultados.json'
]

flog = "logs/logs_json_to_db_iter_001.json"
output_logs = []

count = 0
quest_img_count = 0
database = "tcc"
collection_db = "quest_db_iter_01"
collection_rc = "quest_rc_iter_01"

db = DatabaseManipulation("mongo")

for file in input_files_db:
    json_data = {}
    with open(main_folder + file, "r") as f:
        json_data = json.load(f)
        for quest in json_data["ext_quest_list"]:
            quest["theme"] = json_data["theme"]
            if len(quest["question_imgs"]) > 0:
                quest_img_count += 1
        db.insert_many(database, collection_db, json_data["ext_quest_list"])
        count += len(json_data["ext_quest_list"])
        output_logs.append({
            "theme": json_data["theme"],
            "file": file.split(".json")[0],
            "total_questions": len(json_data["ext_quest_list"]),
            "questions_with_image": quest_img_count,
            "collection_name": collection_db
        })

quest_img_count = 0

for file in input_files_rc:
    json_data = {}
    with open(main_folder + file, "r") as f:
        json_data = json.load(f)
        for quest in json_data["ext_quest_list"]:
            quest["theme"] = json_data["theme"]
        db.insert_many(database, collection_rc, json_data["ext_quest_list"])
        count += len(json_data["ext_quest_list"])
        output_logs.append({
            "theme": json_data["theme"],
            "file": file.split(".json")[0],
            "total_questions": len(json_data["ext_quest_list"]),
            "questions_with_image": quest_img_count,
            "collection_name": collection_rc
        })

with open(flog, 'w+') as f:
    json.dump(output_logs, f)

print str(count) + ' questões inseridas no banco de dados!'