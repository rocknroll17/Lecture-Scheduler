from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
#account.md에 아이디 비밀번호 넣고 작업
with open("account.md",'r') as f:
    account=f.readlines()
for i in range(len(account)):
    account[i] = account[i].strip()
id = account[0]
password = account[1]

lectures = []
seperator = '$'
num = 1

def option_exist(selector):
    try:
        driver.find_element_by_css_selector(selector)
        return True
    except NoSuchElementException:
        return False

chromedriver ='chromedriver.exe'
driver = webdriver.Chrome(chromedriver)
driver.get('https://ocs.cau.ac.kr/index.php?module=xn_commonsi&act=dispXn_commonsiMobileLogin&return_url=https%3A%2F%2Focs.cau.ac.kr%2Findex.php%3Fmodule%3Dxn_sso2013%26act%3DprocXn_sso2013ExternalLoginCallback%26return_url%3Dhttps%253A%252F%252Feclass3.cau.ac.kr%252F%252Flearningx%252Flogin%26from%3Dweb_redirect%26login_type%3Dsso%26sso_only%3Dtrue&auto_login=true&sso_only=true&cvs_lgn=')
res = driver.page_source
soup = BeautifulSoup(res,"html.parser")
time.sleep(1)
driver.find_element(By.ID,'login_user_id').send_keys(id)
driver.find_element(By.ID,'login_user_password').send_keys(password)
driver.find_element(By.ID,'login_user_password').send_keys(Keys.RETURN)

