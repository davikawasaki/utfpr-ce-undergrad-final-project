# encoding: utf-8

"""NLP snippets to process data for machine learning trainings.

Methods:
    " >>> tokenizer(s, config, stopwords)
    " >>> is_stoptoken(s, config)
    " >>> _unnaccent(s)
    " >>> _rule_base_processing(s, rule)

"""

import nltk
import json
import re
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from training.snippets import misc_snippets as MSC
import unidecode


def tokenizer(s, config, stopwords):
    """Get string and convert its words into tokens.

    Options:
        - config: [downcase, unaccent, short, misspelings, lemmatize, porter_stem, stopwords]
        - stopwords: list of combined stopwords in string file

    :param s:
    :param config:
    :param stopwords:
    :return [array] tokens:
    """

    if 'downcase' in config:
        s = s.lower()  # downcase

    if 'unaccent' in config:
        s = _unnaccent(s)  # unaccent

    tokens = nltk.tokenize.word_tokenize(s)  # split string into words (tokens)

    if 'short' in config:
        tokens = [t for t in tokens if len(t) > 2]  # remove short words

    # if 'misspelings' in config:
        # todo: misspellings

    if 'lemmatize' in config:
        wordnet_lemmatizer = WordNetLemmatizer()
        tokens = [wordnet_lemmatizer.lemmatize(t) for t in tokens]  # putting words in base form

    if 'stopwords' in config:
        tokens = [t for t in tokens if t not in stopwords]  # remove stopwords

    if 'porter_stem' in config:
        porter_stemmer = PorterStemmer()
        tokens = [porter_stemmer.stem(t) for t in tokens]

    return tokens


def is_stoptoken(s, config):
    """Check if string is a stoptoken according to config rules.
    Config rules work for unicode, lots of digits, remove ', technical related keys rules (i.e IP addresses)
    Options:
        - config: ['number', 'inner_digits', 'key_base_rules']
    
    :param s:
    :param config:
    :return [boolean] True or False:
    """

    status = False

    if 'number' in config:
        status = s.isdigit()  # number

    if status is False and 'inner_digits' in config:
        status = MSC.has_numbers(s)

    if status is False and 'key_base_rules' in config:
        with open("../rules/rule_based_key_pair.json", 'r') as f:
            rules_themes = json.load(f)
            for theme in rules_themes:
                for rule in theme['rules']:
                    rule_status = _rule_base_processing(s, rule)
                    status = rule_status["status"]

    return status


def _unnaccent(s):
    """Unnaccent string with unidecode.
    
    :param s:
    :return [string] string_noaccent:
    """
    return unidecode.unidecode(s)


def _rule_base_processing(s, rule):
    """Process rule base in string.
    Options:
        - rule types: "regex", "string"
            - e.g. {"name": "networkaddress", "type": "regex",
                    "pattern": "^([0-9]{1,3}).([0-9]{1,3}).([0-9]{1,3}).([0-9]{1,3})$",
                    "valueType": "string", "value": "NETWORK_ADDRESS"}
    @ref rules/rule_based_key_pair.json
    :param s:
    :param rule:
    :return [object] status and value, which status says if string passed in the rule base:
    """
    if rule["type"] == "regex":
        pattern = re.compile(rule["pattern"])
        s_pattern_match = pattern.match(s)
        if s_pattern_match:
            if rule["valueType"] == "string":
                return {"status": True, "value": rule["value"]}
            elif rule["valueType"] == "regex":
                # value needs to follow this pattern: $1\.+$2, where $\d corresponds to the group you want to get
                groups = pattern.findall(rule["value"])
                if len(groups) > 0:
                    for group in groups:
                        group_num = group.replace("$", "")
                        # i.e 192.168.1.1             to 192[.]168[.]1[.]1[.]
                        #     gr(0).gr(1).gr(2).gr(3) to $1[.]$2[.]$3[.]$4[.]
                        rule["value"].replace(group, s_pattern_match.group(group_num - 1))
                    return {"status": True, "value": rule["value"]}
                else:
                    return {"status": False, "value": "Pattern not found with findall!"}
            else:
                return {"status": False, "value": "Value type of regex type not implemented yet!"}
        else:
            return {"status": False, "value": "Pattern not found in rule base regex type!"}
    elif rule["type"] == "string":
        if rule["valueType"] == "string":
            return {"status": True, "value": rule["value"]}
        else:
            return {"status": False, "value": "Rule base value type not implemented yet!"}
    else:
        return {"status": False, "value": "Rule base not implemented yet!"}
