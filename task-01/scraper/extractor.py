from playwright.sync_api import sync_playwright

URL = 'https://books.toscrape.com'

def scrape_site(URL):
    print('scrapping starts.....')
    
    with sync_playwright() as p :
        browser = p.chromium.launch(headless=False)
        page =  browser.new_page()
        print('Going to site ...')
        page.goto(URL)

        print('wait for product load...')
        page.wait_for_selector('.product_pod')
        items = page.locator('.product_pod')
        print('printing items .......')
        for i in range(items.count()):
            item = items.nth(i)
            name = item.locator("h3 a").get_attribute("title")
            price = item.locator(".price_color").inner_text()
            print('\n------------------------Item ',i,'---------------------------------')
            print(name)
            print(price)
        
        browser.close()
    
scrape_site(URL)