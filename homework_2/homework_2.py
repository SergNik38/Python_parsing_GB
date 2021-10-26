import requests
from bs4 import BeautifulSoup
import lxml
import json

headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
           }
job = input('Введите название вакансии: ')
pages = int(input('Введите количество страниц поиска: '))

result = []


def hh_search():
    for i in range(0, pages):
        url = f'https://hh.ru/vacancies/{job.strip()}?page={i}'

        r = requests.get(url=url, headers=headers)

        soup = BeautifulSoup(r.text, 'lxml')

        vacancy_cards = soup.findAll('div', class_='vacancy-serp-item')
        for vacancy in vacancy_cards:
            name = vacancy.find('a', class_='bloko-link').text.strip()
            try:
                salary = vacancy.find('div', class_='vacancy-serp-item__sidebar') \
                    .find('span').text.replace(u'\u202f', '')
            except Exception:
                salary = 'Не указана'
            url = vacancy.find('a', class_='bloko-link').get('href')
            site = 'https://hh.ru/'
            employer = vacancy.find('div', class_='vacancy-serp-item__meta-info-company') \
                .text.replace(u'\xa0', ' ')
            vacancy_card = {
                'name': name,
                'salary': salary,
                'url': url,
                'site': site,
                'employer': employer
            }
            result.append(vacancy_card)


def sj_search():
    for i in range(0, pages):
        url = f'https://russia.superjob.ru/vacancy/search/?keywords={job.strip()}&page={i}'

        r = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')

        parent_div = soup.find('div', class_='_3Qutk')
        vacancy_cards = parent_div.findAll('div', class_='f-test-search-result-item')
        for vacancy in vacancy_cards:
            try:
                name = vacancy.find('a', class_='_6AfZ9').text
            except Exception:
                name = None
            if name is None:
                pass
            else:
                try:
                    salary = vacancy.find('span', class_='_2Wp8I').text.replace(u'\xa0', '')
                except Exception:
                    salary = 'По договоренности'
                url = 'https://russia.superjob.ru' + vacancy.find('a', class_='_6AfZ9').get('href')
                site = 'https://superjob.ru/'
                employer = vacancy.find('a', class_='_205Zx').text
                vacancy_card = {
                    'name': name,
                    'salary': salary,
                    'url': url,
                    'site': site,
                    'employer': employer
                }
                result.append(vacancy_card)


if __name__ == '__main__':
    hh_search()
    sj_search()
    with open('result.json', 'w') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
