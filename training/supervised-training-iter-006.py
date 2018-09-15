#!/usr/bin/env python
# encoding: utf-8
# Second training with computer arquitecture, information systems and operational system questions
## AC Total: 1062 questions
## SI Total: 3081 questions
## SO Total: 2483 questions

import json

import numpy as np
import training.nlp_snippets as NLPSP
import training.misc_snippets as MSCSP
import datetime

import sklearn_training

from nltk.corpus import stopwords
from classes.DatabaseManipulation import DatabaseManipulation

# Temp variables
smaller_length = 0
today_date = datetime.datetime.now()
kfold = 10
# ml_list = ['logistic_regression', 'decision_tree', 'svm_svc_linear', 'svm_svc_rbf', 'svm_linear_svr ,'multinomial_nb', 'random-forest', 'kneighbors', 'stochastic-gradient-descent-log', 'stochastic-gradient-descent-svm']
ml_list = ['logistic_regression', 'decision_tree', 'svm_svc_linear', 'multinomial_nb', 'random-forest', 'stochastic-gradient-descent-log', 'stochastic-gradient-descent-svm']

print "Starting training..."

# Output variables
filepath = "reports/training_report_iter_006_"
header = "\n--------------------------------------\n"
header += "REPORT FROM TRAINING - ITERATION 006\n"
header += "--------------------------------------\n"
header += "Algorithms used: "
for ml in ml_list:
    header = header + ml + " "
header += "\n--------------------------------------\n\n"

# Variables
db_name = "tcc"
db_collection_list = ["quest_ac_iter_02", "quest_si_iter_02", "quest_so_iter_02"]
collection_label_list = [0, 1, 2]  # 0: ac, 1: si, 2: so
tokenizer_config = ['downcase', 'short', 'porter_stem', 'stopwords']
stoptoken_config = ['number', 'key_base_rules']
split_testing_percentage = 0.2

# Setting base for matrix X with index dictionary and token arrays
word_index_map = {}
theme_question_list_map = {}
theme_token_list_map = {}
current_index = 0
N = 0

# Setting stopwords from list to reduce processing time and dimensionality
pt_stopwords = stopwords.words('portuguese')
pt_stopwords += [w.rstrip() for w in open('stopwords.txt')]

# Load themes questions from mongo db into dict arrays
db = DatabaseManipulation("mongo")
for collection in db_collection_list:
    theme_question_list_map[collection] = [MSCSP.bind_question_text_alternatives(q) for q in db.find_all(db_name, collection)]

header = header + "Computer Architecture total questions: " + str(len(theme_question_list_map[db_collection_list[0]])) + "\n"
header = header + "Information Systems total questions: " + str(len(theme_question_list_map[db_collection_list[1]])) + "\n"
header = header + "Operational System total questions: " + str(len(theme_question_list_map[db_collection_list[2]])) + "\n"

# Unbalanced themes
# (N x D+1 matrix - keeping themes together so shuffle more easily later
for collection in db_collection_list:
    N = N + len(theme_question_list_map[collection])

# Balance themes
# Random each theme questions reviews and get same quantity from the theme that has more questions
# smaller_length = len(theme_question_list_map[db_collection_list[0]])
#
# for collection in db_collection_list:
#     actual_len = len(theme_question_list_map[collection])
#     smaller_length = actual_len if actual_len < smaller_length else smaller_length
#
# N = smaller_length * len(collection_label_list)
# header = header + "Total questions for each theme after balancing: " + str(smaller_length) + "\n\n"
#
# for collection in db_collection_list:
#     np.random.shuffle(theme_question_list_map[collection])
#     theme_question_list_map[collection] = theme_question_list_map[collection][:smaller_length]

# Iterate questions from each theme, remove extra stoptokens, insert tokens into array and map word index in object
for collection in db_collection_list:
    tokens = []
    theme_token_list_map[collection] = []

    for question_text in theme_question_list_map[collection]:
        tokens = NLPSP.tokenizer(question_text, tokenizer_config, pt_stopwords)

        # Remove extra stoptokens that weren't removed from stopwords
        tokens = [t for t in tokens if not NLPSP.is_stoptoken(t, stoptoken_config)]

        theme_token_list_map[collection].append(tokens)

        for token in tokens:
            if token not in word_index_map:
                word_index_map[token] = current_index
                current_index += 1

with open("logs/word_index_map_" + today_date.strftime("%d-%m-%Y %H:%M:%S") + ".json", 'w+') as f:
    json.dump(word_index_map, f)

# Initialize data matrix with zero frequencies
data = np.zeros((N, len(word_index_map) + 1))

i = 0
col = 0

# Get themes words frequencies and add to data matrix
for collection in db_collection_list:
    for tokens in theme_token_list_map[collection]:
        row = MSCSP.tokens_to_vector(tokens, collection_label_list[col], word_index_map)
        data[i, :] = row
        i += 1
    col += 1

# Training with report output
sklearn_training.train_report(data, split_testing_percentage, kfold, ml_list, filepath, header)
