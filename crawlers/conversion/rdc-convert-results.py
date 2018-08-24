#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import json

fin = "../output/rota-dos-concursos-crawler-ciencia-computacao-resultados-090818.json"
fout = "../output/rota-dos-concursos-crawler-ciencia-computacao-resultados-conv-090818.json"
flog = "logs/rdc-convert-results-rota-dos-concursos-crawler-ciencia-computacao-resultados-conv-090818.json"

rdc_results = []
inner_results = []
output_results = []
output_logs = []

def _fillLogList(logList, theme, subtheme):
    search = [index for index, x in enumerate(logList) if x["theme"] == theme]
    if len(search) == 1:
        if subtheme not in logList[search[0]]["subthemes"]:
            logList[search[0]]["subthemes"].append(subtheme)
    else:
        theme_obj = {}
        theme_obj["theme"] = theme
        theme_obj["subthemes"] = [subtheme]
        logList.append(theme_obj)

    return logList

with open(fin, 'r') as f:
    rdc_results = json.load(f)

inner_results = [rdc_result['result'] for rdc_result in rdc_results]

for result in inner_results:
    if result["main_theme"] != "":
        for nest_result in inner_results:
            if nest_result["theme"] == result["main_theme"]:
                for quest in result["ext_quest_list"]:
                    quest["subthemes"].append(result["theme"])
                nest_result["ext_quest_list"].extend(result["ext_quest_list"])
                output_logs = _fillLogList(output_logs, nest_result["theme"], result["theme"])
                break

output_results = [res for res in inner_results if res["main_theme"] == ""]

with open(fout, 'w') as f:
    json.dump(output_results, f)

with open(flog, 'w') as f:
    json.dump(output_logs, f)


