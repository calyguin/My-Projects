import os
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from psycopg2 import Error
from openpyxl import Workbook
from datetime import date, timedelta

start_date = date(2020, 1, 1)
end_date = date(2021, 1, 1)

delta = end_date - start_date

daysArr = []

for i in range(delta.days + 1):
    day = start_date + timedelta(days=i)
    daysArr.append(day.strftime('%d.%m.%Y'))

# URL - отправная точка парсера
urlMain = 'https://zakupki.gov.ru/epz/orderplan/search/results.html?morphology=on&search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&structuredCheckBox=on&structured=true&notStructured=false&fz44=on&actualPeriodRangeYearFrom=2020&publishDateFrom=01.01.2020&publishDateTo=01.01.2020&sortBy=BY_MODIFY_DATE&pageNumber=1&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&searchType=false'

# Credentials для requests
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
session = requests.Session()
retry = Retry(connect=20, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
session.get(urlMain, headers=headers)

# Создание Excel листа
wb = Workbook()
wb['Sheet'].title = 'List'
mainSheet = wb.active

columnNames = ['Уникальный номер плана-графика закупок', 'Кол-во позиций',
               'Бюджет на 2022 год', 'Наименование Заказчика', 'Статус',
               'Место нахождения (адрес)', 'Дата утверждения плана-графика закупок', 'Адрес электронной почты',
               'Телефон', 'ИНН', 'Дата регистрации']
mainSheet.append(columnNames)

# Глобальные переменные
orgUrl = ''
pageNum = 1
linksArr = []

try:

    # Парсим все необходимые данные
    def getOrders(link):

        global orgUrl
        global pageNum
        global urlMain

        parsedData = {'Уникальный номер плана-графика закупок': '', 'Кол-во позиций': '',
                      'Бюджет на 2022 год': '', 'Наименование Заказчика': '',
                      'Статус': '', 'Место нахождения (адрес)': '', 'Дата утверждения плана-графика закупок': '',
                      'Адрес электронной почты': '', 'Телефон': '', 'ИНН': '', 'Дата регистрации': ''}

        budgetUrl = ''
        response = session.get(link['link'], headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        contentContainers = soup.findAll('div', 'row blockInfo')

        # Парсим уникальный номер плана-графика закупок
        for contentContainer in contentContainers:
            contentRows = contentContainer.findAll('section', 'blockInfo__section')
            for contentRow in contentRows:

                textTitle = contentRow.find('span', 'section__title')
                if textTitle:
                    textValue = contentRow.find('span', 'section__info')
                    if textTitle.text.lower() == 'уникальный номер плана-графика закупок':
                        orderNum = textValue.text.strip()
                        # Получение ссылки на итоговые показатели закупок
                        budgetUrl = 'https://zakupki.gov.ru/epz/orderplan/pg2020/total-info.html?plan-number=' + orderNum + '&revision-id=&position-number='
                        parsedData['Уникальный номер плана-графика закупок'] = orderNum

        # Парсим наименование заказчика
        for contentContainer in contentContainers:
            contentRows = contentContainer.findAll('section', 'blockInfo__section')
            for contentRow in contentRows:

                textTitle = contentRow.find('span', 'section__title')
                if textTitle:
                    textValue = contentRow.find('span', 'section__info')
                    if textTitle.text.lower() == 'наименование заказчика':
                        # Получение ссылки на страницу организации заказчика
                        global orgUrl
                        orgUrl = 'https://zakupki.gov.ru' + contentRow.find('a').get('href')
                        customerName = textValue.text.strip()
                        parsedData['Наименование Заказчика'] = customerName

        # Парсим статус
        for contentContainer in contentContainers:
            contentRows = contentContainer.findAll('section', 'blockInfo__section')
            for contentRow in contentRows:

                textTitle = contentRow.find('span', 'section__title')
                if textTitle:
                    textValue = contentRow.find('span', 'section__info')
                    if textTitle.text.lower() == 'статус':
                        orderStatus = textValue.text.strip()
                        parsedData['Статус'] = orderStatus

        # Парсим место нахождения (адрес)
        for contentContainer in contentContainers:
            contentRows = contentContainer.findAll('section', 'blockInfo__section')
            for contentRow in contentRows:

                textTitle = contentRow.find('span', 'section__title')
                if textTitle:
                    textValue = contentRow.find('span', 'section__info')
                    if textTitle.text.lower() == 'место нахождения (адрес)':
                        address = textValue.text.strip()
                        parsedData['Место нахождения (адрес)'] = address

        # Парсим дату утверждения плана-графика закупок
        for contentContainer in contentContainers:
            contentRows = contentContainer.findAll('section', 'blockInfo__section')
            for contentRow in contentRows:

                textTitle = contentRow.find('span', 'section__title')
                if textTitle:
                    textValue = contentRow.find('span', 'section__info')
                    if textTitle.text.lower() == 'дата утверждения плана-графика закупок':
                        orderDate = textValue.text.strip()
                        parsedData['Дата утверждения плана-графика закупок'] = orderDate

        # Парсим адрес электронной почты
        for contentContainer in contentContainers:
            contentRows = contentContainer.findAll('section', 'blockInfo__section')
            for contentRow in contentRows:

                textTitle = contentRow.find('span', 'section__title')
                if textTitle:
                    textValue = contentRow.find('span', 'section__info')
                    if textTitle.text.lower() == 'адрес электронной почты':
                        customerEmail = textValue.text.strip()
                        parsedData['Адрес электронной почты'] = customerEmail

        # Парсим телефон
        for contentContainer in contentContainers:
            contentRows = contentContainer.findAll('section', 'blockInfo__section')
            for contentRow in contentRows:

                textTitle = contentRow.find('span', 'section__title')
                if textTitle:
                    textValue = contentRow.find('span', 'section__info')
                    if textTitle.text.lower() == 'телефон':
                        customerPhoneNum = textValue.text.strip()
                        parsedData['Телефон'] = customerPhoneNum

        # Парсим ИНН
        response = session.get(orgUrl, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        contentContainers = soup.findAll('div', 'row blockInfo')

        for contentContainer in contentContainers:
            contentRows = contentContainer.findAll('section', 'blockInfo__section')
            for contentRow in contentRows:

                textTitle = contentRow.find('span', 'section__title')
                if textTitle:
                    textValue = contentRow.find('span', 'section__info')
                    if textTitle.text.lower() == 'инн':
                        INN = textValue.text.strip()
                        parsedData['ИНН'] = INN

        # Парсим дату регистрации
        response = session.get(orgUrl, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        contentContainers = soup.findAll('div', 'row blockInfo')

        for contentContainer in contentContainers:
            contentRows = contentContainer.findAll('section', 'blockInfo__section')
            for contentRow in contentRows:

                textTitle = contentRow.find('span', 'section__title')
                if textTitle:
                    textValue = contentRow.find('span', 'section__info')
                    if textTitle.text.lower() == 'дата регистрации':
                        orgRegDate = textValue.text.strip()
                        parsedData['Дата регистрации'] = orgRegDate

        # Парсим бюджет на 2022 год и кол-во позиций
        response = session.get(budgetUrl, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        try:
            contentContainers = soup.find('table', 'blockInfo__table tableBlock').find('tr', 'tableBlock__row').findAll(
                'th',
                'tableBlock__col tableBlock__col_header tableBlock__col_right')
            index = 0
            for line in contentContainers:
                if (line.text.strip() == 'На 2022 год'):
                    break
                index += 1
            budgetData = soup.find('tbody', 'tableBlock__body').find('tr', 'tableBlock__row').findAll('td',
                                                                                                      'tableBlock__col tableBlock__col_right')
            budget = budgetData[index].text.strip()
            parsedData['Бюджет на 2022 год'] = budget
        except:
            parsedData['Бюджет на 2022 год'] = '-'
        parsedData['Кол-во позиций'] = link['position']
        print(parsedData)
        mainSheet.append((parsedData['Уникальный номер плана-графика закупок'],
                          parsedData['Кол-во позиций'],
                          parsedData['Бюджет на 2022 год'],
                          parsedData['Наименование Заказчика'],
                          parsedData['Статус'],
                          parsedData['Место нахождения (адрес)'],
                          parsedData['Дата утверждения плана-графика закупок'],
                          parsedData['Адрес электронной почты'],
                          parsedData['Телефон'],
                          parsedData['ИНН'],
                          parsedData['Дата регистрации']))

    # Собираем все вместе
    def getLinks(day):
        global linksArr
        global urlMain
        pageCount = 1
        urlMain = 'https://zakupki.gov.ru/epz/orderplan/search/results.html?morphology=on&search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&structuredCheckBox=on&structured=true&notStructured=false&fz44=on&actualPeriodRangeYearFrom=2020&publishDateFrom=' + str(
            day) + '&publishDateTo=' + str(
            day) + '&sortBy=BY_MODIFY_DATE&pageNumber=' + str(
            pageCount) + '&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&searchType=false'
        while True:
            response = session.get(urlMain, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            contentContainers = soup.findAll('div', 'row no-gutters registry-entry__form mr-0')

            for contentContainer in contentContainers:
                linkDict = {'link': '', 'position': ''}
                orderUrl = 'https://zakupki.gov.ru' + contentContainer.find('div','registry-entry__header-mid__number').find('a').get('href')
                print('Day: ' + day + '\n' + 'Link: ' + orderUrl + '\n')
                posNumContainer = contentContainer.find('div',
                                                        'registry-entry__body-caption float-right cursor-pointer')
                if posNumContainer:
                    posNum = contentContainer.find('div',
                                                   'registry-entry__body-caption float-right cursor-pointer').text.strip()
                    linkDict['position'] = posNum
                else:
                    linkDict['position'] = '-'
                # Получаем URL закупки
                linkDict['link'] = orderUrl
                linksArr.append(linkDict)
            if contentContainers:
                pageCount += 1
                urlMain = 'https://zakupki.gov.ru/epz/orderplan/search/results.html?morphology=on&search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&structuredCheckBox=on&structured=true&notStructured=false&fz44=on&actualPeriodRangeYearFrom=2020&publishDateFrom=' + str(
                    day) + '&publishDateTo=' + str(
                    day) + '&sortBy=BY_MODIFY_DATE&pageNumber=' + str(
                    pageCount) + '&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&searchType=false'
            else:
                break

    # Функция - лаунчер для if __name__ == '__main__'
    def main():
        with ThreadPoolExecutor(max_workers=(4)) as p:
            p.map(getLinks, daysArr)
        print('All links have been collected.')
        for item in daysArr:
            print(item)
        with ThreadPoolExecutor(max_workers=(os.cpu_count()*10)) as p:
            p.map(getOrders, linksArr)
        wb.save("parsedData.xlsx")

    if __name__ == '__main__':
        main()

except (Exception, Error) as error:
    print(error)