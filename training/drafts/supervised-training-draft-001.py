#!/usr/bin/env python
# encoding: utf-8
# First training with database and network questions
## BD Total: 4449 questions
## RC Total: 5483 questions

import json

import numpy as np
import training.snippets.nlp_snippets as NLPSP
import training.snippets.misc_snippets as MSCSP
import datetime

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

from nltk.corpus import stopwords
from classes.DatabaseManipulation import DatabaseManipulation

# Temp variables
smaller_length = 0
today_date = datetime.datetime.now()

# Variables
db_name = "tcc"
db_collection_list = ["quest_db_iter_01", "quest_rc_iter_01"]
collection_label_list = [0, 1]  # 0: db, 1: rc
tokenizer_config = ['downcase', 'short', 'porter_stem', 'stopwords']
stoptoken_config = ['number', 'key_base_rules']
split_test = 0.2

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

# Balance themes
# Random each theme questions reviews and get same quantity from the theme that has more questions
smaller_length = len(theme_question_list_map[db_collection_list[0]])

for collection in db_collection_list:
    actual_len = len(theme_question_list_map[collection])
    # (N x D+1 matrix - keeping themes together so shuffle more easily later
    N = N + actual_len

    smaller_length = actual_len if actual_len < smaller_length else smaller_length

for collection in db_collection_list:
    np.random.shuffle(theme_question_list_map[collection])
    theme_question_list_map[collection] = theme_question_list_map[collection][:smaller_length]

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

testing_len = int(round(len(data) * split_test))
training_len = int(round(len(data) - testing_len))

print testing_len
print training_len
print testing_len + training_len

# Shuffle data and create train/test splits
np.random.shuffle(data)
# X as data matrix except true label column; Y as true label column
X = data[:, :-1]
Y = data[:, -1]

# print(X[:,0].shape)
# index = 0
# for i in X[:,0]:
#     if not np.isfinite(i):
#         print(index, i)
#     index +=1

# Last split testing (20%) rows will be used as test
Xtrain = X[:-testing_len, ]
Ytrain = Y[:-testing_len, ]
Xtest = X[-testing_len:, ]
Ytest = Y[-testing_len:, ]

# Classifying with LogisticRegression
model = LogisticRegression()
model.fit(Xtrain, Ytrain)
print "Logistic Regression Classification rate: ", model.score(Xtest, Ytest)

# Classifying with DecisionTreeClassifier
modelTree = DecisionTreeClassifier()
modelTree.fit(Xtrain, Ytrain)
print "Decision Tree Classification rate: ", modelTree.score(Xtest, Ytest)