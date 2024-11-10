import os
import yaml
import time
from pathlib import Path
import re
import datetime


def content_base_dir():
    return Path("swingscouts-website")


def output_base_dir():
    return Path("output")


def extract_yaml(path):
    with open(path, "rt") as finp:
        indoc = False
        lines = []
        for line in finp:
            if indoc:
                if line == "---\n":
                    break
                else:
                    lines.append(line)
            else:
                if line == "---\n":
                    indoc = True
        buf = "".join(lines)
        doc = yaml.safe_load(buf)
        return doc


def read_events():
    events = []
    d0 = content_base_dir().joinpath("content/events")
    a = os.listdir(d0)
    for e in a:
        m = re.match("\\d{4}-\\d{2}-\\d{2}--\\d{2}:\\d{2}--", e)
        if m is not None:
            ts = datetime.datetime.strptime(m[0], "%Y-%m-%d--%H:%M--")
            # print(ts)
            path = d0.joinpath(e)
            doc = extract_yaml(path)
            doc["ts"] = ts
            events.append(doc)
    return events


def event_to_html(ev):
    bkgimg = ev["image"]
    month = ev["ts"].strftime("%b")
    day = ev["ts"].strftime("%d")
    time = ev["ts"].strftime("%H:%M")
    if "caption" in ev:
        tile_class = "tile-with-date-caption"
        caption = f"""<div class="caption">{ev["caption"]}</div>"""
    else:
        tile_class = "tile-with-date"
        caption = ""
    s = f"""
    <a href="#">
        <div class="cnt-tile {tile_class} tile-bkg-dark" style="background-image: url({bkgimg});">
            <div class="date">
                <div class="date-month">{month}</div>
                <div class="date-day">{day}</div>
                <div class="date-time">{time}</div>
            </div>
            {caption}
        </div>
    </a>
    """
    return s


def build_lessons():
    template = open(content_base_dir().joinpath("templates/page.html"), "rt").read()
    inner = open(content_base_dir().joinpath("kurse.html"), "rt").read()
    s = template.replace("PAGE_CONTENT", inner)
    open(output_base_dir().joinpath("kurse.html"), "wt").write(s)


def build_home():
    events = read_events()
    events = sorted(events, key=lambda x: x["ts"])
    htmls = []
    for ev in events:
        s = event_to_html(ev)
        htmls.append(s)
    template = open(content_base_dir().joinpath("templates/page.html"), "rt").read()
    html = """<div class="grid-tiles">""" + "".join(htmls) + "</div>"
    s = template.replace("PAGE_CONTENT", html)
    open(output_base_dir().joinpath("index.html"), "wt").write(s)


def build():
    build_home()
    build_lessons()


def buildloop():
    while True:
        time.sleep(2.0)
        try:
            build()
        except:
            print("error during build")


if __name__ == "__main__":
    build()
