# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests


class SdamGIA:
    def __init__(self, exam="ege"):
        """
        :param exam: 'ege' или 'oge'
        """
        self.exam = exam.lower()
        self._BASE_DOMAIN = "sdamgia.ru"

        self._SUBJECT_BASE_URL = {
            "math": f"https://math-{self.exam}.{self._BASE_DOMAIN}",
            "mathb": f"https://mathb-{self.exam}.{self._BASE_DOMAIN}",
            "phys": f"https://phys-{self.exam}.{self._BASE_DOMAIN}",
            "inf": f"https://inf-{self.exam}.{self._BASE_DOMAIN}",
            "rus": f"https://rus-{self.exam}.{self._BASE_DOMAIN}",
            "bio": f"https://bio-{self.exam}.{self._BASE_DOMAIN}",
            "chem": f"https://chem-{self.exam}.{self._BASE_DOMAIN}",
            "geo": f"https://geo-{self.exam}.{self._BASE_DOMAIN}",
            "soc": f"https://soc-{self.exam}.{self._BASE_DOMAIN}",
            "hist": f"https://hist-{self.exam}.{self._BASE_DOMAIN}",
            "en": f"https://en-{self.exam}.{self._BASE_DOMAIN}",
            "de": f"https://de-{self.exam}.{self._BASE_DOMAIN}",
            "fr": f"https://fr-{self.exam}.{self._BASE_DOMAIN}",
            "lit": f"https://lit-{self.exam}.{self._BASE_DOMAIN}",
        }

    def _get_base(self, subject):
        """Проверка и возврат правильной ссылки для предмета"""
        if subject not in self._SUBJECT_BASE_URL:
            raise ValueError(f"Неверный предмет '{subject}' для {self.exam.upper()}")
        return self._SUBJECT_BASE_URL[subject]

    def get_problem_by_id(
        self,
        subject,
        id,
        img=None,
        path_to_img=None,
        path_to_html="",
        grabzit_auth=None,
    ):
        base_url = self._get_base(subject)
        page = requests.get(f"{base_url}/problem?id={id}")
        soup = BeautifulSoup(page.content, "html.parser")

        probBlock = soup.find("div", {"class": "prob_maindiv"})
        if probBlock is None:
            return None

        for i in probBlock.find_all("img"):
            if not "sdamgia.ru" in i["src"]:
                i["src"] = base_url + i["src"]

        URL = f"{base_url}/problem?id={id}"
        try:
            TOPIC_ID = " ".join(
                probBlock.find("span", {"class": "prob_nums"}).text.split()[1:][:-2]
            )
        except Exception:
            TOPIC_ID = ""

        CONDITION, SOLUTION, ANSWER, ANALOGS = {}, {}, "", []

        try:
            CONDITION = {
                "text": probBlock.find_all("div", {"class": "pbody"})[0].text,
                "images": [
                    i["src"]
                    for i in probBlock.find_all("div", {"class": "pbody"})[0].find_all(
                        "img"
                    )
                ],
            }
        except Exception:
            pass

        try:
            SOLUTION = {
                "text": probBlock.find_all("div", {"class": "pbody"})[1].text,
                "images": [
                    i["src"]
                    for i in probBlock.find_all("div", {"class": "pbody"})[1].find_all(
                        "img"
                    )
                ],
            }
        except Exception:
            pass

        try:
            ANSWER = probBlock.find("div", {"class": "answer"}).text.replace(
                "Ответ: ", ""
            )
        except Exception:
            pass

        try:
            ANALOGS = [
                i.text for i in probBlock.find("div", {"class": "minor"}).find_all("a")
            ]
            if "Все" in ANALOGS:
                ANALOGS.remove("Все")
        except Exception:
            pass

        return {
            "id": id,
            "topic": TOPIC_ID,
            "condition": CONDITION,
            "solution": SOLUTION,
            "answer": ANSWER,
            "analogs": ANALOGS,
            "url": URL,
        }

    def search(self, subject, request, page=1):
        """
        Поиск задач по запросу

        :param subject: Наименование предмета
        :type subject: str

        :param request: Запрос
        :type request: str

        :param page: Номер страницы поиска
        :type page: int
        """
        doujin_page = requests.get(
            f"{self._SUBJECT_BASE_URL[subject]}/search?search={request}&page={str(page)}"
        )
        soup = BeautifulSoup(doujin_page.content, "html.parser")
        return [
            i.text.split()[-1] for i in soup.find_all("span", {"class": "prob_nums"})
        ]

    def get_test_by_id(self, subject, testid):
        """
        Получение списка задач, включенных в тест

        :param subject: Наименование предмета
        :type subject: str

        :param testid: Идентификатор теста
        :type testid: str
        """
        doujin_page = requests.get(
            f"{self._SUBJECT_BASE_URL[subject]}/test?id={testid}"
        )
        soup = BeautifulSoup(doujin_page.content, "html.parser")
        return [
            i.text.split()[-1] for i in soup.find_all("span", {"class": "prob_nums"})
        ]

    def get_category_by_id(self, subject, categoryid, page=1):
        """
        Получение списка задач, включенных в категорию

        :param subject: Наименование предмета
        :type subject: str

        :param categoryid: Идентификатор категории
        :type categoryid: str

        :param page: Номер страницы поиска
        :type page: int
        """

        doujin_page = requests.get(
            f"{self._SUBJECT_BASE_URL[subject]}/test?&filter=all&theme={categoryid}&page={page}"
        )
        soup = BeautifulSoup(doujin_page.content, "html.parser")
        return [
            i.text.split()[-1] for i in soup.find_all("span", {"class": "prob_nums"})
        ]

    def get_catalog(self, subject):
        """
        Получение каталога заданий для определенного предмета

        :param subject: Наименование предмета
        :type subject: str
        """

        doujin_page = requests.get(f"{self._SUBJECT_BASE_URL[subject]}/prob_catalog")
        soup = BeautifulSoup(doujin_page.content, "html.parser")
        catalog = []
        CATALOG = []

        for i in soup.find_all("div", {"class": "cat_category"}):
            try:
                i["data-id"]
            except:
                catalog.append(i)

        for topic in catalog[1:]:
            TOPIC_NAME = topic.find("b", {"class": "cat_name"}).text.split(". ")[1]
            TOPIC_ID = topic.find("b", {"class": "cat_name"}).text.split(". ")[0]
            if TOPIC_ID[0] == " ":
                TOPIC_ID = TOPIC_ID[2:]
            if TOPIC_ID.find("Задания ") == 0:
                TOPIC_ID = TOPIC_ID.replace("Задания ", "")

            CATALOG.append(
                dict(
                    topic_id=TOPIC_ID,
                    topic_name=TOPIC_NAME,
                    categories=[
                        dict(
                            category_id=i["data-id"],
                            category_name=i.find("a", {"class": "cat_name"}).text,
                        )
                        for i in topic.find("div", {"class": "cat_children"}).find_all(
                            "div", {"class": "cat_category"}
                        )
                    ],
                )
            )

        return CATALOG

    def generate_test(self, subject, problems=None):
        """
        Генерирует тест по заданным параметрам

        :param subject: Наименование предмета
        :type subject: str

        :param problems: Список заданий
        По умолчанию генерируется тест, включающий по одной задаче из каждого задания предмета.
        Так же можно вручную указать одинаковое количество задач для каждого из заданий: {'full': <кол-во задач>}
        Указать определенные задания с определенным количеством задач для каждого: {<номер задания>: <кол-во задач>, ... }
        :type problems: dict
        """

        if problems is None:
            problems = {"full": 1}

        if "full" in problems:
            dif = {
                f"prob{i}": problems["full"]
                for i in range(1, len(self.get_catalog(subject)) + 1)
            }
        else:
            dif = {f"prob{i}": problems[i] for i in problems}

        return (
            requests.get(
                f"{self._SUBJECT_BASE_URL[subject]}/test?a=generate",
                dif,
                allow_redirects=False,
            )
            .headers["location"]
            .split("id=")[1]
            .split("&nt")[0]
        )

    def generate_pdf(
        self,
        subject,
        testid,
        solution="",
        nums="",
        answers="",
        key="",
        crit="",
        instruction="",
        col="",
        pdf=True,
    ):
        """
        Генерирует pdf версию теста

        :param subject: Наименование предмета
        :type subject: str

        :param testid: Идентифигатор теста
        :type testid: str

        :param solution: Пояснение
        :type solution: bool

        :param nums: № заданий
        :type nums: bool

        :param answers: Ответы
        :type answers: bool

        :param key: Ключ
        :type key: bool

        :param crit: Критерии
        :type crit: bool

        :param instruction: Инструкция
        :type instruction: bool

        :param col: Нижний колонтитул
        :type col: str

        :param pdf: Версия генерируемого pdf документа
        По умолчанию генерируется стандартная вертикальная версия
        h - горизонтальная версия
        z - версия с крупным шрифтом
        m - версия с большим полем
        :type pdf: str

        """

        def a(a):
            if a == False:
                return ""
            return a

        return (
            self._SUBJECT_BASE_URL[subject]
            + requests.get(
                f"{self._SUBJECT_BASE_URL[subject]}/test?"
                f"id={testid}&print=true&pdf={pdf}&sol={a(solution)}&num={a(nums)}&ans={a(answers)}"
                f"&key={a(key)}&crit={a(crit)}&pre={a(instruction)}&dcol={a(col)}",
                allow_redirects=False,
            ).headers["location"]
        )


if __name__ == "__main__":
    sdamgia = SdamGIA()
