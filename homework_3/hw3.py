import requests
from bs4 import BeautifulSoup
import lxml
import json
from pymongo import MongoClient
import pprint

headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
}
job = input("Введите название вакансии: ")


client = MongoClient("localhost", 27017)
db = client["jobs_database"]
collection = db.jobs


def hh_search():
    i = 0
    while True:
        url = f"https://hh.ru/vacan2cies/{job.strip()}?page={i}"

        r = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")

        vacancy_cards = soup.findAll("div", class_="vacancy-serp-item")
        if vacancy_cards:
            for vacancy in vacancy_cards:
                name = vacancy.find("a", class_="bloko-link").text.strip()
                try:
                    salary = (
                        vacancy.find("div", class_="vacancy-serp-item__sidebar")
                        .find("span")
                        .text.replace("\u202f", "")
                    )
                    if salary[:2] == "до":
                        salary = salary[2:].strip()
                        currency = salary.split(" ")[1]
                        salary_max = int(salary.split(" ")[0])
                        salary_min = None
                    elif salary[:2] == "от":
                        salary = salary[2:].strip()
                        currency = salary.split(" ")[1]
                        salary_max = None
                        salary_min = int(salary.split(" ")[0])
                    else:
                        salary_min = int(salary.split(" – ")[0])
                        salary_max = salary.split(" – ")[1]
                        currency = salary_max.split(" ")[1]
                        salary_max = int(salary_max.split(" ")[0])
                except Exception:
                    salary_min = None
                    salary_max = None
                    currency = None
                url = vacancy.find("a", class_="bloko-link").get("href")
                site = "https://hh.ru/"
                employer = vacancy.find(
                    "div", class_="vacancy-serp-item__meta-info-company"
                ).text.replace("\xa0", " ")
                vacancy_card = {
                    "name": name,
                    "salary_min": salary_min,
                    "salary_max": salary_max,
                    "currency": currency,
                    "url": url,
                    "site": site,
                    "employer": employer,
                }
                if not db.collection.find({"url": vacancy_card["url"]}):
                    db.collection.insert_one(vacancy_card)
                i += 1
        else:
            break


def sj_search():
    i = 0
    while True:
        url = f"https://russia.superjob.ru/vacancy/search/?keywords={job.strip()}&page={i}"

        r = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")

        parent_div = soup.find("div", class_="_3Qutk")
        vacancy_cards = parent_div.findAll("div", class_="f-test-search-result-item")
        if vacancy_cards:
            for vacancy in vacancy_cards:
                try:
                    name = vacancy.find("a", class_="_6AfZ9").text
                except Exception:
                    name = None
                if name is None:
                    pass
                else:
                    salary = vacancy.find("span", class_="_2Wp8I").text.replace(
                        "\xa0", " "
                    )
                    if salary[:2] == "до":
                        salary = salary[2:].strip()
                        currency = salary.split(" ")[2]
                        salary_max = int(salary.split(" ")[0] + salary.split(" ")[1])
                        salary_min = None
                    elif salary[:2] == "от":
                        salary = salary[2:].strip()
                        currency = salary.split(" ")[2]
                        salary_max = None
                        salary_min = int(salary.split(" ")[0] + salary.split(" ")[1])
                    else:
                        try:
                            salary_min = int(salary.split(" — ")[0].replace(" ", ""))
                            salary_max = salary.split(" — ")[1]
                            currency = salary_max.split(" ")[2]
                            salary_max = int(
                                salary_max.split(" ")[0] + salary_max.split(" ")[1]
                            )
                        except Exception:
                            salary_min = None
                            salary_max = None
                            currency = None
                    url = "https://russia.superjob.ru" + vacancy.find(
                        "a", class_="_6AfZ9"
                    ).get("href")
                    site = "https://superjob.ru/"
                    try:
                        employer = vacancy.find("a", class_="_205Zx").text
                    except Exception as e:
                        employer = None
                    vacancy_card = {
                        "name": name,
                        "salary_min": salary_min,
                        "salary_max": salary_max,
                        "currency": currency,
                        "url": url,
                        "site": site,
                        "employer": employer,
                    }
                    if not db.collection.find({"url": vacancy_card["url"]}):
                        db.collection.insert_one(vacancy_card)
                    i += 1
        else:
            break


if __name__ == "__main__":
    hh_search()
    sj_search()
