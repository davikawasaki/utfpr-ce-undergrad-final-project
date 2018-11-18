#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""Script used for iteration 03 to populate MongoDB with themes questions.
todo: let it be generic to be called with params

Runs through all JSON files from each theme (extracted from /crawler scripts folder)
and input all questions in their specific collection.
Outputs the a JSON log file with details of added collection. Example:

    "questions_with_image": 47,
    "collection_name": "quest_ac_iter_02",
    "theme": "Arquitetura de Computadores",
    "file": "questao-certa-crawler-arquitetura-de-computadores-resultados",
    "total_questions": 670

methods:
    " >>> _insert_questions_from_file(file, collection_name)

"""

# APPEND HERE THE PROJECT FULL PATH TO RUN FROM TERMINAL
# import sys
# sys.path.append("/home/kawasaki/Git/utfpr/tcc/utfpr-ce-undegrad-final-project/")

from classes.DatabaseManipulation import DatabaseManipulation
import json
import os
import re


def _insert_questions_from_file(file, collection_name):
    """Get file and insert into collection.
        Insert data from inner 'ext_quest_list' object.

    :param file:
    :param collection_name:
    :return inserted_length:
    """
    count_img = 0
    with open(file, "r") as f:
        json_data = json.load(f)
        for quest in json_data["ext_quest_list"]:
            quest["theme"] = json_data["theme"]
            if len(quest["question_imgs"]) > 0:
                count_img += 1
        db.insert_many(db_name_env, collection_name, json_data["ext_quest_list"])
        output_logs.append({
            "theme": json_data["theme"],
            "file": file.split(".json")[0],
            "total_questions": len(json_data["ext_quest_list"]),
            "questions_with_image": count_img,
            "collection_name": collection_name
        })
        return len(json_data["ext_quest_list"])


# Folders with JSON inputs
qc_folder = '../crawlers/output/questao-certa'
rc_folder = '../crawlers/output/rota-dos-concursos'
rc_files_added = []

flog = "logs/logs_json_to_db.json"
output_logs = []
quest_count = 0

# CHANGE HERE TO ALLOW DIFFERENT DB_NAMES
db_name_local = "tccprod"
db_name_prod = "tccprod"
db_name_env = db_name_prod
db_env = "prod"

# JSON files to be read follow the regex pattern below
regex = '(.*-crawler-)(.*)(-resultados.json)'

db = DatabaseManipulation("mongo", db_env)

# Start with questions from questao certa folder
for flname_qc in os.listdir(qc_folder):
    qc_rc_status = False
    if flname_qc.endswith(".json"):
        # print(os.path.join(directory, filename))
        re_search_qc = re.search(regex, flname_qc)
        if re_search_qc is not None:
            collection_name = re_search_qc.group(2).replace('-', '_')
            flname_rc_temp = None

            for flname_rc in os.listdir(rc_folder):
                if flname_rc.endswith(".json"):
                    re_search_rc = re.search(regex, flname_rc)
                    if re_search_rc is not None:
                        if re_search_qc.group(2) == re_search_rc.group(2):
                            qc_rc_status = True
                            flname_rc_temp = flname_rc
                            break
            quest_count += _insert_questions_from_file(qc_folder + "/" + flname_qc, collection_name)
            if qc_rc_status is True and flname_rc_temp is not None:
                quest_count += _insert_questions_from_file(rc_folder + "/" + flname_rc_temp, collection_name)
                rc_files_added.append(flname_rc_temp)

# Finish with questions from rota dos concursos folder
for flname_rc in os.listdir(rc_folder):
    if flname_rc.endswith(".json"):
        if flname_rc not in rc_files_added:
            re_search_rc = re.search(regex, flname_rc)
            if re_search_rc is not None:
                collection_name = re_search_rc.group(2).replace('-', '_')
                quest_count += _insert_questions_from_file(rc_folder + "/" + flname_rc, collection_name)

with open(flog, 'w+') as f:
    json.dump(output_logs, f)

print str(quest_count) + ' questões inseridas no banco de dados!'