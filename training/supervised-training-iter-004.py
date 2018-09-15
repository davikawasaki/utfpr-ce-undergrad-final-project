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

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix

import codecs
from numpy import array_str

from nltk.corpus import stopwords
from classes.DatabaseManipulation import DatabaseManipulation

# Temp variables
smaller_length = 0
today_date = datetime.datetime.now()

# Output variables
sout = "REPORT FROM TRAINING - ITERATION 004\n------------------\n\n"

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

sout = sout + "Computer Architecture total questions: " + str(len(theme_question_list_map[db_collection_list[0]])) + "\n"
sout = sout + "Information Systems total questions: " + str(len(theme_question_list_map[db_collection_list[1]])) + "\n"
sout = sout + "Operational System total questions: " + str(len(theme_question_list_map[db_collection_list[2]])) + "\n"

# Balance themes
# Random each theme questions reviews and get same quantity from the theme that has more questions
smaller_length = len(theme_question_list_map[db_collection_list[0]])

for collection in db_collection_list:
    actual_len = len(theme_question_list_map[collection])
    # (N x D+1 matrix - keeping themes together so shuffle more easily later
    N = N + actual_len

    smaller_length = actual_len if actual_len < smaller_length else smaller_length

sout = sout + "Total questions for each theme after balancing: " + str(smaller_length) + "\n\n"

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

testing_len = int(round(len(data) * split_testing_percentage))
training_len = int(round(len(data) - testing_len))

sout = sout + "Training mode: " + str(100 - split_testing_percentage * 100) + "/" + str(split_testing_percentage * 100) + "\n"
sout = sout + "Training amount: " + str(training_len) + "\n"
sout = sout + "Testing amount: " + str(testing_len) + "\n\n"

print testing_len
print training_len
print testing_len + training_len

# Shuffle data and create train/test splits
np.random.shuffle(data)
# X as data matrix except true label column; Y as true label column
X = data[:, :-1]
Y = data[:, -1]

# Last split testing (20%) rows will be used as test
Xtrain = X[:-testing_len, ]
Ytrain = Y[:-testing_len, ]
Xtest = X[-testing_len:, ]
Ytest = Y[-testing_len:, ]

# Classifying with LogisticRegression
model = LogisticRegression()
model.fit(Xtrain, Ytrain)
modelLRscore = model.score(Xtest, Ytest)

print "Logistic Regression Classification rate: ", modelLRscore
sout += "--------------------------------------\n"
sout = sout + "Logistic Regression Main Classification Rate: " + str(modelLRscore) + "\n"

Ypred = model.predict(Xtest)
classificationReportLR = classification_report(Ytest, Ypred)
confusionMatrixLR = confusion_matrix(Ytest, Ypred)

print "Metrics for LR"
print classificationReportLR
print confusionMatrixLR

sout += "Logistic Regression Metrics\n"
sout = sout + classificationReportLR + "\n"
sout = sout + "Confusion Matrix: \n" + array_str(confusionMatrixLR) + "\n\n"

# Classifying with DecisionTreeClassifier
modelTree = DecisionTreeClassifier()
modelTree.fit(Xtrain, Ytrain)
modelDecisionTreeScore = modelTree.score(Xtest, Ytest)

# print "Decision Tree Classification rate: ", modelDecisionTreeScore
sout += "--------------------------------------\n"
sout = sout + "Decision Tree Main Classification Rate: " + str(modelDecisionTreeScore) + "\n"

Ypred = modelTree.predict(Xtest)
classificationReportDecisionTree = classification_report(Ytest, Ypred)
confusionMatrixDecisionTree = confusion_matrix(Ytest, Ypred)

print "Metrics for DT"
print classificationReportDecisionTree
print confusionMatrixDecisionTree

sout += "Decision Tree Metrics\n\n"
sout = sout + classificationReportDecisionTree + "\n"
sout = sout + "Confusion Matrix: \n" + array_str(confusionMatrixDecisionTree)
sout += "\n--------------------------------------"

fname = "reports/training_report_iter_004_" + today_date.strftime("%d-%m-%Y %H:%M:%S") + ".txt"
fout = codecs.open(fname, 'w+', 'utf8')
fout.write(sout)  # Stored on disk as UTF-8
fout.close()