from tkinter import *
from selenium import webdriver
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException, UnexpectedAlertPresentException, NoAlertPresentException
from random import randint
import time
import os
import sys
import pygame

# PyInstaller로 패킹할 때 파일 경로 설정
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def play_sound(file_path):
    pygame.mixer.init()
    sound = pygame.mixer.Sound(file_path)
    sound.play()

# EdgeDriver를 자동으로 다운로드하고 설정
def open_browser():
    service = Service(EdgeChromiumDriverManager().install())
    options = webdriver.EdgeOptions()
    driver = webdriver.Edge(service=service, options=options)

    # 엣지 드라이버 버전 출력
    driver_version = driver.capabilities['browserVersion']
    log_message(f"엣지 드라이버 버전: {driver_version}")
    return driver

def login(driver, login_id, login_psw):
    driver.get('https://etk.srail.co.kr/cmc/01/selectLoginForm.do')
    driver.implicitly_wait(15)
    driver.find_element(By.ID, 'srchDvNm01').send_keys(str(login_id))
    driver.find_element(By.ID, 'hmpgPwdCphd01').send_keys(str(login_psw))
    driver.find_element(By.XPATH, '//*[@id="login-form"]/fieldset/div[1]/div[1]/div[2]/div/div[2]/input').click()
    driver.implicitly_wait(5)
    return driver

def log_message(message):
    text_log.insert(END, message + "\n")
    text_log.see(END)
    root.update()  # 즉시 GUI 업데이트

def search_train(driver, dpt_stn, arr_stn, dpt_dt, dpt_tm, num_trains_to_check=2):
    is_booked = False
    cnt_refresh = 0

    try:
        driver.get('https://etk.srail.kr/hpg/hra/01/selectScheduleList.do')
        driver.implicitly_wait(5)
        
        # 출발지, 도착지, 날짜, 시간 입력
        elm_dpt_stn = driver.find_element(By.ID, 'dptRsStnCdNm')
        elm_dpt_stn.clear()
        elm_dpt_stn.send_keys(dpt_stn)
        
        elm_arr_stn = driver.find_element(By.ID, 'arvRsStnCdNm')
        elm_arr_stn.clear()
        elm_arr_stn.send_keys(arr_stn)
        
        elm_dptDt = driver.find_element(By.ID, "dptDt")
        driver.execute_script("arguments[0].setAttribute('style','display: True;')", elm_dptDt)
        Select(driver.find_element(By.ID, "dptDt")).select_by_value(dpt_dt)
        
        elm_dptTm = driver.find_element(By.ID, "dptTm")
        driver.execute_script("arguments[0].setAttribute('style','display: True;')", elm_dptTm)
        Select(driver.find_element(By.ID, "dptTm")).select_by_visible_text(dpt_tm)

        log_message("기차를 조회합니다")
        
        driver.find_element(By.XPATH, "//input[@value='조회하기']").click()
        driver.implicitly_wait(5)
        time.sleep(3)

        while True:
            try:
                # 예약 가능한 기차 확인 루프
                for i in range(num_trains_to_check, num_trains_to_check+1):
                    standard_seat = driver.find_element(By.CSS_SELECTOR, f"#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr:nth-child({i}) > td:nth-child(7)").text
                    reservation = driver.find_element(By.CSS_SELECTOR, f"#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr:nth-child({i}) > td:nth-child(8)").text

                    if "예약하기" in standard_seat:
                        log_message("예약 가능 클릭")
                        driver.find_element(By.CSS_SELECTOR, f"#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr:nth-child({i}) > td:nth-child(7) > a.btn_burgundy_dark").click()
                        driver.implicitly_wait(3)
                        if driver.find_elements(By.ID, 'isFalseGotoMain'):
                            is_booked = True
                            log_message("예약 성공")
                            play_sound(resource_path('success_sound.wav'))
                            break
                        else:
                            log_message("잔여석 없음. 다시 검색")
                            driver.back()
                            driver.implicitly_wait(5)
            except StaleElementReferenceException:
                log_message("StaleElementReferenceException 발생 - 요소를 다시 찾습니다.")
                continue  # 요소를 새로고침하여 다시 검색

            if not is_booked:
                time.sleep(randint(2, 4))
                submit = driver.find_element(By.XPATH, "//input[@value='조회하기']")
                driver.execute_script("arguments[0].click();", submit)
                cnt_refresh += 1
                log_message(f"새로고침 {cnt_refresh}회")
                driver.implicitly_wait(10)
                time.sleep(0.5)
            else:
                break
    except WebDriverException:
        log_message("WebDriver 연결이 끊어졌습니다. 브라우저를 다시 엽니다.")
        driver.quit()
        driver = open_browser()
        driver = login(driver, entry_login_id.get(), entry_login_psw.get())
        search_train(driver, dpt_stn, arr_stn, dpt_dt, dpt_tm, num_trains_to_check)
    return driver

def start_search():
    login_id = entry_login_id.get()
    login_psw = entry_login_psw.get()
    dpt_stn = entry_dpt_stn.get()
    arr_stn = entry_arr_stn.get()
    dpt_dt = entry_dpt_dt.get()
    dpt_tm = entry_dpt_tm.get()
    num_trains_to_check = int(entry_num_trains_to_check.get())

    driver = open_browser()
    driver = login(driver, login_id, login_psw)
    search_train(driver, dpt_stn, arr_stn, dpt_dt, dpt_tm, num_trains_to_check)

if __name__ == "__main__":
    root = Tk()
    root.title("SRT 매크로")

    Label(root, text="회원번호:").grid(row=0, column=0)
    entry_login_id = Entry(root)
    entry_login_id.grid(row=0, column=1)

    Label(root, text="비밀번호:").grid(row=1, column=0)
    entry_login_psw = Entry(root)
    entry_login_psw.grid(row=1, column=1)

    Label(root, text="출발지:").grid(row=2, column=0)
    entry_dpt_stn = Entry(root)
    entry_dpt_stn.grid(row=2, column=1)

    Label(root, text="도착지:").grid(row=3, column=0)
    entry_arr_stn = Entry(root)
    entry_arr_stn.grid(row=3, column=1)

    Label(root, text="출발 날짜 (YYYYMMDD):").grid(row=4, column=0)
    entry_dpt_dt = Entry(root)
    entry_dpt_dt.grid(row=4, column=1)

    Label(root, text="출발 시간 (짝수 시간, 예: 08):").grid(row=5, column=0)
    entry_dpt_tm = Entry(root)
    entry_dpt_tm.grid(row=5, column=1)

    Label(root, text="검색 상위 몇 번째 기차를 예매할지 입력하세요:").grid(row=6, column=0)
    entry_num_trains_to_check = Entry(root)
    entry_num_trains_to_check.grid(row=6, column=1)

    Button(root, text="검색 시작", command=start_search).grid(row=8, columnspan=2)

    text_log = Text(root, height=10, width=50)
    text_log.grid(row=9, columnspan=2)

    Label(root, text="spread-one").grid(row=10, columnspan=2)
    root.mainloop()
