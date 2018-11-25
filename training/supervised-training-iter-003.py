#!/usr/bin/env python
# encoding: utf-8

"""Supervised training for iteration 3.

Themes: Database, Computer Network, Computer Architecture, Information Systems and Operational Systems
Total of questions: 4449 (Database),
                    5483 (Computer Network),
                    1062 (Computer Architecture),
                    3081 (Information Systems),
                    2483 (Operational Systems)

"""

import training.snippets.training_snippets as TRNSP

##
# 1. CONFIG VARIABLES
##
ml_list = ['logistic_regression', 'decision_tree', 'svm_svc_linear', 'multinomial_nb',
           'random-forest', 'stochastic-gradient-descent-log', 'stochastic-gradient-descent-svm']
split_test = 0.2
k_fold = 10
balancing = True
iter_number = 1
db_type = "mongo"
db_name = "tcc"
db_env = "local"
db_collection_list = [{"collec_name": "quest_db_iter_01", "theme_name": "Database"},
                      {"collec_name": "quest_rc_iter_01", "theme_name": "Computer Network"},
                      {"collec_name": "quest_ac_iter_02", "theme_name": "Computer Architecture"},
                      {"collec_name": "quest_si_iter_02", "theme_name": "Information Systems"},
                      {"collec_name": "quest_so_iter_02", "theme_name": "Operational Systems"}]
collection_label_list = [0, 1, 2, 3, 4]  # 0: db, 1: rc, 2: ac, 3: si, 4: so
tokenizer_config = ['downcase', 'short', 'porter_stem', 'stopwords']
stoptoken_config = ['number', 'key_base_rules']
output_file_path = "reports/training_report_iter_003_"


##
# 2. START SUPERVISED TRAINING
##
TRNSP.supervised_training(ml_list, split_test, k_fold, balancing,
                          iter_number, db_type, db_name, db_collection_list,
                          collection_label_list, tokenizer_config,
                          stoptoken_config, output_file_path, db_env)
