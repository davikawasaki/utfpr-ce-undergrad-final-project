#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from classes.DatabaseManipulation import DatabaseManipulation
import json, os, re

qc_folder = '../crawlers/output/questao-certa'
rc_folder = '../crawlers/output/rota-dos-concursos'
rc_files_added = []

flog = "logs/logs_json_to_db.json"
output_logs = []

quest_count = 0
db_name = "tccprod"
regex = '(.*-crawler-)(.*)(-resultados.json)'

db = DatabaseManipulation("mongo")

def _insert_questions_from_file(file, collection_name):
    count_img = 0
    with open(file, "r") as f:
        json_data = json.load(f)
        for quest in json_data["ext_quest_list"]:
            quest["theme"] = json_data["theme"]
            if len(quest["question_imgs"]) > 0:
                count_img += 1
        db.insert_many(db_name, collection_name, json_data["ext_quest_list"])
        output_logs.append({
            "theme": json_data["theme"],
            "file": file.split(".json")[0],
            "total_questions": len(json_data["ext_quest_list"]),
            "questions_with_image": count_img,
            "collection_name": collection_name
        })
        return len(json_data["ext_quest_list"])


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