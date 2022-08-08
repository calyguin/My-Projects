import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from psycopg2 import Error
from openpyxl import Workbook
import datetime

# URL - отправная точка парсера
urlMain = 'https://zakupki.gov.ru/epz/orderplan/search/results.html?morphology=on&search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&structuredCheckBox=on&structured=true&notStructured=false&fz44=on&actualPeriodRangeYearFrom=2020&customerPlace=5277400&customerPlaceCodes=14000000000&publishDateFrom=01.01.2020&publishDateTo=01.01.2020&sortBy=BY_MODIFY_DATE&pageNumber=1&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&searchType=false'

# Credentials для requests
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
session = requests.Session()
retry = Retry(connect=20, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
session.get(urlMain, headers=headers)

# Библиотека спаршенных данных
parsedData = {'Уникальный номер плана-графика закупок': '', 'Кол-во позиций': '',
              'Бюджет на 2022 год': '', 'Наименование Заказчика': '',
              'Статус': '', 'Место нахождения (адрес)': '', 'Дата утверждения плана-графика закупок': '',
              'Адрес электронной почты': '', 'Телефон': '', 'ИНН': '', 'Дата регистрации': ''}

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
budgetUrl = ''
pageNum = 1
linksArr = []
startDate = datetime.datetime.strptime('01.01.2020', '%d.%m.%Y')

try:

    # Парсинг всех необходимых данных со страницы закупки
    # Получение номера закупки
    def getOrderNum(url):

        global budgetUrl

        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        contentContainers = soup.findAll('div', 'row blockInfo')

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

    # Получение наименования заказчика
    def getCustomerName(url):

        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        contentContainers = soup.findAll('div', 'row blockInfo')

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

    # Получение статуса закупки
    def getStatus(url):

        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        contentContainers = soup.findAll('div', 'row blockInfo')

        for contentContainer in contentContainers:
            contentRows = contentContainer.findAll('section', 'blockInfo__section')
            for contentRow in contentRows:

                textTitle = contentRow.find('span', 'section__title')
                if textTitle:
                    textValue = contentRow.find('span', 'section__info')
                    if textTitle.text.lower() == 'статус':
                        orderStatus = textValue.text.strip()
                        parsedData['Статус'] = orderStatus

    # Получение адреса заказчика
    def getAddress(url):

        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        contentContainers = soup.findAll('div', 'row blockInfo')

        for contentContainer in contentContainers:
            contentRows = contentContainer.findAll('section', 'blockInfo__section')
            for contentRow in contentRows:

                textTitle = contentRow.find('span', 'section__title')
                if textTitle:
                    textValue = contentRow.find('span', 'section__info')
                    if textTitle.text.lower() == 'место нахождения (адрес)':
                        address = textValue.text.strip()
                        parsedData['Место нахождения (адрес)'] = address

    # Получение даты утверждения закупки
    def getOrderDate(url):

        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        contentContainers = soup.findAll('div', 'row blockInfo')

        for contentContainer in contentContainers:
            contentRows = contentContainer.findAll('section', 'blockInfo__section')
            for contentRow in contentRows:

                textTitle = contentRow.find('span', 'section__title')
                if textTitle:
                    textValue = contentRow.find('span', 'section__info')
                    if textTitle.text.lower() == 'дата утверждения плана-графика закупок':
                        orderDate = textValue.text.strip()
                        parsedData['Дата утверждения плана-графика закупок'] = orderDate

    # Получение электронной почты заказчика
    def getCustomerEmail(url):

        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        contentContainers = soup.findAll('div', 'row blockInfo')

        for contentContainer in contentContainers:
            contentRows = contentContainer.findAll('section', 'blockInfo__section')
            for contentRow in contentRows:

                textTitle = contentRow.find('span', 'section__title')
                if textTitle:
                    textValue = contentRow.find('span', 'section__info')
                    if textTitle.text.lower() == 'адрес электронной почты':
                        customerEmail = textValue.text.strip()
                        parsedData['Адрес электронной почты'] = customerEmail

    # Получение номера телефона заказчика
    def getCustomerPhoneNum(url):

        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        contentContainers = soup.findAll('div', 'row blockInfo')

        for contentContainer in contentContainers:
            contentRows = contentContainer.findAll('section', 'blockInfo__section')
            for contentRow in contentRows:

                textTitle = contentRow.find('span', 'section__title')
                if textTitle:
                    textValue = contentRow.find('span', 'section__info')
                    if textTitle.text.lower() == 'телефон':
                        customerPhoneNum = textValue.text.strip()
                        parsedData['Телефон'] = customerPhoneNum

    # Парсинг всех необходимых данных со страницы организации заказчика
    # Получение ИНН заказчика
    def getINN():

        global orgUrl
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

    # Получение даты регистрации организации заказчика
    def getOrgRegDate():

        global orgUrl
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

    # Получаем годовой бюджет закупки (нет)
    def getBudget():

        global budgetUrl
        response = session.get(budgetUrl, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        try:
            contentContainers = soup.find('table', 'blockInfo__table tableBlock').find('tr', 'tableBlock__row').findAll('th',
                                                                                                                'tableBlock__col tableBlock__col_header tableBlock__col_right')
            index = 0
            for line in contentContainers:
                if (line.text.strip() == 'На 2022 год'):
                    break
                index += 1
            budgetData = soup.find('tbody', 'tableBlock__body').find('tr', 'tableBlock__row').findAll('td', 'tableBlock__col tableBlock__col_right')
            budget = budgetData[index].text.strip()
            parsedData['Бюджет на 2022 год'] = budget
        except:
            parsedData['Бюджет на 2022 год'] = '-'

    # Получаем список закупок и кол-во позиций
    def getOrders():

        global pageNum
        global urlMain
        global startDate

        response = session.get(urlMain, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        contentContainers = soup.findAll('div', 'row no-gutters registry-entry__form mr-0')

        print('\nLink: ' + urlMain + '\nPage: ' + str(pageNum) + '\nDate: ' + str(startDate.strftime('%d.%m.%Y')) + '\n')

        for contentContainer in contentContainers:
            # Получаем URL закупки
            orderUrl = 'https://zakupki.gov.ru' + contentContainer.find('div', 'registry-entry__header-mid__number').find('a').get('href')
            # Получаем кол-во позиций
            posNumContainer = contentContainer.find('div', 'registry-entry__body-caption float-right cursor-pointer')
            if posNumContainer:
                posNum = contentContainer.find('div', 'registry-entry__body-caption float-right cursor-pointer').text.strip()
                parsedData['Кол-во позиций'] = posNum
            else:
                parsedData['Кол-во позиций'] = '-'
            runParser(orderUrl)
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
            wb.save("parsedData.xlsx")

        # Проверяем есть ли закупки на следующей странице, если есть - парсим дальше, если нет - меняем дату
        if contentContainers:
            pageNum += 1
            urlMain = 'https://zakupki.gov.ru/epz/orderplan/search/results.html?morphology=on&search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&structuredCheckBox=on&structured=true&notStructured=false&fz44=on&actualPeriodRangeYearFrom=2020&customerPlace=5277400&customerPlaceCodes=14000000000&publishDateFrom=' + str(startDate.strftime('%d.%m.%Y')) + '&publishDateTo=' + str(startDate.strftime('%d.%m.%Y')) + '&sortBy=BY_MODIFY_DATE&pageNumber=' + str(pageNum) + '&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&searchType=false'
            getOrders()
        else:
            pageNum = 1
            startDate = startDate + datetime.timedelta(days=1)
            urlMain = 'https://zakupki.gov.ru/epz/orderplan/search/results.html?morphology=on&search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&structuredCheckBox=on&structured=true&notStructured=false&fz44=on&actualPeriodRangeYearFrom=2020&customerPlace=5277400&customerPlaceCodes=14000000000&publishDateFrom=' + str(startDate.strftime('%d.%m.%Y')) + '&publishDateTo=' + str(startDate.strftime('%d.%m.%Y')) + '&sortBy=BY_MODIFY_DATE&pageNumber=' + str(pageNum) + '&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&searchType=false'
            getOrders()

    # Запуск парсинга всех необходимых данных
    def runParser(url):
        getOrderNum(url)
        getCustomerName(url)
        getStatus(url)
        getAddress(url)
        getOrderDate(url)
        getCustomerEmail(url)
        getCustomerPhoneNum(url)
        getINN()
        getOrgRegDate()
        getBudget()

    # Функция - лаунчер для if __name__ == '__main__'
    def main():
        getOrders()

    if __name__ == '__main__':
        main()

except (Exception, Error) as error:
    print(error)