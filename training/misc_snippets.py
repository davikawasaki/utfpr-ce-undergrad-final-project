# encoding: utf-8

import numpy as np

# Bind question text with alternatives text
def bind_question_text_alternatives(question):
    s = question["question_text"]
    for alternative in question["options"]:
        s = s + " " + alternative["text"]
    return s

# Convert each set of tokens into a data vector
def tokens_to_vector(tokens, label, word_index_map):
    row_vec = np.zeros(len(word_index_map) + 1)  # setting bag of words frequency then increase last column for true label
    for t in tokens:
        i = word_index_map[t]
        row_vec[i] += 1

    if row_vec.sum() > 0:
        row_vec = row_vec / row_vec.sum()  # normalize it before setting true label
    row_vec[-1] = label

    # index = 0
    # for w_vec_qty in row_vec:
    #     if np.isnan(w_vec_qty):
    #         print(index, w_vec_qty)
    #     index += 1

    return row_vec

def hasNumbers(s):
    return any(c.isdigit() for c in s)