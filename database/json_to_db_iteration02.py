#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""Script used for iteration 02 to populate MongoDB with themes questions.

Runs through all JSON files from each theme (extracted from /crawler scripts folder)
and input all questions in their specific collection.
Outputs the a JSON log file with details of added collection. Example:

    "questions_with_image": 47,
    "collection_name": "quest_ac_iter_02",
    "theme": "Arquitetura de Computadores",
    "file": "questao-certa-crawler-arquitetura-de-computadores-resultados",
    "total_questions": 670

Themes: Computer Architecture, Information Security, Operation Systems

"""

from classes.DatabaseManipulation import DatabaseManipulation
import json

main_folder = '../crawlers/output/iteration-02/'
input_files_ac = [
    'questao-certa-crawler-arquitetura-de-computadores-resultados.json',
    'rota-dos-concursos-crawler-arquitetura-de-computadores-resultados.json'
]
input_files_si = [
    'questao-certa-crawler-seguranca-da-informacao-resultados.json',
    'rota-dos-concursos-crawler-seguranca-da-informacao-resultados.json'
]
input_files_so = [
    'questao-certa-crawler-sistemas-operacionais-resultados.json',
    'rota-dos-concursos-crawler-sistemas-operacionais-resultados.json'
]
flog = "logs/logs_json_to_db_iter_002.json"
output_logs = []

count = 0
database = "tcc"
collection_ac = "quest_ac_iter_02"
collection_si = "quest_si_iter_02"
collection_so = "quest_so_iter_02"

db = DatabaseManipulation("mongo")

quest_img_count = 0
for file in input_files_ac:
    json_data = {}
    with open(main_folder + file, "r") as f:
        json_data = json.load(f)
        for quest in json_data["ext_quest_list"]:
            quest["theme"] = json_data["theme"]
            if len(quest["question_imgs"]) > 0:
                quest_img_count += 1
        db.insert_many(database, collection_ac, json_data["ext_quest_list"])
        count += len(json_data["ext_quest_list"])
        output_logs.append({
            "theme": json_data["theme"],
            "file": file.split(".json")[0],
            "total_questions": len(json_data["ext_quest_list"]),
            "questions_with_image": quest_img_count,
            "collection_name": collection_ac
        })

quest_img_count = 0
for file in input_files_si:
    json_data = {}
    with open(main_folder + file, "r") as f:
        json_data = json.load(f)
        for quest in json_data["ext_quest_list"]:
            quest["theme"] = json_data["theme"]
        db.insert_many(database, collection_si, json_data["ext_quest_list"])
        count += len(json_data["ext_quest_list"])
        output_logs.append({
            "theme": json_data["theme"],
            "file": file.split(".json")[0],
            "total_questions": len(json_data["ext_quest_list"]),
            "questions_with_image": quest_img_count,
            "collection_name": collection_si
        })

quest_img_count = 0
for file in input_files_so:
    json_data = {}
    with open(main_folder + file, "r") as f:
        json_data = json.load(f)
        for quest in json_data["ext_quest_list"]:
            quest["theme"] = json_data["theme"]
        db.insert_many(database, collection_so, json_data["ext_quest_list"])
        count += len(json_data["ext_quest_list"])
        output_logs.append({
            "theme": json_data["theme"],
            "file": file.split(".json")[0],
            "total_questions": len(json_data["ext_quest_list"]),
            "questions_with_image": quest_img_count,
            "collection_name": collection_so
        })

with open(flog, 'w+') as f:
    json.dump(output_logs, f)

print str(count) + ' questões inseridas no banco de dados!'