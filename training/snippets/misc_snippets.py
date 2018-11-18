# encoding: utf-8

"""Misc snippets to manipulate data.

Methods:
    " >>> bind_question_text_alternatives(question)
    " >>> tokens_to_vector(tokens, label, word_index_map)
    " >>> has_numbers(s)

"""

import numpy as np


def bind_question_text_alternatives(question):
    """Bind question text with each alternative in one single string variable.
    :param question:
    :return [string] merged_question_text:
    """
    s = question["question_text"]
    for alternative in question["options"]:
        s = s + " " + alternative["text"]
    return s


def tokens_to_vector(tokens, label, word_index_map):
    """Convert each set of tokens into a frequency vector.
    :param tokens:
    :param label:
    :param word_index_map:
    :return [array] row_vec:
    """

    # setting bag of words frequency then increase last column for true label
    row_vec = np.zeros(len(word_index_map) + 1)
    for t in tokens:
        i = word_index_map[t]
        row_vec[i] += 1

    if row_vec.sum() > 0:
        # normalize it before setting true label
        row_vec = row_vec / row_vec.sum()
    row_vec[-1] = label

    # index = 0
    # for w_vec_qty in row_vec:
    #     if np.isnan(w_vec_qty):
    #         print(index, w_vec_qty)
    #     index += 1

    return row_vec


def has_numbers(s):
    """Check if string has numbers.
    :param s:
    :return [boolean] true or false:
    """
    return any(c.isdigit() for c in s)

