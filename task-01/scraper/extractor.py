from playwright.sync_api import sync_playwright


def scrape_site(URL):
    print('scrapping starts.....')
    products = []
    with sync_playwright() as p :
        browser = p.chromium.launch(headless=False)
        page =  browser.new_page()
        print('Going to site : ',URL)
        page.goto(URL)

        page.wait_for_selector('.product_pod')
        items = page.locator('.product_pod')
        for i in range(items.count()):
            item = items.nth(i)
            name = item.locator("h3 a").get_attribute("title")
            price = item.locator(".price_color").inner_text()
            instock = item.locator('.availability').inner_text()
            item_detail ={
                'name': name.strip(),
                'price':price.strip(),
                'sku' : instock.strip()
            }
            products.append(item_detail)
        
        browser.close()
        return products
    
# print(scrape_site(URL))