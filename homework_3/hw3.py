import pymongo
import requests
from bs4 import BeautifulSoup
import lxml
import json
from pymongo import MongoClient
from pprint import pprint
from pymongo.errors import DuplicateKeyError

headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
}
job = input("Введите название вакансии: ")


client = MongoClient("localhost", 27017)
db = client["jobs_database"]


def hh_search():
    hh = db.headhunter
    url = f"https://hh.ru/vacancies/{job.strip()}"
    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    div = soup.find("div", class_="pager")
    last_page = int(div.find_all("span", class_="")[-2].text)
    for i in range(0, last_page):
        url = f"https://hh.ru/vacancies/{job.strip()}?page={i}"

        r = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")

        vacancy_cards = soup.findAll("div", class_="vacancy-serp-item")
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
                "_id": url.split("/")[4].split("?")[0],
                "name": name,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "currency": currency,
                "url": url,
                "site": site,
                "employer": employer,
            }
            try:
                hh.insert_one(vacancy_card)
            except DuplicateKeyError:
                pass


def sj_search():
    sj = db.superjob
    url = f"https://russia.superjob.ru/vacancy/search/?keywords={job.strip()}"
    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    div = str(soup.find("div", class_="_2G0xv L1p51 bwVVU VsleO e495U _2_kCs _3l5cC"))
    last_page = int(div.split('<span class="_1BOkc">')[-2].split("</span>")[0]) + 1
    for i in range(0, last_page):
        url = f"https://russia.superjob.ru/vacancy/search/?keywords={job.strip()}&page={i}"

        r = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")

        parent_div = soup.find("div", class_="_3Qutk")
        vacancy_cards = parent_div.findAll("div", class_="f-test-search-result-item")
        for vacancy in vacancy_cards:
            try:
                name = vacancy.find("a", class_="_6AfZ9").text
            except Exception:
                name = None
            if name is None:
                pass
            else:
                salary = vacancy.find("span", class_="_2Wp8I").text.replace("\xa0", " ")
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
                    "_id": url.split("/")[4].split(".")[0].split("-")[-1],
                    "name": name,
                    "salary_min": salary_min,
                    "salary_max": salary_max,
                    "currency": currency,
                    "url": url,
                    "site": site,
                    "employer": employer,
                }
                try:
                    sj.insert_one(vacancy_card)
                except DuplicateKeyError:
                    pass


if __name__ == "__main__":
    hh_search()
    sj_search()
