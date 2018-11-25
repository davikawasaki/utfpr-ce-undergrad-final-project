# encoding: utf-8

"""Sklearn snippets for machine learning trainings.

Methods:
    " >>> train_report(data, split_test, k_fold, ml_list, file_path, header, classes)
    " >>> _training_results(data_dict, split_test, k_fold, list)
    " >>> _process_training(data_dict, result_dict, model, split_test, k_fold)
    " >>> _log_results(file_path, header, final_results, split_test, training_len, testing_len)

"""

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

# Default parameters for: SVM and KNN
C = 1.0  # SVM regularization parameter
num_neighbors = 5


def train_report(data, split_test, k_fold, ml_list, file_path, header, classes):
    """Execute supervised training for list of algorithms and report the output.
    Options:
        - split_test: decimal number percentages (recommended 0.1 to 0.3)
        - k_fold: integer number (recommended 5 or 10)
        - ml_list: algorithms options
            ['logistic_regression', 'decision_tree', 'svm_svc_linear',
             'svm_svc_rbf', 'svm_linear_svr ,'multinomial_nb',
             'random-forest', 'kneighbors', 'stochastic-gradient-descent-log',
             'stochastic-gradient-descent-svm']
        - collection_label_list: collections labels for each theme from db_collection_list
            [0, 1]  # 0: database, 1: computer network (same quantity from db_collection_list)

    :param data:
    :param split_test:
    :param k_fold:
    :param ml_list:
    :param file_path:
    :param header:
    :param classes:
    :return:
    """

    # Shuffle data and create train/test splits
    np.random.shuffle(data)

    # X as data matrix except true label column; Y as true label column
    X = data[:, :-1]
    Y = data[:, -1]

    # Get length for testing and training
    if split_test is None:
        testing_len = 0
        training_len = 0
    else:
        testing_len = int(round(len(data) * split_test))
        training_len = int(round(len(data) - testing_len))

    # Input data
    Xtrain, Xtest, Ytrain, Ytest = train_test_split(X, Y, test_size=split_test, random_state=0)
    data_dict = {
        'X': X,
        'Y': Y,
        'Xtrain': Xtrain,
        'Xtest': Xtest,
        'Ytrain': Ytrain,
        'Ytest': Ytest,
        'data': data,
        'classes': classes,
        'training_len': training_len,
        'testing_len': testing_len
    }

    # Execute training and get results
    final_results = _training_results(data_dict, split_test, k_fold, ml_list)

    # Output the results in log JSON files
    _log_results(file_path, header, final_results, split_test, training_len, testing_len)

    
def _training_results(data_dict, split_test, k_fold, training_type_list):
    """Execute supervised training for each training algorithm type.
    Options:
        - split_test: decimal number percentages (recommended 0.1 to 0.3)
        - k_fold: integer number (recommended 5 or 10)
        - training_type_list: algorithms options
            ['logistic_regression', 'decision_tree', 'svm_svc_linear',
             'svm_svc_rbf', 'svm_linear_svr ,'multinomial_nb',
             'random-forest', 'kneighbors', 'stochastic-gradient-descent-log',
             'stochastic-gradient-descent-svm']
        - [OUTPUT] final_results: e.g.
            - {'training_test': [{'name': 'Logistic Regression', 'accuracy': 0.9531331',
                                  'classification_report': '
                                       precision    recall  f1-score   support

                                        0.0       0.95      0.95      0.95      4449
                                        1.0       0.95      0.95      0.95      4449

                                  avg / total       0.95      0.95      0.95      8898',
                                  'confusion_matrix': '
                                        [[4233  216]
                                        [ 229 4220]]'
                                  }],
              {'cross_validation': [{'name': 'Logistic Regression', 'accuracy': 0.9531331', ...}]}

    :param data_dict:
    :param split_test:
    :param k_fold:
    :param training_type_list:
    :return [object] final results for each methodology:
    """
    final_results = {
        'training_test': [],
        'cross_validation': []
    }

    for training_type in training_type_list:
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
                model = RandomForestClassifier()

            elif training_type == 'kneighbors':
                result_dict['name'] = 'KNN'
                model = KNeighborsClassifier(n_neighbors=num_neighbors)

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
    """Execute training with Sklearn and return the results.
    Options:
        - result_dict: object to store the output results
            {'name': 'Logistic Regression', 'accuracy': None, 'classification_report': None, 'confusion_matrix': None}
        - model: sklearn object with specific supervised training bootstraped model
        - split_test: decimal number percentages (recommended 0.1 to 0.3)
        - k_fold: integer number (recommended 5 or 10)

    :param data_dict:
    :param result_dict:
    :param model:
    :param split_test:
    :param k_fold:
    :return [object] final_results
        e.g. {'training_test': result_dict, 'cross_validation': result_dict, 'time': 130103}:
    """

    training_results = {
        'training_test': None,
        'cross_validation': None,
        'time': None
    }

    # Random forest algorithm has a different type of data argument
    if result_dict['name'] == 'random-forest':
        X = data_dict['data']
        Y = data_dict['classes']
        Xtrain = X[:-data_dict['testing_len'], ]
        Ytrain = Y[:-data_dict['testing_len'], ]
        Xtest = X[-data_dict['testing_len']:, ]
        Ytest = Y[-data_dict['testing_len']:, ]
    else:
        X = data_dict['X']
        Y = data_dict['Y']
        Xtrain = data_dict['Xtrain']
        Ytrain = data_dict['Ytrain']
        Xtest = data_dict['Xtest']
        Ytest = data_dict['Ytest']

    if split_test is not None:
        print "--- Split test training for " + result_dict['name'] + " starting... ---"
        start = time.time()

        model.fit(Xtrain, Ytrain)
        result_dict['accuracy'] = model.score(Xtest, Ytest)

        Ypred = model.predict(Xtest)
        result_dict['classification_report'] = classification_report(Ytest, Ypred)
        result_dict['confusion_matrix'] = confusion_matrix(Ytest, Ypred)

        end = time.time()
        result_dict['time'] = (end - start)
        training_results['training_test'] = result_dict

        print "--- Split test training ended for " + result_dict['name'] + " in " + str(result_dict['time']) + " ---"
    if k_fold is not None:
        print "--- k-fold test training for " + result_dict['name'] + " starting... ---"
        start = time.time()
        result_dict['accuracy'] = cross_val_score(model, X, Y, cv=k_fold).mean()

        Ypred = cross_val_predict(model, X=X, y=Y, verbose=1, cv=k_fold)
        result_dict['classification_report'] = classification_report(Y, Ypred)
        result_dict['confusion_matrix'] = confusion_matrix(Y, Ypred)

        end = time.time()
        result_dict['time'] = (end - start)
        training_results['cross_validation'] = result_dict

        print "--- k-fold test training ended for " + result_dict['name'] + " in " + str(result_dict['time']) + " ---"

    return training_results


def _log_results(file_path, header, final_results, split_test, training_len, testing_len):
    """Output the training results in a file path log JSON file.

    @ref reports/*.json
    :param file_path:
    :param header:
    :param final_results:
    :param split_test:
    :param training_len:
    :param testing_len:
    :return:
    """

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
            sout = sout + "\n\nTime: " + str(item_dict['time']) + "\n"
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
            sout = sout + "\n\nTime: " + str(item_dict['time']) + "\n"
            sout += "\n--------------------------------------\n"

    fname = file_path + datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S") + ".txt"
    fout = codecs.open(fname, 'w+', 'utf8')
    fout.write(sout)  # Stored on disk as UTF-8
    fout.close()
