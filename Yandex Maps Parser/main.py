from psycopg2 import Error
from openpyxl import Workbook
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import selenium.common.exceptions
import selenium.webdriver as webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

try:

    urlMain = 'https://yandex.ru/maps/48/orenburg/category/management_company/184105510/?ll=55.131744%2C51.795813&sll=55.131744%2C51.795813&sspn=0.302811%2C0.107505&z=12'

    parsedData = {'Название': '',
                  'Адрес': '',
                  'Номер телефона': '',
                  'Сайт': '',
                  'Контакты': '',
                  'Рейтинг': '',
                  'Кол-во оценок': ''
                  }

    wb = Workbook()
    wb['Sheet'].title = 'List'
    mainSheet = wb.active
    columnNames = ['Название', 'Адрес', 'Номер телефона', 'Сайт', 'Контакты', 'Рейтинг', 'Кол-во оценок']
    mainSheet.append(columnNames)

    linkIndex = 1
    dictIndex = 1
    scrollIndex = 30
    zhabaIndex = 0
    zhabaCap = 10
    links = []

    def getLinks(url, index):

        global linkIndex, scrollIndex, zhabaIndex

        options = webdriver.FirefoxOptions()
        options.headless = True
        options.add_argument('--window-position=850,0')
        driver = webdriver.Firefox(options=options)
        driver.get(url)
        scrollbar = driver.find_element(by=By.CLASS_NAME, value='scroll__scrollbar-thumb')
        action = ActionChains(driver)

        while True:
            try:
                action.click_and_hold(scrollbar).move_by_offset(0, index).perform()
                action.reset_actions()
                try:
                    driver.find_element(by=By.CLASS_NAME, value='add-business-view')
                    zhabaIndex += 1
                    print('Parsing is being finished: ' + str(zhabaIndex) + '/' + str(zhabaCap))
                    if zhabaIndex == zhabaCap:
                        break
                except selenium.common.exceptions.NoSuchElementException:
                    pass
            except selenium.common.exceptions.MoveTargetOutOfBoundsException:
                try:
                    action.click_and_hold(scrollbar).move_by_offset(0, index / 2).perform()
                    action.reset_actions()
                    try:
                        driver.find_element(by=By.CLASS_NAME, value='add-business-view')
                        zhabaIndex += 1
                        print('Parsing is being finished: ' + str(zhabaIndex) + '/' + str(zhabaCap))
                        if zhabaIndex == zhabaCap:
                            break
                    except selenium.common.exceptions.NoSuchElementException:
                        pass
                except selenium.common.exceptions.MoveTargetOutOfBoundsException:
                    try:
                        action.click_and_hold(scrollbar).move_by_offset(0, index / 3).perform()
                        action.reset_actions()
                        try:
                            driver.find_element(by=By.CLASS_NAME, value='add-business-view')
                            zhabaIndex += 1
                            print('Parsing is being finished: ' + str(zhabaIndex) + '/' + str(zhabaCap))
                            if zhabaIndex == zhabaCap:
                                break
                        except selenium.common.exceptions.NoSuchElementException:
                            pass
                    except selenium.common.exceptions.MoveTargetOutOfBoundsException:
                        try:
                            action.click_and_hold(scrollbar).move_by_offset(0, index / 4).perform()
                            action.reset_actions()
                            try:
                                driver.find_element(by=By.CLASS_NAME, value='add-business-view')
                                zhabaIndex += 1
                                print('Parsing is being finished: ' + str(zhabaIndex) + '/' + str(zhabaCap))
                                if zhabaIndex == zhabaCap:
                                    break
                            except selenium.common.exceptions.NoSuchElementException:
                                pass
                        except selenium.common.exceptions.MoveTargetOutOfBoundsException:
                            try:
                                action.click_and_hold(scrollbar).move_by_offset(0, index / 5).perform()
                                action.reset_actions()
                                try:
                                    driver.find_element(by=By.CLASS_NAME, value='add-business-view')
                                    zhabaIndex += 1
                                    print('Parsing is being finished: ' + str(zhabaIndex) + '/' + str(zhabaCap))
                                    if zhabaIndex == zhabaCap:
                                        break
                                except selenium.common.exceptions.NoSuchElementException:
                                    pass
                            except selenium.common.exceptions.MoveTargetOutOfBoundsException:
                                try:
                                    action.click_and_hold(scrollbar).move_by_offset(0, 1).perform()
                                    action.reset_actions()
                                    try:
                                        driver.find_element(by=By.CLASS_NAME, value='add-business-view')
                                        zhabaIndex += 1
                                        print('Parsing is being finished: ' + str(zhabaIndex) + '/' + str(zhabaCap))
                                        if zhabaIndex == zhabaCap:
                                            break
                                    except selenium.common.exceptions.NoSuchElementException:
                                        pass
                                except selenium.common.exceptions.MoveTargetOutOfBoundsException:
                                    break

        print('\n')
        html = driver.page_source
        soup = BeautifulSoup(html, features="html.parser")
        contentContainers = soup.findAll('div', 'search-snippet-view__body _type_business')
        for i in contentContainers:
            element = 'https://yandex.ru' + i.find('a', 'search-snippet-view__link-overlay _focusable').get('href')
            print(linkIndex, element)
            links.append(element)
            linkIndex += 1
        print('\n')

    def getData(url):

        global dictIndex

        options = webdriver.FirefoxOptions()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, features="html.parser")

        try:
            parsedData['Название'] = '-'
            getName = soup.find('h1', 'orgpage-header-view__header')
            name = getName.text.strip()
            parsedData['Название'] = name
        except:
            pass

        try:
            parsedData['Адрес'] = '-'
            getAddress = soup.find('a', 'orgpage-header-view__address')
            address = getAddress.text.strip()
            address = address.replace('Оренбург', 'Оренбург ')
            parsedData['Адрес'] = address
        except:
            pass

        try:
            parsedData['Номер телефона'] = '-'
            getPhoneNum = soup.find('div', 'orgpage-phones-view__phone-number')
            phoneNum = getPhoneNum.text.strip()
            parsedData['Номер телефона'] = phoneNum
        except:
            pass

        try:
            parsedData['Сайт'] = '-'
            getBusinessUrl = soup.find('a', 'business-urls-view__link')
            businessUrl = getBusinessUrl.get('href')
            parsedData['Сайт'] = businessUrl
        except:
            pass

        try:
            getUrlContainer = soup.findAll('div', 'business-contacts-view__social-button')
            contacts = ''
            for i in getUrlContainer:
                urlContainer = i.find('a').get('href')
                contacts = contacts + urlContainer + ' '
            parsedData['Контакты'] = contacts
        except:
            pass

        try:
            getRatingContainer = soup.find('span', 'business-summary-rating-badge-view__rating')
            ratingContainer = ''
            for i in getRatingContainer:
                ratingContainer += (i.text.strip())
            parsedData['Рейтинг'] = ratingContainer
        except:
            pass

        try:
            getRatesAmount = soup.find('span', 'business-rating-amount-view _summary')
            ratesAmount = getRatesAmount.text.strip()
            parsedData['Кол-во оценок'] = ratesAmount
        except:
            pass

        print(dictIndex, parsedData)
        dictIndex += 1
        mainSheet.append((parsedData['Название'],
                          parsedData['Адрес'],
                          parsedData['Номер телефона'],
                          parsedData['Сайт'],
                          parsedData['Контакты'],
                          parsedData['Рейтинг'],
                          parsedData['Кол-во оценок']))

        wb.save('parsedData.xlsx')

    def main():
        getLinks(urlMain, scrollIndex)
        with ThreadPoolExecutor(max_workers=(5)) as p:
            p.map(getData, links)

    if __name__ == '__main__':
         main()

except (Exception, Error) as error:
    print(error)