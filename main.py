import json
import time
import asyncio
import requests
from lxml import html


def fetch_html_response(url):
    headers = {
        "authority": "gocbocphot.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
                  "application/signed-exchange;v=b3;q=0.9",
        "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
        "cache-control": "max-age=0",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/106.0.0.0 Safari/537.36 "
    }

    response = requests.request("GET", url, headers=headers)

    return response


async def parse_article(response):
    tree = html.fromstring(response.content.decode(response.encoding))
    elements = tree.xpath('//div[@class="col-lg-9"]//div[@class="review_listing"]')
    articles = []
    for element in elements:
        title = "".join(element.xpath('.//h4//text()'))

        url = "".join(element.xpath('.//ul//li[2]//@href'))

        articles.append({
            'title': title,
            'url': url
        })

    return articles


async def parse_article_detail(response):
    tree = html.fromstring(response.content.decode(response.encoding))

    name_shops = tree.xpath('//div[@id="page"]//main//div[@class = "box_general company_info"]//h3//text()')

    name_shop = "".join(name_shops)

    phone_numbers = tree.xpath('//div[@id="page"]//main//div[@class = "row"]//div[@class = "col-12"]//p[1]//text()')

    phone_number = "".join(phone_numbers[1])

    selling_addresses = tree.xpath('//div[@id="page"]//main//div[@class = "row"]//div[@class = "col-12"]//p[2]//text()')

    selling_address = "".join(selling_addresses[1])

    link_shops = tree.xpath('//div[@id="page"]//main//div[@class = "row"]//div[@class = "col-12"]//p[3]//text()')

    link_shop = "".join(link_shops[1])

    return {
        'name_shop': name_shop,
        'phone_number': phone_number,
        'selling_address': selling_address,
        'link_shop': link_shop
    }


start_time = time.time()

if __name__ == '__main__':
    i = 0
    file = open("file1.json", "a+")
    while True:
        i += 1
        url = 'https://gocbocphot.com/tim-kiem-shop-online?trang=', str(i)

        detail_response = fetch_html_response(url="".join(url))
        articles = asyncio.run(parse_article(detail_response))

        data = []
        count = 0
        if not articles:
            break

        for ar in articles:
            shop_response = fetch_html_response(url=ar['url'])
            shop_article = asyncio.run(parse_article_detail(shop_response))
            if not shop_article:
                continue
            text = {"title": ar["title"], "post link": ar["url"], "name_shop": shop_article["name_shop"],
                    "phone_number": shop_article["phone_number"], "selling_address": shop_article["selling_address"],
                    "link_shop": shop_article["link_shop"]}

            file.write(json.dumps(text) + '\n')

    file.close()
end_time = time.time()

elapsed_time = end_time - start_time
print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
