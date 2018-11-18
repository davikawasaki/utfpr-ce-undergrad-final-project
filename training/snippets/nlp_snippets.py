# encoding: utf-8

import nltk
import json
import re
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from training import misc_snippets as MSC
import unidecode

# config: [downcase, unaccent, short, misspelings, lemmatize, porter_stem, stopwords]
def tokenizer(s, config, stopwords):
    if 'downcase' in config:
        s = s.lower()  # downcase

    if 'unaccent' in config:
        s = _unnacent(s)  # unaccent

    tokens = nltk.tokenize.word_tokenize(s)  # split string into words (tokens)

    if 'short' in config:
        tokens = [t for t in tokens if len(t) > 2]  # remove short words

    #if 'misspelings' in config:
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

# do config for unicode, lots of digits, remove ', technical related keys rules (i.e IP addresses)
# config: [number, inner_digits, key_base_rules]
def is_stoptoken(s, config):
    status = False

    if 'number' in config:
        status = s.isdigit()  # number

    if status is False and 'inner_digits' in config:
        status = MSC.hasNumbers(s)

    if status is False and 'key_base_rules' in config:
        with open("../rules/rule_based_key_pair.json", 'r') as f:
            rules_themes = json.load(f)
            for theme in rules_themes:
                for rule in theme['rules']:
                    rule_status = _rule_base_processing(s, rule)
                    status = rule_status["status"]

    return status

def _unnacent(s):
    return unidecode.unidecode(s)

def _rule_base_processing(s, rule):
    if rule["type"] == "regex":
        pattern = re.compile(rule["pattern"])
        s_pattern_match = pattern.match(s)
        if s_pattern_match:
            if rule["valueType"] == "string":
                return { "status": True, "value": rule["value"] }
            elif rule["valueType"] == "regex":
                # value needs to follow this pattern: $1\.+$2, where $\d corresponds to the group you want to get
                groups = pattern.findall(rule["value"])
                if len(groups) > 0:
                    for group in groups:
                        group_num = group.replace("$", "")
                        # i.e 192.168.1.1             to 192[.]168[.]1[.]1[.]
                        #     gr(0).gr(1).gr(2).gr(3) to $1[.]$2[.]$3[.]$4[.]
                        rule["value"].replace(group, s_pattern_match.group(group_num - 1))
                    return { "status": True, "value": rule["value"] }
                else:
                    return { "status": False, "value": "Pattern not found with findall!" }
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