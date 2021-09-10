import requests
import re
from bs4 import BeautifulSoup as bs
import urllib.parse
import os.path
import pandas as pd
import tqdm


regex_enrolled = re.compile(r"\d+ student")
semesters_links = {"LS2015":
                   "http://geraldine.fjfi.cvut.cz/WORK/Anketa/LS2015/67_pub/courses/",
                   "ZS2015":
                   "http://geraldine.fjfi.cvut.cz/WORK/Anketa/ZS2015/67_pub/courses/",
                   "LS2016":
                   "http://geraldine.fjfi.cvut.cz/WORK/Anketa/LS2016/67_pub/courses/",
                   "ZS2016":
                   "http://geraldine.fjfi.cvut.cz/WORK/Anketa/ZS2016/67/public/cs/courses/",
                   "LS2017":
                   "http://geraldine.fjfi.cvut.cz/WORK/Anketa/LS2017/predmety/courses/",
                   "ZS2017":
                   "http://geraldine.fjfi.cvut.cz/WORK/Anketa/ZS2017/67/public/cs/courses/",
                   "LS2018":
                   "http://geraldine.fjfi.cvut.cz/WORK/Anketa/LS2018/predmety/cs/courses/",
                   "ZS2018":
                   "http://geraldine.fjfi.cvut.cz/WORK/Anketa/ZS2018/public/cs/courses/"}


def get_courses_links(semester):
    page = requests.get(semesters_links[semester] + "index.html")
    soup = bs(page.content, "html.parser")
    divs = soup.find_all("div", {"class": "my-list-item"})
    links = [div.findChildren("a", recursive=False) for div in divs]
    links = [item for sublist in links for item in sublist]
    return links


def get_course_stats(link):
    page = requests.get(link)
    counts = regex_enrolled.findall(page.text)
    counts = [int(count.split(" ")[0]) for count in counts]
    return counts[:2]


def get_courses_stats(semester):
    links = get_courses_links(semester)
    courses_stats = []
    for link in tqdm.tqdm(links):
        full_link = urllib.parse.urljoin(semesters_links[semester], link["href"])
        course_stats = get_course_stats(full_link)
        courses_stats.append([link.text.replace("\xa0", " "), course_stats[0],
                              course_stats[1]])

    return courses_stats


def load_semester_data(semester):
    if not os.path.isfile(semester + ".csv"):
        courses_stats = get_courses_stats(semester)
        df = pd.DataFrame.from_records(courses_stats, columns=["name",
                                                               "enrolled",
                                                               "passed"])
        df.to_csv(semester + ".csv")
    else:
        df = pd.read_csv(semester + ".csv", usecols=["name", "enrolled", "passed"])
    df["pass rate"] = round(df["passed"] / df["enrolled"] * 100, 2)
    df["semester"] = semester
    return df


if __name__ == "__main__":
    semesters = ["LS2015", "ZS2015", "LS2016", "ZS2016", "LS2017", "ZS2017",
                 "LS2018", "ZS2018"]
    frames = [load_semester_data(semester) for semester in semesters]
    df = pd.concat(frames)
    print(df)
