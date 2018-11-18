#!/usr/bin/env python
# encoding: utf-8

"""Training snippets codes (supervised and unsupervised).

Methods:
    " >>> supervised_training(ml_list, split_test, k_fold, balancing,
                            iter_number, db_type, db_name, db_collection_list,
                            collection_label_list, tokenizer_config,
                            stoptoken_config, output_file_path)
                            
"""

import json

import numpy as np
import training.snippets.nlp_snippets as NLPSP
import training.snippets.misc_snippets as MSCSP
import datetime
import training.snippets.sklearn_training_snippets as SKLTSP
from nltk.corpus import stopwords
from classes.DatabaseManipulation import DatabaseManipulation


def supervised_training(ml_list, split_test, k_fold, balancing,
                        iter_number, db_type, db_name, db_collection_list,
                        collection_label_list, tokenizer_config,
                        stoptoken_config, output_file_path, env):
    """Start supervised training for k_fold and/or split methods.
    Options:
        - ml_list: algorithms options
            ['logistic_regression', 'decision_tree', 'svm_svc_linear',
             'svm_svc_rbf', 'svm_linear_svr ,'multinomial_nb',
             'random-forest', 'kneighbors', 'stochastic-gradient-descent-log',
             'stochastic-gradient-descent-svm']
        - split_test: decimal number percentages (recommended 0.1 to 0.3)
        - k_fold: integer number (recommended 5 or 10)
        - balancing: boolean state to balance sample quantities
        - iter_number: iteration number for training as integer number (e.g. 3)
        - db_type: database used to get the data (e.g. "mongo")
        - db_name: database name to access (e.g. "tcc")
        - db_collection_list: collection name and theme name used in iteration
            [
                { "collec_name": "quest_db_iter_01", "theme_name": "Database" },
                { "collec_name": "quest_rc_iter_01", "theme_name": "Computer Network" }
            ]
        - collection_label_list: collections labels for each theme from db_collection_list
            [0, 1]  # 0: database, 1: computer network (same quantity from db_collection_list)
        - tokenizer_config: types of tokenizer to be used
            ['downcase', 'short', 'porter_stem', 'stopwords']
        - stoptoken_config: types of stoptoken to be used
            ['number', 'key_base_rules']
        - output_file_path: RELATIVE filepath used to output the results (e.g. "reports/training_report_iter_008_")
        - env: database environment ('local', 'preprod', 'prod')

    :param ml_list:
    :param split_test:
    :param k_fold:
    :param balancing:
    :param iter_number:
    :param db_type:
    :param db_name:
    :param db_collection_list:
    :param collection_label_list:
    :param tokenizer_config:
    :param stoptoken_config:
    :param output_file_path:
    :return:
    """
    # Temp variables
    today_date = datetime.datetime.now()

    print "Starting training..."

    # Output variables
    header = "\n--------------------------------------\n"
    header += "REPORT FROM TRAINING - ITERATION " + str(iter_number) + "\n"
    header += "--------------------------------------\n"
    header += "Algorithms used: "
    for ml in ml_list:
        header = header + ml + " "
    header += "\n--------------------------------------\n\n"

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
    db = DatabaseManipulation(db_type, env)
    for collection in db_collection_list:
        theme_question_list_map[collection["collec_name"]] = [MSCSP.bind_question_text_alternatives(q) for q in
                                                              db.find_all(db_name, collection["collec_name"])]
        header = header + collection["theme_name"] + " total questions: " + str(len(
            theme_question_list_map[collection["collec_name"]])) + "\n"

    # Check if quantity needs to be balanced or not
    if balancing:
        # Balance themes
        # Random each theme questions reviews and get same quantity from the theme that has more questions
        smaller_length = len(theme_question_list_map[db_collection_list[0]["collec_name"]])

        for collection in db_collection_list:
            actual_len = len(theme_question_list_map[collection["collec_name"]])
            smaller_length = actual_len if actual_len < smaller_length else smaller_length

        N = smaller_length * len(collection_label_list)
        header = header + "Total questions for each theme after balancing: " + str(smaller_length) + "\n\n"

        for collection in db_collection_list:
            np.random.shuffle(theme_question_list_map[collection["collec_name"]])
            theme_question_list_map[collection["collec_name"]] = \
                theme_question_list_map[collection["collec_name"]][:smaller_length]

        output_file_path = output_file_path + "balanced_"
    else:
        # Unbalanced themes
        # (N x D+1 matrix - keeping themes together so shuffle more easily later
        for collection in db_collection_list:
            N = N + len(theme_question_list_map[collection["collec_name"]])
        output_file_path = output_file_path + "unbalanced_"

    # Iterate questions from each theme, remove extra stoptokens,
    # insert tokens into array and map word index in object
    for collection in db_collection_list:
        tokens = []
        theme_token_list_map[collection["collec_name"]] = []

        for question_text in theme_question_list_map[collection["collec_name"]]:
            tokens = NLPSP.tokenizer(question_text, tokenizer_config, pt_stopwords)

            # Remove extra stoptokens that weren't removed from stopwords
            tokens = [t for t in tokens if not NLPSP.is_stoptoken(t, stoptoken_config)]

            theme_token_list_map[collection["collec_name"]].append(tokens)

            for token in tokens:
                if token not in word_index_map:
                    word_index_map[token] = current_index
                    current_index += 1

    with open("logs/word_index_map_" + today_date.strftime("%d-%m-%Y_%H:%M:%S") + ".json", 'w+') as f:
        json.dump(word_index_map, f)

    # Initialize data matrix with zero frequencies
    data = np.zeros((N, len(word_index_map) + 1))

    i = 0
    col = 0

    # Get themes words frequencies and add to data matrix
    for collection in db_collection_list:
        for tokens in theme_token_list_map[collection["collec_name"]]:
            row = MSCSP.tokens_to_vector(tokens, collection_label_list[col], word_index_map)
            data[i, :] = row
            i += 1
        col += 1

    # Training with report output
    SKLTSP.train_report(data, split_test, k_fold, ml_list, output_file_path, header,
                        collection_label_list)
