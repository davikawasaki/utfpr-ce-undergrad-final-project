#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""Crawler to extract IT questions from Questao Certa website.

Project: questao_certa_it_questions
Framework used: Selenium

todo: accept Auth and URL JSON config file
outputs: compiled JSON to output folder

"""

import re
import json
import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# DON'T FORGET TO CHANGE YOUR CREDENTIALS IN HERE
auth = {
    'email': '<INSERT YOUR EMAIL>',
    'password': '<INSERT YOUR PASSWORD>'
}

# IF YOUR CHROME DRIVER IS IN A DIFFERENT FOLDER, CHANGE HERE
chrome_driver_path = "/usr/bin/chromedriver"

url = 'https://www.questaocerta.com.br/'
url_disciplina = url + 'questoes/disciplina/'
url_login = url + 'login/'
url_questions = url + 'questoes/'

error_list = []
error_count = 0

options = webdriver.ChromeOptions()
# options.add_argument('--ignore-certificate-errors')
# options.add_argument("--test-type")
# options.binary_location = chrome_driver_path
# options.add_argument("headless")
driver = webdriver.Chrome(executable_path=chrome_driver_path, chrome_options=options)

# driver = webdriver.Chrome(executable_path=chrome_driver_path)
# driver = webdriver.PhantomJS()

##
# 1. LOGIN PAGE
##
print '--- Starting extraction... ---'
driver.get(url_login)

print '--- Logging in... ---'
driver.find_element_by_id('usuarioLogin').send_keys(auth['email'])
driver.find_element_by_id('senhaLogin').send_keys(auth['password'], Keys.ENTER)

driver.get(url_questions)

##
# 2. GET SUBJECT ELEMENTS
##
disciplina_select = driver.find_element_by_id('filtro_disciplina')
disciplina_list = disciplina_select.find_elements_by_tag_name("option")
disciplina_ti_url_list = []

##
# 3. EXTRACT THEMES
##
print '--- Themes extraction... ---'
for disciplina in disciplina_list:
    if disciplina.text != "Disciplina":
        if disciplina.get_attribute('value') is not None:
            if '(ti)' in disciplina.get_attribute('value'):
                print '--- Theme: ' + disciplina.get_attribute('value') + '---'
                disciplina_ti_url_list.append(url_disciplina + disciplina.get_attribute('value'))

##
# 4. SKIP PAGES
# Maneuver to skip pages if necessary. If not, just let it be 0.
##
skip = 0
# skip = 9 # Engenharia de Software (TI) - page 216 (error)

##
# 5. START EXTRACTION CHECKING URL REGEX FOR TI THEME PAGES
##
for theme_url in disciplina_ti_url_list:
    if skip > 0:
        skip -= 1
        continue
    count = 0
    # theme_url = disciplina_ti_url_list[0]

    theme_name = ''
    try:
        theme_name = re.search('(.+)(disciplina\/)(.+)(-\(ti\))', theme_url).group(3).replace('-', ' ')
    except Exception as e:
        error_count += 1
        error_list.append({
            'error_id': 'THEME_NAME',
            'error_count': 'ERR' + str(error_count),
            'error_ref': theme_url,
            'error_detail': traceback.format_exc()
        })
        print '[ERROR] Erro adicionado a lista de erros! Tema vazio!'

    print '--- Extracting questions from theme ' + theme_name + ' ---'
    extraction = {
        'theme': theme_name,
        'ext_quest_list': []
    }

    driver.get(theme_url)

    page_el = driver.find_element_by_xpath("/html/body/div[@class='wrapper']/section[@class='middle']/div[@class='container']/div[@class='middle-content clearfix']/section[@class='questoes']/div[@class='paginacao']")
    last_span_el = page_el.find_elements_by_tag_name("span")[-1]
    span_a_el = last_span_el.find_element_by_tag_name("a")
    total_pages = re.search('(.+)(-\(ti\)\/)(\d+)', span_a_el.get_attribute('href')).group(3)

    total_pages_per_iter = 10
    total_pages_rest = int(total_pages) % total_pages_per_iter
    extraction_iterations = int(total_pages)/total_pages_per_iter

    # initial range
    # start = 0
    # end = total_pages_per_iter
    #
    # if total_pages_rest > 0:
    #     extraction_iterations += 1
    #
    # if extraction_iterations == 1:
    #     total_pages_per_iter = total_pages_rest
    #     end = total_pages_rest
    #
    # # divide extraction to each 10 pages (not exceed memory)
    # for i in range(extraction_iterations):
    #
    #     # clear extraction list for each batch
    #     extraction['ext_quest_list'] = []

    ##
    # 5.1. LOOP THROUGH EACH PAGE FROM THEME
    ##
    for j in range(int(total_pages)):
        # for j in range(start, end):
        print '--- Page ' + str(j) + ' ---'
        driver.get(theme_url + '/' + str(j))
        more_details_questions = driver.find_elements_by_class_name('ver-texto-associado')
        for link in more_details_questions:
            link.click()

        ##
        # 5.1.1. ANSWER QUESTIONS TO GET THE RIGHT ANSWERS
        ##
        driver.execute_script("for(var list=document.querySelectorAll(\"input[type='radio']\"),i=0;i<list.length;i++)"
                              "list[i].click();list=document.querySelectorAll(\"a[title='Responder']\");"
                              "for(i=0;i<list.length;i++)list[i].click();")
        time.sleep(1)

        ##
        # 5.1.2. LOOP THROUGH EACH QUESTION
        ##
        question_list = driver.find_elements_by_xpath("//article[@class='questao']")
        for question_count in range(len(question_list)):
            ext_quest = {
                "options": [],
                "question_text": '',
                'question_imgs': [],
                'subthemes': []
            }

            ##
            # 5.1.2.1. GET HEADER TEST NAME AND SUBTHEMES
            ##
            header_text = question_list[question_count].find_element_by_xpath(".//header/div[@class='questao-id']").text

            test_name = ''
            try:
                test_name = re.search('(Prova:\s)([\S+\-\s0-9]+)(Disciplina:)', header_text)
                if test_name is None:
                    test_name = re.search('(Provas .+:\s)([\S+\-\s0-9]+)(Disciplina:)', header_text)
                    ext_quest['test_name'] = test_name.group(2)
            except Exception as e:
                error_count += 1
                error_list.append({
                    'error_id': 'TEST_NAME',
                    'error_count': 'ERR' + str(error_count),
                    'error_ref': header_text,
                    'error_detail': traceback.format_exc()
                })
                print '[ERROR] Erro adicionado a lista de erros! Ignorando a questão...'
                continue

            subthemes = ''
            try:
                subthemes = re.search('(Assunto: )(.+)', header_text).group(2).replace(" ,", ",").replace(", ", ",").split(",")
                ext_quest['subthemes'] = [theme for theme in subthemes]
            except Exception as e:
                error_count += 1
                error_list.append({
                    'error_id': 'SUB_THEMES_NAME',
                    'error_count': 'ERR' + str(error_count),
                    'error_ref': header_text,
                    'error_detail': traceback.format_exc()
                })
                print '[ERROR] Erro adicionado a lista de erros! Ignorando a questão...'
                continue

            ##
            # 5.1.2.2. GET QUESTION BODY
            ##
            question_middle = question_list[question_count].find_element_by_xpath(".//div[@class='questao-miolo']")

            ##
            # 5.1.2.3. CHECK QUESTIONS TO GET CORRECT ANSWER
            ##
            alternatives_question = question_middle.find_element_by_xpath(".//div[@class='questao-alternativas']")
            # alternatives_question.find_element_by_xpath(".//ul/li[1]/div[@class='radio']/span/input").click()
            # alternatives_question.find_element_by_xpath(".//a").click()

            green_alert = alternatives_question.find_element_by_xpath(".//div[@class='alerta-verde']")
            red_alert = alternatives_question.find_element_by_xpath(".//div[@class='alerta-vermelho']")

            # assert green_alert.get_attribute("style") == "display: none;" and + \
            #     red_alert.get_attribute("style") == "display: none;"

            ##
            # 5.1.2.4. GET QUESTION MAIN TEXT
            ##
            question_main_text_block = question_middle.find_element_by_xpath(".//div[@class='questao-enunciado']")
            question_text_p_list = question_main_text_block.find_elements_by_tag_name('p')
            question_text_img_list = question_main_text_block.find_elements_by_tag_name('img')

            ext_quest['question_text'] = ''.join([p.text for p in question_text_p_list])
            try:
                ext_quest['question_imgs'] = [img.get_attribute("src") for img in question_text_img_list]
            except Exception as e:
                error_count += 1
                error_list.append({
                    'error_id': 'IMG_LIST',
                    'error_count': 'ERR' + str(error_count),
                    'error_ref': question_text_img_list,
                    'error_detail': traceback.format_exc()
                })
                print '[ERROR] Erro adicionado a lista de erros! Ignorando a questão...'
                continue
            # for p_count in range(len(question_text_p_list)):
            #    ext_quest['question_text'] = ext_quest['question_text'].join(question_text_p_list[p_count].text)

            ##
            # 5.1.2.5. GET QUESTION ALTERNATIVES' TEXTS
            ##
            question_alternatives_li_label_list = alternatives_question.find_elements_by_tag_name('label')
            for label_count in range(len(question_alternatives_li_label_list)):
                ext_quest_option = {
                    "correct": False,
                    "text": question_alternatives_li_label_list[label_count].text
                }

                ext_quest['options'].append(ext_quest_option)

            ##
            # 5.1.2.6. CHECK RIGHT ALTERNATIVE FROM QUESTION
            ##
            if red_alert.get_attribute("style") == "display: none;":
                ext_quest['options'][-1]['correct'] = True
            else:
                alternatives_question = question_middle.find_element_by_xpath(".//div[@class='questao-alternativas']")
                red_alert = alternatives_question.find_element_by_xpath(".//div[@class='alerta-vermelho']")
                alternative_html = red_alert.get_attribute('innerHTML')
                # print alternative_html
                right_question = ''
                true_false_question = False

                re_search = re.search('(\<strong\>)(\()([a-zA-Z])(\)\.)(\<\/strong\>)', alternative_html)
                if re_search is not None:
                    right_question = re_search.group(3)
                else:
                    if len(ext_quest['options']) == 2:
                        print 'Questao de verdadeiro e falso. Mudando a logica...'
                        true_false_question = True
                    else:
                        print 'Logica nao implementada na prova: ' + header_text

                if true_false_question is False:
                    ascii_right_question = ord(right_question)
                    pos = 0
                    if ascii_right_question < 97:
                        pos = ascii_right_question-65
                    else:
                        pos = ascii_right_question-97

                    ext_quest['options'][pos]['correct'] = True
                else:
                    ext_quest['options'][0]['correct'] = True

            extraction['ext_quest_list'].append(ext_quest)
            count += 1

    ##
    # 5.2. OUTPUT EXTRACTION OBJECT WITH QUESTIONS FROM THEME TO JSON FILE
    ##
    print 'outputing...'
    with open('../output/questao-certa-crawler-' + theme_name + '-resultados.json', 'w') as outfile:
        # with open('../output/questao-certa-crawler-' + extraction['theme'] + '-resultados-batch-'
        #           + str(i) + '.json', 'w') as outfile:
        json.dump(extraction, outfile)

    ##
    # 5.3. OUTPUT ERROR LIST TO JSON FILE
    ##
    if len(error_list) > 0:
        print 'outputing errors...'
        with open('../errors/questao-certa-crawler-' + theme_name + '-errors.json', 'w') as outfile:
            # with open('../output/questao-certa-crawler-' + extraction['theme'] + '-resultados-batch-'
            #           + str(i) + '.json', 'w') as outfile:
            json.dump(error_list, outfile)

    # print 'batch ' + str(i) + ' finished!'
    # # last batch reduce the total iterated pages to total_pages_rest
    # if i == extraction_iterations - 1:
    #     total_pages_per_iter = total_pages_rest
    #
    # # next batch
    # start = end
    # end = end + total_pages_per_iter

    # print 'extraction successful for ' + str(extraction_iterations) + ' batches! Check output folder.'
    print '--- Extraction successful for ' + str(count) + ' questions and unsuccessful for ' + str(error_count) + ' questions from theme ' + theme_name + '! Check output/errors folder. ---'

driver.close()
