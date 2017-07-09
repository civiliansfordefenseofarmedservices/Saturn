import grab
import time
import bs4
import random
import sys

def main():
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: {0} [nsfw|sfw] [subreddit name] (start index)\n".format(sys.argv[0]))
        sys.exit(-1)

    nsfwOrNot = sys.argv[1]
    subreddit = sys.argv[2]

    if len(sys.argv) == 3:
        number = 0
    elif len(sys.argv) == 4:
        number = int(sys.argv[3])
    else:
        sys.stderr.write("Usage: {0} [nsfw|sfw] [subreddit name] (start index)\n".format(sys.argv[0]))
        sys.exit(-1)

    numImages = 0

    links = set()

    links.add("http://www.reddit.com/r/{0}".format(subreddit))

    grabObj = grab.Grab()

    while len(links) > 0:
        url = links.pop()

        print("Processing \"{0}\"".format(url))

        while True:
            try:
                resp = grabObj.go(url)
                break
            except BaseException as be:
                print("Got error \"{1}\" with \"{0}\". Retrying.".format(
url, str(be)))
            finally:
                time.sleep(2 + random.randint(1, 20))

        html = bs4.BeautifulSoup(resp.body, "lxml")

        for tag in html.find_all("img"):
            try:
                src = tag["src"]
            except KeyError:
                continue

            if "thumbs.redditmedia.com" in src:
                if "http://" in src:
                    url = "{0}".format(src)
                elif "//" in src:
                    url = "http:{0}".format(src)
                else:
                    url = "http://{0}".format(src)

                if url.endswith(".png"):
                    fileName = "{1}_{0}.png".format(number, nsfwOrNot)
                elif url.endswith(".jpg"):
                    fileName = "{1}_{0}.jpg".format(number, nsfwOrNot)
                else:
                    print("Skipping \"{0}\"".format(url))
                    continue

                print("Downloading \"{0}\"".format(url))
                while True:
                    try:
                        resp2 = grabObj.go(url)
                        break
                    except BaseException as be:
                        print("Got error \"{1}\" with \"{0}\". Retrying.".format(
url, str(be)))
                    finally:
                        time.sleep(2 + random.randint(1, 20))

                print("Downloaded \"{0}\"".format(url))
                with open(fileName, "wb") as imgFile:
                    imgFile.write(resp2.body)
                number += 1
                numImages += 1
                print("{0} images so far.".format(numImages))

        for tag in html.find_all("a"):
            try:
                href = tag["href"]
            except KeyError:
                continue
            if "count" in href and "after" in href and subreddit in href:
                links.add(href)

if __name__ == "__main__":
    main()
