# encoding: utf-8

import numpy as np
import codecs
import datetime
import time

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.svm import LinearSVR
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import SGDClassifier

from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import cross_val_score

# Parameters
C = 1.0  # SVM regularization parameter
num_neighbors = 5

def train_report(data, split_test, k_fold, ml_list, filepath, header):
    # Shuffle data and create train/test splits
    np.random.shuffle(data)
    # X as data matrix except true label column; Y as true label column
    X = data[:, :-1]
    Y = data[:, -1]

    # Input data
    Xtrain, Xtest, Ytrain, Ytest = train_test_split(X, Y, test_size=split_test, random_state=0)
    data_dict = {
        'X': X,
        'Y': Y,
        'Xtrain': Xtrain,
        'Xtest': Xtest,
        'Ytrain': Ytrain,
        'Ytest': Ytest
    }
    testing_len = int(round(len(data) * split_test))
    training_len = int(round(len(data) - testing_len))

    final_results = _training_results(data_dict, split_test, k_fold, ml_list)
    _log_results(filepath, header, final_results, split_test, training_len, testing_len)

    
def _training_results(data_dict, split_test, k_fold, list):
    final_results = {
        'training_test': [],
        'cross_validation': []
    }

    for training_type in list:
        result_dict = {
            'name': '',
            'accuracy': None,
            'classification_report': None,
            'confusion_matrix': None
        }

        training_results = []

        if training_type is not None:
            if training_type == 'logistic_regression':
                result_dict['name'] = 'Logistic Regression'
                model = LogisticRegression()

            elif training_type == 'decision_tree':
                result_dict['name'] = 'Decision Tree'
                model = DecisionTreeClassifier()

            elif training_type == 'svm_svc_linear':
                result_dict['name'] = 'SVM SVC Linear'
                model = SVC(kernel='linear', C=C, verbose=True)

            elif training_type == 'svm_svc_rbf':
                result_dict['name'] = 'SVM SVC RBF'
                model = SVC(kernel='rbf', C=C, verbose=True)

            elif training_type == 'svm_linear_svr':
                result_dict['name'] = 'SVM Linear SVR'
                model = LinearSVR(C=C, verbose=True)

            elif training_type == 'multinomial_nb':
                result_dict['name'] = 'Multinomial Naive Bayes'
                model = MultinomialNB()

            elif training_type == 'random-forest':
                result_dict['name'] = 'Random Forest'
                model = KNeighborsClassifier(n_neighbors=num_neighbors)

            elif training_type == 'kneighbors':
                result_dict['name'] = 'KNN'
                model = RandomForestClassifier()

            elif training_type == 'stochastic-gradient-descent-log':
                result_dict['name'] = 'Stochastic Gradient Descent - Logistic Regression'
                model = SGDClassifier(loss='log')

            elif training_type == 'stochastic-gradient-descent-svm':
                result_dict['name'] = 'Stochastic Gradient Descent - Linear SVM'
                model = SGDClassifier(loss='hinge')

            training_results = _process_training(data_dict, result_dict, model, split_test, k_fold)
        else:
            print 'ML not implemented for ' + training_type

        if training_results['training_test'] is not None:
            final_results['training_test'].append(training_results['training_test'])

        elif training_results['cross_validation'] is not None:
            final_results['cross_validation'].append(training_results['cross_validation'])

    return final_results


def _process_training(data_dict, result_dict, model, split_test, k_fold):
    training_results = {
        'training_test': None,
        'cross_validation': None,
        'time': None
    }

    if split_test is not None:
        print "--- Split test training for " + result_dict['name'] + " starting... ---"
        start = time.time()

        model.fit(data_dict['Xtrain'], data_dict['Ytrain'])
        result_dict['accuracy'] = model.score(data_dict['Xtest'], data_dict['Ytest'])

        Ypred = model.predict(data_dict['Xtest'])
        result_dict['classification_report'] = classification_report(data_dict['Ytest'], Ypred)
        result_dict['confusion_matrix'] = confusion_matrix(data_dict['Ytest'], Ypred)

        training_results['training_test'] = result_dict

        end = time.time()
        training_results['time'] = (end - start)
        print "--- Split test training ended for " + result_dict['name'] + " in " + str(training_results['time']) + " ---"
    if k_fold is not None:
        print "--- k-fold test training for " + result_dict['name'] + " starting... ---"
        start = time.time()
        result_dict['accuracy'] = cross_val_score(model, data_dict['X'], data_dict['Y'], cv=k_fold).mean()

        Ypred = cross_val_predict(model, X=data_dict['X'], y=data_dict['Y'], verbose=1, cv=k_fold)
        result_dict['classification_report'] = classification_report(data_dict['Y'], Ypred)
        result_dict['confusion_matrix'] = confusion_matrix(data_dict['Y'], Ypred)

        training_results['cross_validation'] = result_dict

        end = time.time()
        training_results['time'] = (end - start)
        print "--- k-fold test training ended for " + result_dict['name'] + " in " + str(training_results['time']) + " ---"

    return training_results


def _log_results(filepath, header, final_results, split_test, training_len, testing_len):
    # Report output
    sout = header

    if len(final_results['training_test']) > 0:
        sout += "\n--------------------------------------\n"
        sout += "Normal training/test mode\n"
        sout += "--------------------------------------\n"
        sout = sout + "Training mode: " + str(100 - split_test * 100) + "/" + str(split_test * 100) + "\n"
        sout = sout + "Training amount: " + str(training_len) + "\n"
        sout = sout + "Testing amount: " + str(testing_len) + "\n\n"
        sout += "--------------------------------------\n"

        for item_dict in final_results['training_test']:
            sout = sout + "Results for " + item_dict['name'] + " algorithm in normal training/test mode\n"
            sout += "--------------------------------------\n"
            sout = sout + "Main Classification Rate: " + str(item_dict['accuracy']) + "\n"
            sout += "Metrics:\n\n"
            sout += item_dict['classification_report']
            sout += "\n\nConfusion Matrix:\n"
            sout += np.array_str(item_dict['confusion_matrix'])
            # sout = sout + "\n\nTime: " + item_dict['time'] + "\n"
            sout += "\n--------------------------------------\n"

    if len(final_results['cross_validation']) > 0:
        sout += "\n--------------------------------------\n"
        sout += "Cross-validation mode with k-folds\n"
        sout += "--------------------------------------\n"

        for item_dict in final_results['cross_validation']:
            sout = sout + "Results for " + item_dict['name'] + " algorithm in cross-validation mode\n"
            sout += "--------------------------------------\n"
            sout = sout + "Main Classification Rate: " + str(item_dict['accuracy']) + "\n"
            sout += "Metrics:\n\n"
            sout += item_dict['classification_report']
            sout += "\n\nConfusion Matrix:\n"
            sout += np.array_str(item_dict['confusion_matrix'])
            # sout = sout + "\n\nTime: " + item_dict['time'] + "\n"
            sout += "\n--------------------------------------\n"

    fname = filepath + datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ".txt"
    fout = codecs.open(fname, 'w+', 'utf8')
    fout.write(sout)  # Stored on disk as UTF-8
    fout.close()