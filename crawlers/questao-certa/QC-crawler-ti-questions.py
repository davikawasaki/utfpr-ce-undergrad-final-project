#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-07-28 11:56:11
# Project: questaocertati

import re
import unicodedata
from pyspider.libs.base_handler import *

auth = {
    'email': 'd_s_m_k_@hotmail.com',
    'password': '123456'
}

url = 'https://www.questaocerta.com.br/'
url_nested = url + 'questoes/disciplina/'
url_login = url + 'login/'
url_questions = url + 'questoes/'


class Accents(object):
    @staticmethod
    def remove_accents(s):
        return unicodedata.normalize('NFD', s).encode('ascii', 'ignore')


class Handler(BaseHandler):
    crawl_config = {
        'itag': 'v1',
        "taskdb": "mongodb+taskdb://127.0.0.1:27017/pyspider_taskdb",
        "projectdb": "mongodb+projectdb://127.0.0.1:27017/pyspider_projectdb",
        "resultdb": "mongodb+resultdb://127.0.0.1:27017/pyspider_resultdb"
    }

    @every(minutes=60)
    def on_start(self):
        self.crawl(url, callback=self.index_page)

    @config(age=120)
    def index_page(self, response):
        self.crawl(url_login, callback=self.login_page)

    @config(priority=2)
    def login_page(self, response):
        self.crawl(url_login, callback=self.redirect_questions,
                   method='POST', data={'data[Aluno][email]': auth['email'], 'data[Aluno][senha]': auth['password'],
                                        'data[Aluno][relembrar]': 1})

    @config(priority=3)
    def redirect_questions(self, response):
        self.crawl(url_questions, callback=self.load_pages)

    @config(priority=3)
    def load_pages(self, response):
        for item in response.doc('select#filtro_disciplina>option').items():
            if item.text() != "Disciplina":
                if '(ti)' in item.val():
                    print item.val()
                    self.crawl(url_nested + item.val(), callback=self.detail_page)

    @config(priority=4)
    def detail_page(self, response):
        count = 0
        page = 1

        extraction = {
            'theme': re.search('(.+)(disciplina\/)(.+)(-\(ti\))', response.url).group(3).replace('-', ' '),
            'ext_quest_list': []
        }

        pagination = response.doc(
            'HTML>BODY>DIV.wrapper>SECTION.middle>DIV.container>DIV.middle-content>SECTION.questoes>DIV.paginacao')
        last_span_a = pagination.children()('span a')[-1]
        total_pages = re.search('(.+)(-\(ti\)\/)(\d+)', last_span_a.attrib.get('href')).group(3)

        # loop against each page
        for i in range(int(total_pages)):
            self.crawl(response.url + '/' + str(page), callback=self.questions_login_page,
                           fetch_type='js', js_script='''
                           function() {
                               var list = document.getElementsByClassName('ver-texto-associado');
                               for(var i=0; i<list.length; i++) { 
                                   if (list[i]) {
                                       list[i].click();
                                   }
                               }
                               var list = document.querySelectorAll('div.questao-miolo');
                               for(var i=0; i<list.length; i++) {
                                   list[i].lastElementChild.firstElementChild.firstElementChild.firstElementChild.firstElementChild.firstElementChild.click()
                               }
                            
                               list = document.querySelectorAll('div.questao-alternativas');
                               for(var i=0; i<list.length; i++) {
                                   list[i].querySelector('a').click();
                               }
                           }
                           ''')

    @config(priority=5)
    def questions_login_page(self, response):
        response.doc('FORM#flogin>INPUT#usuarioLogin').val(auth['email'])
        response.doc('FORM#flogin>INPUT#senhaLogin').val(auth['password'])
        response.doc('FORM#flogin').children()[4].click()

    @config(priority=6)
    def questions_page(self, response):
        # loop against each question
        for question in response.doc(
                'HTML>BODY>DIV.wrapper>SECTION.middle>DIV.container>DIV.middle-content>SECTION.questoes>ARTICLE').items():
            print '---'
            ext_quest = {
                "options": []
            }

            # Get header test name
            header_text = question.children()('header').children().text()
            ext_quest['test_name'] = re.search('(Prova:\s)([\S+\-\s0-9]+)(Disciplina:)', header_text).group(2)

            # Get test question text
            question('DIV.questao-miolo>DIV.questao-enunciado').children()('a').remove()
            ext_quest['question_text'] = question('DIV.questao-miolo>DIV.questao-enunciado').children().text()

            # Get test question options
            for question_option_li in question('DIV.questao-miolo>DIV.questao-alternativas>UL>LI').children():
                ext_quest_option = {
                     "correct": False,
                     "text": question_option_li.text_content().replace('\n', ' ').replace('  ', '')
                }

        #         for classe in question_option_li.values():
        #             if "resposta-correta" in classe:
        #                 ext_quest_option['correct'] = True
        #
        #         ext_quest['options'].append(ext_quest_option)
        #
        #     #print ext_quest
        #     count = count + 1
        #     extraction['ext_quest_list'].append(ext_quest)
        # return extraction
