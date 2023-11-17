from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.chrome.service import Service
import re


def get_start_index():
    f = open('start.txt', mode='r')
    data = f.read()
    return int(data)


def data_extracted(count):
    f = open('collected.txt', mode='a')
    f.writelines(f'Data has been collected on Page number: {count} ' + '\n')


def print_start_index(count):
    f = open('start.txt', mode='w')
    data = str(count+1)
    f.write(data)


def fail_to_write(count):
    f = open('Not_found.txt', mode='a')
    f.writelines(f'The data is not available on page number: {count}' + '\n')


def web_scraping(count):
    service = Service(executable_path='D:\chromedriver-win64\chromedriver.exe')
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    #    lists
    car_titles = []
    milages = []
    registration_dates = []
    powers = []
    transmissions = []
    fuel_types = []
    country_names = []
    prices = []
    photos = []
    print(f'Current page number is {count}')

    try:
        url = f"https://carvago.com/cars?page={count}"
        driver.get(url)
        content = driver.page_source
        soup = BeautifulSoup(content, features="html.parser")

        count1 = 0
        for a in soup.findAll('div', attrs={'data-testid': "feature.car.card"}):
            det = "No detail available"
            count1 += 1
            car_title = a.find('h4', attrs={'data-testid': 'feature.car.card_serp_row_title'})
            mileage = a.find('p', attrs={'data-testid': 'desc-mileage'})
            registration_date = a.find('p', attrs={'data-testid': 'desc-registration-date'})
            power = a.find('p', attrs={'data-testid': 'desc-power'})
            transmission = a.find('p', attrs={'data-testid': 'desc-transmission'})
            fuel_type = a.find('p', attrs={'data-testid': 'desc-fuel-type'})
            delivery_info = a.find('p', attrs={'data-testid': "serp.car_card.delivery_info_label"})
            price_data = a.find('h4', attrs={'data-testid': 'feature.serp_car_card.price'})
            photo = a.find('p', attrs={'class': "chakra-text css-1x2ei3v"})
            if car_title:
                car_titles.append(car_title.text)
            else:
                car_titles.append(det)
            if mileage:
                data = mileage.text
                matches = re.findall(r'[0-9]+', data)
                mil = int(''.join(matches).replace(',', ''))
                milages.append(mil)
            else:
                milages.append(det)
            if registration_date:
                registration_dates.append(registration_date.text)
            else:
                registration_dates.append(registration_date)
            if power:
                powers.append(power.text.split()[0])
            else:
                powers.append(power)
            if transmission:
                transmissions.append(transmission.text)
            else:
                transmissions.append(det)
            if fuel_type:
                fuel_types.append(fuel_type.text)
            else:
                fuel_types.append(det)
            if delivery_info:
                data = delivery_info.text.split(',')[0].strip()
                country_names.append(data)
            else:
                country_names = det
            if price_data:
                price = price_data.text
                price_str = price.replace("€", "").replace(" ", "").replace("\xa0", "")
                prices.append(int(price_str)*100)
            else:
                prices.append(det)
            if photo:
                photos.append(photo.text)
            else:
                photos.append(det)

        df = pd.DataFrame(
            {'Car Title': car_titles, 'Price': prices, 'Milage': milages, 'Power': powers,
             'Registration Date': registration_dates, 'Transmission': transmissions, 'Country': country_names,
             'Fuel Type': fuel_types, 'Photos Upload': photos})
        df.to_csv('Car_Vago(Scraped_data).csv', mode='a', header=False, index=False, encoding='utf-8')
        print(f"Total data extracted: {count1} ")
        data_extracted(count)
        print_start_index(count)
    except:
        fail_to_write(count)
        print(f'May be error occur on Page number; {count}')


if __name__ == '__main__':
    start = get_start_index()
    for x in range(start, 15000):
        web_scraping(x)
