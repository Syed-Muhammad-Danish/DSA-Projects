from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.chrome.service import Service


def write_record_file(record):
    file = open('record.txt', mode='a')
    file.writelines(record + '\n')
    file.close()


def web_scraping(ct, pur, count):
    service = Service(executable_path='C:\chromedriver-win64\chromedriver.exe')
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    products = []  # list of all property name
    prices = []  # List of all property's prices
    descriptions = []  # list contain the description of properties
    bedrooms = []  # list of bedrooms
    washrooms = []  # list of washrooms
    photos_uploads = []  # list of number of photos uploaded
    property_sizes = []  # list of size of property

    try:
        url = f"https://www.zameen.com/{pur}/{ct}-{count}.html"
        driver.get(url)
        content = driver.page_source
        soup = BeautifulSoup(content, features="html.parser")

        purpose = soup.find('span', attrs={'class': 'ef5cccac'}).text
        city = soup.find('div', attrs={'aria-label': 'City filter'}).text
        property_type = soup.find('div', attrs={'aria-label': 'Category filter'}).text
        count1 = 0
        for a in soup.findAll('li', attrs={'class': 'ef447dde'}):
            det = "No detail available"
            count1 += 1
            name = a.find('div', attrs={'class': '_162e6469'})
            price = a.find('span', attrs={'class': 'f343d9ce'})
            description = a.find('h2', attrs={'class': 'c0df3811'})
            bedroom = a.find('span', attrs={'aria-label': 'Beds'})
            washroom = a.find('span', attrs={'aria-label': 'Baths'})
            photo_upload = a.find('span', attrs={'class': '_78f72f87'})
            property_size = a.find('span', attrs={'aria-label': 'Area'})
            if name:
                products.append(name.text)
            else:
                products.append(det)
            if price:
                amount = 0
                data2 = price.text.split()
                if data2[1] == 'Crore':
                    amount = float(data2[0]) * 100
                elif data2[1] == 'Lakh':
                    amount = float(data2[0])
                else:
                    amount = float(data2[0]) * 0.1
                prices.append(round(amount, 3))
            else:
                prices.append(det)
            if description:
                descriptions.append(description.text)
            else:
                descriptions.append(det)
            if washroom:
                washrooms.append(washroom.text)
            else:
                washrooms.append(det)
            if bedroom:
                bedrooms.append(bedroom.text)
            else:
                bedrooms.append(det)
            if photo_upload:
                photos_uploads.append(photo_upload.text)
            else:
                photos_uploads.append(det)
            if property_size:
                size = 0
                data1 = property_size.text.split()
                if data1[1] == 'Kanal':
                    size = float(data1[0]) * 20 * 225
                if data1[1] == 'Marla':
                    size = float(data1[0]) * 225
                if data1[1] == 'Sq.':
                    size = float(data1[0]) * 9
                property_sizes.append(size)
            else:
                property_sizes.append(det)
        df = pd.DataFrame(
            {'Property_Type': property_type, 'Purpose': purpose, 'City': city, 'location': products,
             'Price': prices,
             'Description': descriptions,
             'Property Size': property_sizes, 'Bedrooms': bedrooms, 'Washrooms': washrooms,
             'Photos Upload': photos_uploads})
        df.to_csv('Zameen_file(Scraped_data).csv', mode='a', header=False, index=False, encoding='utf-8')
        print(f"Total data extracted: {count1} ")
        write_record_file(f'The data is extracted from city: {ct}, the sates is {pur} and page count is {count}')
        return count1
    except:
        print(f"<<<<<<<<<<    Nothing found and Page {count} and city: {ct} and purpose is : {pur}  >>>>>>>>>>>>>>>>>>")
        write_record_file(f'The data is extracted from city: {ct}, the sates is {pur} and page count is {count}>>>>>>>'
                          f'>>>>>>>>>>>>>>>>>>>>>>')
        return 0


if __name__ == '__main__':
    states = ['Homes', 'Rentals', 'Plots', 'Commercial', 'Rentals', 'Rentals_Plots', 'Rentals_Commercial']
    cities = ['Karachi-2', 'Murree-36', 'Sargodha-778', 'Sialkot-480', 'Taxila-464']
    for x in cities:
        for y in states:
            data = 0
            for z in range(1, 1000):
                print(f"City: {x}, state: {y} and Page Count: {z}")
                val = web_scraping(x, y, z)
                if val == 0:
                    data += 1
                if data == 5:
                    print(f" The loop has been break at city is {x} , states of property is {y} and page number: {z}")
                    break

# cities = ['Lahore-1', 'Karachi-2', 'Islamabad-3', 'Rawalpindi-41', 'Abbottabad-385', 'Attock-1233',
#               'Bahawalnagar-557', 'Chakwal-751', 'Faisalabad-16', 'Gujranwala-327', 'Gujrat-20', 'Gwadar-389',
#               'Hyderabad-30', 'Multan-15', 'Murree-36', 'Sargodha-778', 'Sialkot-480', 'Taxila-464']