time.sleep(0.5)
driver.switch_to.alert.accept()
driver.get('https://mportal.cau.ac.kr/std/usk/sUskSif001/index.do?type=1')
driver.find_element(By.CSS_SELECTOR, "#sel_year > option:nth-of-type(1)").click()
time.sleep(0.1)
driver.find_element(By.CSS_SELECTOR, "#sel_shtm > option:nth-of-type(3)").click()
time.sleep(0.1)
driver.find_element(By.CSS_SELECTOR, "#sel_course > option:nth-child(1)").click()
time.sleep(0.1)
for i in range(40):
    if i == 0:
        campus = '서울'
    elif i == 1:
        campus = '안성'

    for j in range(40):
        if j == 3:
            continue

        for k in range(40):
            if not driver.find_elements(By.CSS_SELECTOR, f"#sel_camp > option:nth-child({2 + i})"):
                break

            driver.find_element(By.CSS_SELECTOR, f"#sel_camp > option:nth-child({2 + i})").click()
            time.sleep(0.1)

            if not driver.find_elements(By.CSS_SELECTOR, f"#sel_colg > option:nth-child({2 + j})"):
                break

            driver.find_element(By.CSS_SELECTOR, f"#sel_colg > option:nth-child({2 + j})").click()
            time.sleep(0.1)

            if not driver.find_elements(By.CSS_SELECTOR, f"#sel_sust > option:nth-child({2 + k})"):
                break

            driver.find_element(By.CSS_SELECTOR, f"#sel_sust > option:nth-child({2 + k})").click()
            time.sleep(0.1)

            driver.find_element(By.CSS_SELECTOR, ".nb-search-submit button").click()
            time.sleep(5)
            '''try:
                element_present = EC.presence_of_element_located((By.CSS_SELECTOR, '#nbContext > div.nb-contents > div > div.BO_system.nb-q.ng-scope > section.section-gap > div > div > div > div.sp-grid-body > div > div:nth-child(1)'))
                WebDriverWait(driver, 5).until(element_present)#여기 문제 있음
            except:
                continue
            '''
            soup = BeautifulSoup(driver.page_source, "html.parser")
            soup = soup.select_one("#nbContext > div.nb-contents > div > div.BO_system.nb-q.ng-scope > section.section-gap > div > div > div > div.sp-grid-body > div")
            for m in range(700):
                college = soup.select_one(f"div:nth-of-type({1 + m}) > div:nth-of-type(1) > div.sp-grid-data.text-center > span > span")

                if not college:
                    break
                
                college = str(college)
                college = college[120:-7]

                row = soup.select('#nbContext > div.nb-contents > div > div.BO_system.nb-q.ng-scope > section.section-gap > div > div > div > div.sp-grid-body > div > div:nth-child('+str(1+m)+')')
                
                major = row[0].select('div:nth-child(2) > div.sp-grid-data.text-center > span > span')
                major = str(major)             
                major = major[121:-8]

                grade = row[0].select('div:nth-of-type(3) > div.sp-grid-data.text-center > span > span')
                grade = str(grade)
                grade = grade[121:-8]

                course  = row[0].select('div:nth-of-type(4) > div.sp-grid-data.text-center > span > span')
                course = str(course)
                course = course[121:-8]

                category = row[0].select('div:nth-of-type(5) > div.sp-grid-data.text-center > span > span')
                category = str(category)
                category = category[121:-8]

                lecture_number = row[0].select('div:nth-of-type(6) > div.sp-grid-data.text-center > div > span > a')
                lecture_number = str(lecture_number)
                lecture_number = lecture_number[105:-5]

                lecture_name = row[0].select('div:nth-of-type(7) > div.sp-grid-data.text-center > div > span > a')
                lecture_name = str(lecture_name)
                lecture_name = lecture_name[103:-5]

                point = row[0].select('div:nth-of-type(8) > div.sp-grid-data.text-center > span > span')
                point = str(point)
                point = point[121:-8]

                professor = row[0].select('div:nth-of-type(9) > div.sp-grid-data.text-center > div > span > a')                
                professor = str(professor)
                professor = professor[103:-5]

                closed = row[0].select('div:nth-child(10) > div.sp-grid-data.text-center > span > span')
                closed = str(closed)
                closed = closed[121:-8]
                
                

                lecture_time = row[0].select('div:nth-of-type(11) > div.sp-grid-data.text-center > div > span')
                lecture_time = str(lecture_time)
                lecture_time = lecture_time[61:-8]
                if '&amp;' in lecture_time:
                    lecture_time = lecture_time.replace('&amp;','&')
                if '&lt;' in lecture_time:
                    lecture_time = lecture_time.replace('&lt;','<')
                if '&gt;' in lecture_time:
                    lecture_time = lecture_time.replace('&gt;','>')
                if '\xa0' in lecture_time:
                    lecture_time = lecture_time.replace('\xa0', ' ')
                    
                etc = row[0].select('div:nth-of-type(13) > div.sp-grid-data.text-center > span > span')
                etc = str(etc)
                etc = etc[121:-8]
                etc = etc.replace("\n", "")
                lecture=[]
                lecture.append(college)
                lecture.append(major)
                lecture.append(campus)
                lecture.append(grade)
                lecture.append(course)
                lecture.append(category)
                lecture.append(lecture_number)
                lecture.append(lecture_name)
                lecture.append(point)
                lecture.append(professor)
                lecture.append(closed)
                lecture.append(lecture_time)
                lecture.append(etc)

                if lecture not in lectures:
                    lectures.append(lecture)
                    if num %100 == 0:
                        print(str(num)+'개')
                    num += 1
                    #print('추가됨')
                    pass
                else:
                    #print(lecture_number+'겹침')
                    pass
                
driver.quit()
with open('Data/lecture.txt', 'w', encoding='utf-8') as file:
    for i in range(len(lectures)):
        file.write(lectures[i][0]+seperator+lectures[i][1]+seperator+lectures[i][2]+seperator+lectures[i][3]+seperator+lectures[i][4]+seperator+lectures[i][5]+seperator+lectures[i][6]+seperator+lectures[i][7]+seperator+lectures[i][8]+seperator+lectures[i][9]+seperator+lectures[i][10]+seperator+lectures[i][11]+seperator+lectures[i][12]+"\n")
print("done")
