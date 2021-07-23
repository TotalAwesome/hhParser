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
        print ('Введи номер региона либо оставь поле пустым для поиска на текущем уровне:')
        ID = None
        while ID == None:
            ID = input()
            if ID not in ID_LIST and ID != '':
                print ('Ты чо пёс, введи правильный id!')
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
    if len(RESULT) == 0:
        RESULT = ['']
    return RESULT

def get_vacancies(REGION_ID,TEXT,PERIOD,EMP_ID):
    PAGE = 0
    ENDPAGE = False
    CONTACTS_LIST = []
    while not ENDPAGE:
        if PAGE == 0:
            PAGE_TEXT = ''
        else:
            PAGE_TEXT = '&page='+str(PAGE)
        URL_VACANCIES = URL_SEARCH + '?text='+TEXT+'&per_page=100&area='+str(REGION_ID)+'&employer_id='+EMP_ID+'&period='+ PERIOD+PAGE_TEXT
        RES = requests.get(URL_VACANCIES)
        # print(RES)
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

def print_employers_list(TEXT, REGION):
    URL_EMPLOYERS = 'https://api.hh.ru/employers?'
    URL_EMPLOYERS += 'text='+TEXT
    URL_EMPLOYERS += '&area='+REGION
    PAGE = 0
    ENDPAGE = False
    EMP_LIST = []
    while not ENDPAGE:
        if PAGE == 0:
            PAGE_TEXT = ''
        else:
            PAGE_TEXT = '&page='+str(PAGE)
        URL_EMPLOYERS += '&per_page=100'+PAGE_TEXT
        RES = requests.get(URL_EMPLOYERS)
        JSON = RES.json()
        if 'bad_argument' not in JSON:
            PAGE = JSON['page']
            PAGES = JSON['pages'] 
            LIST = JSON['items']
            for EMP in LIST:
                LINE = 'ID : ' + EMP['id'] + '  Фирма: '+ EMP['name']
                print (LINE)
            if PAGE == PAGES-1:
                ENDPAGE = True
            else:
                PAGE += 1
        else:
            ENDPAGE = True


def main():
    global REGION_LIST
    global SEARCH_LIST
    global PERIOD 
    TABLE = []
    LIST =SEARCH_LIST.copy()
    INPUT = ''

    # print()
    while True:
        INPUT = input ('Обработать списки (1) или ввести данные вручну? (2) ')
        if INPUT == '2':
            REGION_LIST =[]
            REGION_LIST.append(get_region_id())
            LIST = get_search_list()
            break
        if INPUT == '1':
            break

    # REPEAT =True
    # while (INPUT !='1' and INPUT!='2'):
    #     INPUT = input()
    #     if INPUT != '1' and INPUT != '2':
    #          print('Введите 1 или 2')
    # if INPUT == '2':
    #     REGION_LIST =[]
    #     REGION_LIST.append(get_region_id())
    #     LIST = get_search_list()

    while True:
        INPUT = input('Получить список работодателей в выбранных регионах? (1 - Да, 2 - Нет): ')
        if INPUT == '2':
            break
        if INPUT == '1':
            INPUT = input('Введи текст для поиска, например "ИНКО" или оставь поле пустым: ')
            for AREA in REGION_LIST:
                print_employers_list(INPUT,AREA)
            break
    EMP_ID = ''
    while True:
        INPUT = input('Добавить к поиску фильтр по работодателю? (1 - Да, 2 - Нет): ')
        if INPUT == '2':
            break
        if INPUT == '1':
            INPUT = input('Введи ID работодателя: ')
            EMP_ID = INPUT
            break
    

    for REGION_ID in REGION_LIST:
        for i in LIST:
            TABLE += get_vacancies(REGION_ID, i, PERIOD, EMP_ID)
        print (TABLE)
        save_csv(TABLE)
            

main()