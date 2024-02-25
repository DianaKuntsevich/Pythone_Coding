
from pprint import pprint


import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from DB_client import create_flat_table, insert_flat

URL = 'https://realt.by/sale/flats/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Alt-Used': 'realt.by',
    'Connection': 'keep-alive'
}

PARAM_PATTERN = {
    'Количество комнат': 'rooms',
    'Площадь общая': 'square',
    'Год постройки': 'year',
    'Этаж / этажность': 'floor',
    'Тип дома': 'type_house',
    'Область': 'region',
    'Населенный пункт': 'city',
    'Улица': 'street',
    'Район города': 'district',
    'Координаты': 'coordinates'




}
def get_last_page() -> int:
    response = requests.get(URL, headers=HEADERS)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        pages = soup.find_all('a',
                              class_="focus:outline-none sm:focus:shadow-10bottom cursor-pointer select-none inline-flex font-normal text-body min-h-[2.5rem] min-w-[2.5rem] py-0 items-center !px-1.25 justify-center mx-1 hover:bg-basic-200 rounded-md disabled:text-basic-500",
                              href=True)
        last_page = int(pages[-1].text)
        return last_page
    else:
        print(f'Bad request url : {response.url} | Status: {response.status_code}')


def get_all_links(last_page: int) -> list:
    result = []
    for page in tqdm(range(1, last_page + 1), desc='Url parsing'):
        response = requests.get(f'{URL}?page={page}', headers=HEADERS)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            data = soup.find('div', {'class': 't-0 l-0 absolute w-full'})
            cards = data.find_all('div', {'data-index': True})
            for card in cards:
                try:
                    price = card.find('span',
                                      class_='text-title font-semibold text-basic-900 bg-primary-300 px-1.5 py-0.5 rounded-sm md:px-2').text
                    price = price.replace('р.', '').replace(' ', '').replace('\xa0', '').strip()

                except Exception as e:
                    continue
                # print(price)
                if int(price) > 0:
                    link = card.find('a')['href']
                    # print(link)
                    result.append(f'https://realt.by{link}')
        else:
            print(f'Bad request url : {response.url} | Status: {response.status_code}')
    return result


def get_flat_data(link: str) -> dict | None:
    flat = {
        'rooms': '',
        'square': '',
        'year': '',
        'floor': '',
        'type_house': '',
        'region': '',
        'city': '',
        'street': '',
        'district': '',
        'coordinates': ''
    }

    response = requests.get(link, headers=HEADERS)
    if response.status_code == 200:
        flat['flat_id'] = link.split('/')[-2]
        soup = BeautifulSoup(response.text, 'lxml')
        title = soup.find('h1',
                          class_="order-1 mb-0.5 md:-order-2 md:mb-4 block w-full !inline-block lg:text-h1Lg text-h1 font-raleway font-bold flex items-center").text
        flat['title'] = title
        # print(title)
        try:
            price = soup.find('h2',
                          class_="!inline-block mr-1 lg:text-h2Lg text-h2 font-raleway font-bold flex items-center").text
            price = price.replace('р.', '').replace(' ', '').replace('\xa0', '').strip()
        except Exception as e:
            return
        flat['price'] = int(price)
        # print(price)
        try:
            image = soup.find('img', class_="", alt="", src=True)['src']
        except Exception as e:
            image = ''

        flat['image'] = image
        # print(image)
        try:
            description = soup.find('div',
                                    class_=['description_wrapper__tlUQE']).text
            description = description.replace('\n', '')
        except Exception as e:

            description = ''
        flat['description'] = description
        # print(description)

        params = soup.find_all('li', class_="relative py-1")
        for param in params:
            key = param.find('span').text
            if key not in PARAM_PATTERN:
                continue
            value = param.find(['p', 'a']).text.replace('г. ', '').replace(' м²', '')
            flat[PARAM_PATTERN[key]] = value
    else:
        print(f'Bad request url : {response.url} | Status: {response.status_code}')
    return flat



def run():
    create_flat_table()
    last_page = get_last_page()
    links = get_all_links(1)

    for link in tqdm(links, desc='Parsing data'):
        data = get_flat_data(link)
        pprint(data)
        if data:
            insert_flat(data)



run()




