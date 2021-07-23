import requests
import json
from time import sleep
import os

REGION_LIST = [
                '1', # Москва
                '2019', # Московская область
                '145',  # Ленинградская область
                '2',    # Санкт-Петербург

                ]

SEARCH_LIST = [
                'кассир',
                'продавец',
                'кладовщик',
                'разнорабочий',
                'уборщица',
                'товаровед'
                ]



PERIOD = '30'                       # Искать вакансии за последние N дней (В любом случае ХХ не отдаст более 2000 вакансий)
CSV_PATH = os.path.split( os.path.realpath(__file__) )[0]+'\\'


URL_SEARCH = 'https://api.hh.ru/vacancies'
URL_AREAS = 'https://api.hh.ru/areas'


def print_areas_list(JSON):
    ID_LIST = []
    for i in JSON:
        print ( i['id'] + '  :  ' + i['name'])
        ID_LIST.append(i['id'])
    return ID_LIST

def get_region_id():

    RES = requests.get(URL_AREAS)
    JSON = RES.json()
    ID_LIST = []
    REGION = ''

    SELECTED = False
    while not SELECTED:
        ID_LIST = print_areas_list(JSON) 
        print ('- '*50)
        print ('Введите номер региона либо оставь поле пустым для поиска на текущем уровне:')
        ID = None
        while ID == None:
            ID = input()
            if ID not in ID_LIST and ID != '':
                print ('Введен неправильный ID')
                ID = None
        if ID != '':
            for i in JSON:
                if i['id'] == ID:
                    REGION = ID
                    LEVEL = i
            if 'areas' in LEVEL and len(LEVEL['areas']) > 0 : 
                JSON = LEVEL['areas']
            else:
                SELECTED = True
        else:
            SELECTED = True
    return REGION

def parse_vacancy(ITEMS):
    result = []
    for i in ITEMS:
        LINE =i['published_at'] +';'+i['name'] + ';'+ i['employer']['name']+';'
        if i['contacts'] != None:
            LINE = LINE +i['contacts']['name']
            if i['contacts']['email'] != None:
                LINE = LINE +';'+ i['contacts']['email']
            else:
                LINE = LINE +';'
            for num in i['contacts']['phones']:
                LINE = LINE + ';' + num['country'] + num['city'] + num['number']
        result.append(LINE+'\n') 
    return result   

def get_search_list():
    print ('Вводите слова для поискаи нажимайте ENTER. Пустая строка будет означать что слов для поиска больше не будет')
    WORD = ''
    RESULT = []
    REPEAT = True
    while REPEAT:
        WORD = input()
        if WORD != '':
            RESULT.append(WORD)
        else:
            REPEAT = False
    return RESULT

def get_vacancies(REGION_ID,TEXT,PERIOD):
    PAGE = 0
    ENDPAGE = False
    CONTACTS_LIST = []
    while not ENDPAGE:
        if PAGE == 0:
            PAGE_TEXT = ''
        else:
            PAGE_TEXT = '&page='+str(PAGE)
        URL_VACANCIES = URL_SEARCH + '?text='+TEXT+'&per_page=100&area='+str(REGION_ID)+'&period='+ PERIOD+PAGE_TEXT
        RES = requests.get(URL_VACANCIES)
        JSON = RES.json()
        if 'bad_argument' not in JSON:
            PAGE = JSON['page']
            PAGES = int( JSON['pages'] )
            CONTACTS_LIST = CONTACTS_LIST + parse_vacancy(JSON['items'])
            
            if PAGE == PAGES-1:
                ENDPAGE = True
            else:
                PAGE += 1
        else:
            ENDPAGE = True

        print ('Обработано {} вакансий'.format( len(CONTACTS_LIST)))
     
    return CONTACTS_LIST

def save_csv(TEXT): # Лог в консоль
    PATH = CSV_PATH+'contacts.csv'
    PATH2 = CSV_PATH+'contacts_1251.csv'
    DATA = 'ДАТА ПУБЛИКАЦИИ;ВАКАНСИЯ;ПРЕДПРИЯТИЕ;КОНТАКТНОЕ ЛИЦО;EMAIL;ТЕЛЕФОН\n\n'
    for i in TEXT:
        DATA += i
    
    if not os.path.exists(PATH):
        CSV_FILE = open(PATH , 'w')
        CSV_FILE.write(DATA)
        CSV_FILE.close()
    else:
        CSV_FILE = open( PATH, 'a')
        CSV_FILE.write(DATA)
        CSV_FILE.close()

    
    if not os.path.exists(PATH2):
        CSV_FILE = open(PATH2 , 'w', encoding='cp1251', errors='replace')
        CSV_FILE.write(DATA)
        CSV_FILE.close()
    else:
        CSV_FILE = open( PATH2, 'a', encoding='cp1251', errors='replace')
        CSV_FILE.write(DATA)
        CSV_FILE.close()

def main():
    global REGION_LIST
    global SEARCH_LIST
    global PERIOD 
    TABLE = []
    LIST =SEARCH_LIST.copy()
    INPUT = ''
    print('Обработать списки (1) или ввести данные вручну? (2) ')
    REPEAT =True
    while (INPUT !='1' and INPUT!='2'):
        INPUT = input()
        if INPUT != '1' and INPUT != '2':
             print('Введите 1 или 2')
    if INPUT == '2':
        REGION_LIST =[]
        REGION_LIST.append(get_region_id())
        LIST = get_search_list()

    for REGION_ID in REGION_LIST:
        for i in LIST:
            TABLE += get_vacancies(REGION_ID, i, PERIOD)
        save_csv(TABLE)
            

main()