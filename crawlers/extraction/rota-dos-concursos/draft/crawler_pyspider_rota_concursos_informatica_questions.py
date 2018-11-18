#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""Crawler to extract IT Informatics questions from Rota dos Concursos website.

Created at: 2018-07-21 19:26:12
Project: rota_concursos_informatica-microinformatica
Framework used: PySpider
Classes:
    " >>> Accents(object)
    " >>> Handler(BaseHandler)

Accents class static methods:
    " >>> remove_accents(s)

Handler class methods (in execution sequence flow):
    " >>> on_start()
    " >>> index_page(response)
    " >>> detail_page(response)

todo: accept URL JSON config file
returns: JSON from each crawled page in the web pyspider application

"""

import re
import unicodedata
from pyspider.libs.base_handler import *

url = 'http://questoes.grancursosonline.com.br/'
theme = 'informatica-microinformatica'
theme_crawled = url + theme
url_pat = url + 'questoes-de-concursos/' + theme + '-'

regex_url_rule = '(' + url_pat + ')(' + '.+$)'

class Accents(object):
    """Accents class manipulation details.
    :param object:
    """

    @staticmethod
    def remove_accents(s):
        """Remove accents from string.
        :param s:
        :return [string] string_noaccents:
        """
        return unicodedata.normalize('NFD', s).encode('ascii', 'ignore')


class Handler(BaseHandler):
    """PySpider main handler.
    :param BaseHandler (class):
    """

    @every(minutes=24 * 1)
    def on_start(self):
        """PySpider lifecycle starting method.
        Next crawling step: self.index_page
        :return:
        """
        self.crawl(theme_crawled, callback=self.index_page)

    @config(age=1 * 24 * 60 * 60)  # 10 days period
    def index_page(self, response):
        """PySpider lifecycle index page.
        Get link items and crawl each page if match pattern from computer science themes.
        Next crawling step: self.detail_page
        :param response:
        :return:
        """
        # for each in response.doc('div.panel-body > a.list-group-item[href^="http').items():
        for each in response.doc('a').items():
            # If theme match regex pattern for computer science cases, crawl page with JS fn
            # when opening the page to load all questions' answers
            if re.match(url_pat + '.+$', each.attr.href):
                self.crawl(each.attr.href, callback=self.detail_page,
                           fetch_type='js', js_script='''
                           function() {
                               var count = 0;
                               var id = setInterval(function() {
                                   console.log('starting loop',count);
                                   var panel = document.getElementsByClassName('panel panel-default loading-wrapper text-center');
                                   var loadMoreBtn = panel[0].childNodes[1];
                                   var noMoreDiv = panel[0].childNodes[3];
                                   if (loadMoreBtn.attributes.style && loadMoreBtn.attributes.style.nodeValue === "display: none;") {
                                       // No more questions to load
                                   } else {
                                       console.log('clicking new button');
                                       loadMoreBtn.click();
                                   }
                                   count++;
                               }, 500);
                               setTimeout(function() {
                                   clearInterval(id);
                                   var list = document.getElementsByClassName('btn btn-black btn-lg');
                                   for(var i in list) { 
                                       list[i].click();
                                   }
                               }, 15000);
                           }
                           ''')

    @config(priority=2)
    def detail_page(self, response):
        """Detail questions page.
        Get questions' text information and append to ext_quest_list from output extraction object.
        :param response:
        :return [object] extraction:
        """
        count = 0
        extraction = {
            'theme': response.url.split(theme_crawled)[1],
            'ext_quest_list': []
        }

        # Iterate through all div questions
        for question in response.doc('HTML>BODY>DIV.container>DIV.row>SECTION.prova-detalhes>DIV.questao').items():
            ext_quest = {
                "options": []
            }

            # Get header test name
            header_p_list = question('header div.row div.col-a').children()('p')
            if len(header_p_list) == 4:
                if 'Superior' in header_p_list[3].text:
                    ext_quest['test_name'] = header_p_list[0].text

            # Get test question text
            body_question = question('div.panel-body div.panel-questao div.panel-heading')
            body_question_inner_p = body_question.children()('p')
            if len(body_question_inner_p) == 0:
                ext_quest['question_text'] = re.sub(r'[.]+(?![0-9])', r'. ', body_question.text())
            else:
                question_text = ''
                for body_question_p in body_question_inner_p:
                    if body_question_p.text is not None:
                        if len(body_question_p.getchildren()) == 0:
                            question_text = question_text + body_question_p.text
                        else:
                            question_text = question_text + body_question_p.text_content()
                ext_quest['question_text'] = re.sub(r'[.]+(?![0-9])', r'. ', question_text.replace('\n', ' '))
                if ext_quest['question_text'] == '':
                    ext_quest['question_text'] = body_question.text()

            # Get test question options
            body_question_options = question('div.panel-body div.panel-questao div.panel-body ul.list-group')
            inner_options = body_question_options.children()('li')
            for question_option_li in inner_options:
                ext_quest_option = {
                    "correct": False,
                    "text": question_option_li.text_content().replace('\n', ' ').replace('  ', '')
                }

                for classe in question_option_li.values():
                    if "resposta-correta" in classe:
                        ext_quest_option['correct'] = True

                ext_quest['options'].append(ext_quest_option)

            print ext_quest
            count = count + 1
            extraction['ext_quest_list'].append(ext_quest)
        return extraction