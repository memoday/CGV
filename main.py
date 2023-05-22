from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
import sys, os
import chromedriver_autoinstaller
import subprocess
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

form = resource_path('ui/reserve.ui')
icon = resource_path('assets/ico.ico')
form_class = uic.loadUiType(form)[0]

chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
driver_path = f'./{chrome_ver}/chromedriver.exe'
if os.path.exists(driver_path):
    print(f"chromedriver is installed: {driver_path}")
else:
    print('installing chromedriver')
    chromedriver_autoinstaller.install(cwd=True) #chromedriver 크롬 버전에 맞춰 설치

class Thread1(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.stop_flag = False
    
    def run(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
        options.add_argument('User-Agent= Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36')
        driver = webdriver.Chrome(options=options,executable_path=driver_path)
        print(driver.current_url)
        self.parent.label_main.setText("영화 날짜/시간 선택 중")
        while True:
            try:
                print(driver.current_url)
                iframe = driver.find_element(By.XPATH, '//*[@id="ticket_iframe"]')
                driver.switch_to.frame(iframe)
                break
            except:
                print('iframe 탐색 중')

        while not self.stop_flag:
            try:
                validButton = driver.find_element(By.XPATH,'//*[@id="tnb_step_btn_right"]').get_attribute('class')
                validButton = str(validButton)
                if validButton == 'btn-right on':
                    driver.find_element(By.XPATH,'//*[@id="tnb_step_btn_right"]').click()
                    driver.implicitly_wait(10)
                    Thread1.agreement(self, driver)
                    self.stop_flag= True
                    break
                else:
                    print(f'재시도 합니다. {validButton}')
                    continue

            except Exception as e:
                print(f"재시도 중")
                print(e)
                self.parent.label_main.setText(f"{e}")
                Thread1.selectPeople(self,driver)

    def agreement(self, driver):
        try:
            self.parent.label_main.setText("팝업창 동의 중")
            print(driver.find_element(By.XPATH,'/html/body/div[4]/div[1]/a'))
            driver.find_element(By.XPATH,'/html/body/div[4]/div[1]/a').click()
            print('동의 확인')
            Thread1.selectPeople(self,driver)
        except:
            Thread1.selectPeople(self,driver)

    def selectPeople(self,driver):
        driver.find_element(By.XPATH,'//*[@id="nop_group_adult"]/ul/li[3]/a').click()
        self.stop_flag = False
        self.parent.label_main.setText("좌석 선택 중")

        while not self.stop_flag:
            try:
                validButton = driver.find_element(By.XPATH,'//*[@id="tnb_step_btn_right"]').get_attribute('class')
                validButton = str(validButton)
                if validButton == 'btn-right on':
                    driver.find_element(By.XPATH,'//*[@id="tnb_step_btn_right"]').click()
                    Thread1.payment(self,driver)
                    self.stop_flag= True
                    break
                else:
                    print(f'재시도 합니다. {validButton}')
                    continue

            except Exception as e:
                if "좌석" in e:
                    driver.alert.dismiss()
                else:
                    print(f"재시도 중111")
                    print(e)
                    self.parent.label_main.setText(f"{e}")
    
    def payment(self,driver):
        self.parent.label_main.setText("결제 준비 중")
        driver.find_element(By.XPATH,'//*[@id="last_pay_radio3"]').click()
        time.sleep(0.1)
        javascriptElement = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="tnb_step_btn_right"]')))
        javascriptElement.click()
        # driver.find_element(By.XPATH,'//*[@id="agreementAll"]').click()
        self.parent.label_main.setText("결제 동의 중")
        driver.find_element(By.XPATH,'//*[@id="agreementAll"]').click()
        driver.find_element(By.XPATH,'//*[@id="resvConfirm"]').click()
        driver.find_element(By.XPATH,'/html/body/div[4]/div[3]/a[1]').click()

        self.parent.label_main.setText("결제 중")
        driver.switch_to.window(driver.window_handles[1])
        driver.find_element(By.XPATH,'//*[@id="paymentSheetForm"]/div/div/div[3]/button[1]').click()
        return

    def stop(self):
        self.stop_flag = True
        self.parent.label_main.setText(f"작업을 중단했습니다.")
        return

class WindowClass(QMainWindow, form_class):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        #프로그램 기본설정
        self.setWindowIcon(QIcon(icon))
        self.setWindowTitle('CGV Macro')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMinMaxButtonsHint)

        #버튼 기능
        self.btn_start.clicked.connect(self.main)
        self.btn_off.clicked.connect(self.off)
        self.btn_exit.clicked.connect(self.exit)
        self.btn_chrome.clicked.connect(self.runChrome)

    def main(self):
        global x
        x = Thread1(self)
        x.start()
        self.btn_start.setEnabled(False)

    def runChrome(self):
        try:
            chrome_cmd = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            debugging_port = 9222
            user_data_dir = r"C:/ChromeTEMP"

            cmd = [chrome_cmd, f"--remote-debugging-port={debugging_port}", f"--user-data-dir={user_data_dir}"]

            subprocess.Popen(cmd)
        
        except:
            chrome_cmd = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            debugging_port = 9222
            user_data_dir = r"C:/ChromeTEMP"

            cmd = [chrome_cmd, f"--remote-debugging-port={debugging_port}", f"--user-data-dir={user_data_dir}"]

            subprocess.Popen(cmd)

    def off(self):
        x.stop()
        self.btn_start.setEnabled(True)

    def closeEvent(self, event):
        os.system("taskkill /f /im chromium.exe")
        app.quit()

    def exit(self):
        os.system("taskkill /f /im chromium.exe")
        app.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv) 
    myWindow = WindowClass() 
    myWindow.show()
    app.exec_()