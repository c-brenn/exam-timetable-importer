import mechanize
import json
from bs4 import BeautifulSoup as bs
import getpass as gp

class ExamImporter:


    def getAuth(self):
        self.__SN = raw_input('Student number: ')
        self.__PW = gp.getpass('Password: ')

        #set up URIs
        self.__TCD_LOGIN_URI = 'https://my.tcd.ie/urd/sits.urd/run/siw_lgn'
        self.__getExamCalendar()


    def __getExamCalendar(self):

        br = mechanize.Browser()

        br.set_handle_robots(False)
        br.set_handle_refresh(False)
        br.set_handle_redirect(True)
        br.open(self.__TCD_LOGIN_URI)
        br.select_form("f")

        username = br.form.find_control("MUA_CODE.DUMMY.MENSYS.1")
        password = br.form.find_control("PASSWORD.DUMMY.MENSYS.1")
        username.value = self.__SN
        password.value = self.__PW

        br.submit()
        br.open(br.click_link(text="here"))
        br.open(br.click_link(text="My Exams"))

        soup = bs(br.response().read())
        td = soup.find_all('td', {'class' :'portallink'})
        a = td[1].contents[0].get('href')
        br.open(a)
        soup = bs(br.response().read())
        
        table = soup.find_all('table', {'class' : 'sitstablegrid'})[1]
        rows =  table.findChildren('tr')

        for row in rows:
            cells = row.findChildren('td')
            if len(cells) >= 4:
                print cells[4].contents
            # exam = self.__parse_exam_info(cells)
            # if not exam == None:
            #     print json.dumps(exam)
        

    def __parse_exam_info(self, cells):
        if len(cells) < 7:
            return None

        exam = {
            'day' : cells[0].string,
            'date': cells[1].string,
            'start_time' : cells[2].string,
            'end_time' : cells[3].string,
            'venue' : cells[4].contents[0].string,
            'exam_title' : cells[5].string + ' ' + cells[6].string
        }
        return exam

imp = ExamImporter()
imp.getAuth()