from os import mkdir
from time import sleep
import requests
from bs4 import BeautifulSoup as BS

HEADERS = {"User-Agent": "Mozilla/5.0"}

URL = "https://www.livelib.ru/reviews/"
LEAST_NUM_OF_MARKS = 1000
MAX_NUM_OF_REQUESTS = 9000



class Comment:
    def __init__(self, name, comment, mark):
        if name != "":
            self.name = name
        if name is None:
            print("Некорректное название")
            exit()
        if comment is None:
            print("Некоррректное содержимое комментария")
            exit()
        self.comment = comment
        if mark <= 5 and mark >= 0:
            self.mark = mark

    def get_mark(self):
        return self.mark

    def get_name(self):
        return self.name

    def get_comment(self):
        return self.comment


def create_repo():
    mkdir("dataset")
    for i in range(1, 6):
        mkdir("dataset/" + str(i))


def get_page(URL):
    try:
        r = requests.get(URL, HEADERS=HEADERS)
        sleep(2)
        if r.status_code == 200:
            return BS(r.content, "html.parser")
        else:
            print("Page not found")
            exit()
    except:
        print("Ошибка соединения")
        return -1


def get_marks(articles):
    marks = list()
    for article in articles:
        try:
            lenta_card = article.find("div", class_="lenta-card")
            h3 = lenta_card.find("h3", class_="lenta-card__title")
            mark = h3.find("span", class_="lenta-card__mymark").text.strip()
            marks.append(mark)
        except AttributeError as e:
            print("Не найдена оценка")
            return -1
    return marks


def get_names(articles):
    names = list()
    for article in articles:
        try:
            lenta_card = article.find("div", class_="lenta-card")
            lenta_card_book_wrapper = lenta_card.find(
                "div", class_="lenta-card-book__wrapper"
            )
            name = lenta_card_book_wrapper.find(
                "a", class_="lenta-card__book-title"
            ).text.strip()
            names.append(name)
        except AttributeError as e:
            print("Не найдено название")
            return -1
    return names


def get_comments_texts(articles):
    comments_texts = list()
    for article in articles:
        try:
            lenta_card = article.find("div", class_="lenta-card")
            text_without_readmore = lenta_card.find(
                "div", class_="lenta-card__text without-readmore"
            )
            comment = text_without_readmore.find(
                id="lenta-card__text-review-escaped"
            ).text
            comments_texts.append(comment)
        except AttributeError as e:
            print("Не найден комментарий")
            return -1

    return comments_texts


def save_comments(data, filename):
    for i in range(0, len(data)):
        file = open(filename + f"\\{(i+1):04}" + ".txt", "w", encoding="utf-8")
        file.write(data[i].get_name())
        file.write("\n\n\n")
        file.write(data[i].get_comment())
        file.close


def parse_pages(MAX_NUM_OF_REQUESTS, LEAST_NUM_OF_MARKS):
    dataset = list()
    one = 0
    two = 0
    three = 0
    four = 0
    five = 0
    my_key = "Пожалуйста, подождите пару секунд,"
    " идет перенаправление на сайт..."
    for i in range(1, MAX_NUM_OF_REQUESTS):
        print(f"Страница: {i}")
        soup = get_page(URL + "~" + str(i) + "#reviews")
        if soup == -1:
            continue
        if (
            soup.find("h1").text
            == my_key
        ):
            print("Вылезла капча")
            sleep(10)
            continue
        try:
            articles = (
                soup.find("main", class_="main-body page-content")
                .find("section", class_="lenta__content")
                .find_all("article", class_="review-card lenta__item")
            )
        except AttributeError as e:
            print('Не удалось загрузить страницу')
            continue

        marks = get_marks(articles)
        if marks == -1:
            continue
        names = get_names(articles)
        if names == -1:
            continue
        comments_texts = get_comments_texts(articles)
        if comments_texts == -1:
            continue
        for j in range(len(marks)):
            condidate = Comment(names[j], comments_texts[j], float(marks[j]))
            if condidate.mark < 2.0:
                one += 1
            elif condidate.mark < 3.0:
                two += 1
            elif condidate.mark < 4.0:
                three += 1
            elif condidate.mark < 5.0:
                four += 1
            elif condidate.mark == 5.0:
                five += 1
            dataset.append(condidate)
        print(
            f"One={
                one}, Two={two}, three={three}, Four={four}, Five={five}"
        )
        if (
            one >= LEAST_NUM_OF_MARKS
            and two >= LEAST_NUM_OF_MARKS
            and three >= LEAST_NUM_OF_MARKS
            and four >= LEAST_NUM_OF_MARKS
            and five >= LEAST_NUM_OF_MARKS
        ):
            i = MAX_NUM_OF_REQUESTS
            break
    return dataset


if __name__ == "__main__":
    dataset = parse_pages(MAX_NUM_OF_REQUESTS, LEAST_NUM_OF_MARKS)
    create_repo()
    # dataset.sort(key = lambda comment: comment.mark)
    one_data = [el for el in dataset if el.get_mark() < 2.0]
    save_comments(one_data, "dataset\\1")
    two_data = [
        el for el in dataset if el.get_mark() < 3.0 and el.get_mark() >= 2.0]
    save_comments(two_data, "dataset\\2")
    three_data = [
        el for el in dataset if el.get_mark() < 4.0 and el.get_mark() >= 3.0]
    save_comments(three_data, "dataset\\3")
    four_data = [
        el for el in dataset if el.get_mark() < 5.0 and el.get_mark() >= 4.0]
    save_comments(four_data, "dataset\\4")
    five_data = [el for el in dataset if el.get_mark() == 5.0]
    save_comments(five_data, "dataset\\5")
    print("Работа окончена")
