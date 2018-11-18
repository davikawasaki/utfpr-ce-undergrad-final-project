#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""Script used for iteration 01 to populate MongoDB with themes questions.

Runs through all JSON files from each theme (extracted from /crawler scripts folder)
and input all questions in their specific collection.
Outputs the a JSON log file with details of added collection (see logs/ folder). Example:

    "questions_with_image": 378,
    "collection_name": "quest_db_iter_01",
    "theme": "Banco de Dados",
    "file": "questao-certa-crawler-banco-de-dados-resultados",
    "total_questions": 2115

Total of Questao Certa Website for Database:             2115 questions
Total of Rota do Concurso Website for Database:          2334 questions
Database total:                                          4449 questions

Total of Questao Certa Website for Network Computer:     2615 questions
Total of Rota do Concurso Website for Network Computer:  2868 questions
Network Computer total:                                  5483 questions

"""

from classes.DatabaseManipulation import DatabaseManipulation
import json

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
database = "tcc"
collection_db = "quest_db_iter_01"
collection_rc = "quest_rc_iter_01"

db = DatabaseManipulation("mongo")

quest_img_count = 0
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