from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
from PIL import Image


def getChart():
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)

    driver.get(
        'https://www.dextools.io/app/pancakeswap/pair-explorer/0x51fedf8f932eeae9c164a05d00050843b34d75d6')
    driver.fullscreen_window()
    sleep(10)
    driver.find_element_by_xpath(
        '/html/body/app-root/app-chat/div[1]/div[1]/a').click()
    sleep(5)
    element = driver.find_element_by_xpath(
        '/html/body/app-root/div[2]/div/main/app-uniswap/div/app-pairexplorer/app-layout/div/div/div[2]/div[3]')
    sleep(5)
    location = element.location
    size = element.size

    driver.save_screenshot('Images/fullPage.png')

    sleep(5)

    x = location['x']
    y = location['y']
    w = x + size['width']
    h = y + size['height']

    fullImg = Image.open('Images/fullPage.png')
    cropImg = fullImg.crop((x, y, w, h))
    cropImg.save('Images/chart.png')

    driver.close()
    driver.quit()
