#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-07-21 19:26:12
# Project: rota_concursos_ciencia_computacao
# encoding: utf-8

import re
import unicodedata
from pyspider.libs.base_handler import *

url = 'http://www.rotadosconcursos.com.br/'
theme = 'ciencia-da-computacao'

theme_crawled = url + theme
url_pat = 'http://rotadosconcursos.com.br/questoes-de-concursos/' + theme + '-'

regex_url_rule = '(' + url_pat + ')(' + '.+$)'


class Misc(object):
    # @staticmethod
    # Example: html_doc = <pyquery obj>, mid_tags = 'ul > li', el_tag = 'a',
    #          tag_attr = 'href', method_name = 'text', save_attr = 'main_theme',
    #          parent_name = 'banco de dados', nested_list = [{'main_themes': ['seguranca'], 'href': 'http://...'}]
    def get_nested_pyspider_elements(self, html_doc, mid_tags, el_tag, tag_attr, method_name, save_attr, parent_name):
        nested_list = []
        mid_tags_list = mid_tags.replace(' ', '').split('>')
        # item can correspond to the <li> level
        for item in html_doc.children().items():
            inner_el_tag_name = getattr(item.children(el_tag), method_name)()
            inner_el_tag_attr_value = item.children(el_tag).attr[tag_attr]
            # print inner_el_tag_name

            if inner_el_tag_attr_value is None:
                continue
            else:
                # Example: {id: 'mysql', 'main_theme: 'banco de dados', 'a': 'https://...'}
                # print regex_url_rule
                # print inner_el_tag_attr_value
                id_name = re.match(regex_url_rule, inner_el_tag_attr_value).group(2)
                nested_list.append({'id_name': id_name, 'name': inner_el_tag_name,
                                    save_attr: parent_name, tag_attr: inner_el_tag_attr_value})
                # Check if it hasn't nested els (i.e. <ul>) and then add to nested_list with possible nested_save
                inner_html_doc = item.children(mid_tags_list[0])
                if inner_html_doc.html() is not None:
                    # nested_list += self.get_nested_pyspider_elements(inner_html_doc, mid_tags, el_tag, tag_attr,
                    #                                                  method_name, save_attr, inner_el_tag_name)
                    nested_list += self.get_nested_pyspider_elements(inner_html_doc, mid_tags, el_tag, tag_attr,
                                                                     method_name, save_attr, id_name)
        return nested_list

    def get_first_main_theme(self, sub_main_theme, theme_list):
        try:
            pos = [theme['id_name'] for theme in theme_list].index(sub_main_theme)
            if theme_list[pos]['main_theme'] != '':
                return self.get_first_main_theme(theme_list[pos]['main_theme'], theme_list)
            else:
                return theme_list[pos]['name']
        except Exception as e:
            # print "[WARNING] Tema " + sub_main_theme + " nao encontrado na lista! Retornando o tema repassado como argumento..."
            return sub_main_theme


class Accents(object):
    @staticmethod
    def remove_accents(s):
        return unicodedata.normalize('NFD', s).encode('ascii', 'ignore')


class Handler(BaseHandler):
    crawl_config = {
        'itag': 'v2',
        "taskdb": "mongodb+taskdb://127.0.0.1:27017/pyspider_taskdb",
        "projectdb": "mongodb+projectdb://127.0.0.1:27017/pyspider_projectdb",
        "resultdb": "mongodb+resultdb://127.0.0.1:27017/pyspider_resultdb"
    }

    @every(minutes=60)
    def on_start(self):
        self.crawl(theme_crawled, callback=self.index_page)

    @config(age=120)
    def index_page(self, response):
        url_crawling_list = []
        # Main themes
        for each_html in response.doc('ul.list-group').items():
            misc = Misc()
            url_crawling_list = misc.get_nested_pyspider_elements(each_html, 'ul > li', 'a', 'href', 'text',
                                                                  'main_theme', '')
        # for each in response.doc('ul.list-group > li > a.list-group-item').items():
        for crawl_obj in url_crawling_list:
            # Transform inner main themes to most outer one
            misc = Misc()
            crawl_obj['main_theme'] = misc.get_first_main_theme(crawl_obj['main_theme'], url_crawling_list)

            if re.match(url_pat + '.+$', crawl_obj['href']):
                self.crawl(crawl_obj['href'], callback=self.detail_page, save=crawl_obj,
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
        count = 0
        extraction = {
            # 'theme': response.url.split(url_pat)[1],
            'theme': response.save['name'],
            'ext_quest_list': [],
            'main_theme': response.save['main_theme']
        }
        for question in response.doc('HTML>BODY>DIV.container>DIV.row>SECTION.prova-detalhes>DIV.questao').items():
            ext_quest = {
                "subthemes": [],
                'question_imgs': [],
                "options": []
            }

            # Get header test name
            header_p_list = question('header div.row div.col-a').children()('p')
            if len(header_p_list) == 4:
                if 'Superior' in header_p_list[3].text:
                    ext_quest['test_name'] = header_p_list[0].text

            # Get test question text
            # print '---'
            # print count
            body_question = question('div.panel-body div.panel-questao div.panel-heading')
            body_question_inner_p = body_question.children()('p')

            for img_el in body_question_inner_p.items('img'):
                ext_quest['question_imgs'].append(img_el.attr('src'))

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

            for img_el in inner_options.items('img'):
                ext_quest['question_imgs'].append(img_el.attr('src'))

            for question_option_li in inner_options:
                ext_quest_option = {
                    "correct": False,
                    "text": question_option_li.text_content().replace('\n', ' ').replace('  ', '')
                }

                for classe in question_option_li.values():
                    if "resposta-correta" in classe:
                        ext_quest_option['correct'] = True

                ext_quest['options'].append(ext_quest_option)

            # print ext_quest
            count = count + 1
            extraction['ext_quest_list'].append(ext_quest)
        return extraction