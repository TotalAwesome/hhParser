import requests
import json
from time import sleep
import os

region_List = [
                '1', # Москва
                '2019', # Московская область
                '145',  # Ленинградская область
                '2',    # Санкт-Петербург

                ]

search_List = [
                'кассир',
                'продавец',
                'кладовщик',
                'разнорабочий',
                'уборщица',
                'товаровед'
                ]



period = '30'                       # Искать вакансии за последние N дней (В любом случае ХХ не отдаст более 2000 вакансий)
CSV_path = os.path.split( os.path.realpath(__file__) )[0]+'\\'


URL_search = 'https://api.hh.ru/vacancies'
URL_AREAS = 'https://api.hh.ru/areas'


def print_areas_List(json):
    Id_List = []
    for i in json:
        print ( i['id'] + '  :  ' + i['name'])
        Id_List.append(i['id'])
    return Id_List

def get_region_Id():

    res = requests.get(URL_AREAS)
    json = res.json()
    Id_List = []
    region = ''

    selected = False
    while not selected:
        Id_List = print_areas_List(json) 
        print ('- '*50)
        print ('Введите номер региона либо оставь поле пустым для поиска на текущем уровне:')
        Id = None
        while Id == None:
            Id = input()
            if Id not in Id_List and Id != '':
                print ('Введен неправильный Id')
                Id = None
        if Id != '':
            for i in json:
                if i['id'] == Id:
                    region = Id
                    level = i
            if 'areas' in level and len(level['areas']) > 0 : 
                json = level['areas']
            else:
                selected = True
        else:
            selected = True
    return region

def parse_vacancy(items):
    result = []
    for i in items:
        line =i['published_at'] +';'+i['name'] + ';'+ i['employer']['name']+';'
        if i['contacts'] != None:
            line = line +i['contacts']['name']
            if i['contacts']['email'] != None:
                line = line +';'+ i['contacts']['email']
            else:
                line = line +';'
            for num in i['contacts']['phones']:
                line = line + ';' + num['country'] + num['city'] + num['number']
        result.append(line+'\n') 
    return result   

def get_search_List():
    print ('Вводите слова для поискаи нажимайте ENTER. Пустая строка будет означать что слов для поиска больше не будет')
    word = ''
    result = []
    repeat = True
    while repeat:
        word = input()
        if word != '':
            result.append(word)
        else:
            repeat = False
    return result

def get_vacancies(region_Id,text,period):
    page = 0
    endpage = False
    endpagecontacts_List = []
    while not endpage:
        if page == 0:
            page_text = ''
        else:
            page_text = '&page='+str(page)
        url_vacancies = URL_search + '?text='+text+'&per_page=100&area='+str(region_Id)+'&period='+ period+page_text
        res = requests.get(url_vacancies)
        json = res.json()
        if 'bad_argument' not in json:
            page = json['page']
            pageS = int( json['pages'] )
            endpagecontacts_List = endpagecontacts_List + parse_vacancy(json['items'])
            
            if page == pageS-1:
                endpage = True
            else:
                page += 1
        else:
            endpage = True

        print ('Обработано {} вакансий'.format( len(endpagecontacts_List)))
     
    return endpagecontacts_List

def save_csv(text): # Лог в консоль
    path = CSV_path+'contacts.csv'
    path2 = CSV_path+'contacts_1251.csv'
    data = 'ДАТА ПУБЛИКАЦИИ;ВАКАНСИЯ;ПРЕДПРИЯТИЕ;КОНТАКТНОЕ ЛИЦО;EMAIL;ТЕЛЕФОН\n\n'
    for i in text:
        data += i
    
    if not os.path.exists(path):
        csv_file = open(path , 'w')
        csv_file.write(data)
        csv_file.close()
    else:
        csv_file = open( path, 'a')
        csv_file.write(data)
        csv_file.close()

    
    if not os.path.exists(path2):
        csv_file = open(path2 , 'w', encoding='cp1251', errors='replace')
        csv_file.write(data)
        csv_file.close()
    else:
        csv_file = open( path2, 'a', encoding='cp1251', errors='replace')
        csv_file.write(data)
        csv_file.close()

def main():
    global region_List
    global search_List
    global period 
    TABLE = []
    List =search_List.copy()
    Input = ''
    print('Обработать списки (1) или ввести данные вручну? (2) ')
    repeat =True
    while (Input !='1' and Input!='2'):
        Input = input()
        if Input != '1' and Input != '2':
             print('Введите 1 или 2')
    if Input == '2':
        region_List =[]
        region_List.append(get_region_Id())
        List = get_search_List()

    for region_Id in region_List:
        for i in List:
            TABLE += get_vacancies(region_Id, i, period)
        save_csv(TABLE)
            

main()