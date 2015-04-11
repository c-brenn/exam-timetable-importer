import mechanize
import json
from bs4 import BeautifulSoup as bs
import getpass as gp
from datetime import datetime
import requests

class ExamImporter:


    def getAuth(self):
        self.__SN = raw_input('What is your student number? ')
        self.__PW = gp.getpass('What is your my.tcd password? ')

        self.__GOOGLE_EMAIL = raw_input('What is your Google email or username? ')
        self.__GOOGLE_PASSWORD = gp.getpass('What is your Google account password? (If using 2FA, use app specific password.)')

        print 'Wait for a bit pls...'
        #set up URIs
        self.__TCD_LOGIN_URI = 'https://my.tcd.ie/urd/sits.urd/run/siw_lgn'
        self.__GOOGLE_LOGIN_ENDPOINT = 'https://www.google.com/accounts/ClientLogin'
        self.__GOOGLE_CALENDAR_EVENT_ENDPOINT = 'https://www.googleapis.com/calendar/v3/calendars/primary/events'
        # set up google calendar auth and requests
        self.__getGoogleAuthToken()
        self.__request_headers = {
            'Authorization': 'GoogleLogin auth='+self.__GOOGLE_AUTH_TOKEN,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        self.__request_params = {
        "key": "AIzaSyDLt2lWCNKnSyJNz3qB4OJjT0QwB4ExG50"
        }
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

        self.exams = []
        for row in rows:
            cells = row.findChildren('td')
            exam = self.__parse_exam_info(cells)
            if not exam == None:
                self.exams.append(exam)

        self.__addExamsToGoogleCalendar()

    def __addExamsToGoogleCalendar(self):

        time_zone = 'Europe/Dublin'

        for exam in self.exams:


            # get start and end times
            start_time = self.__getRFCTime(exam['date'], exam['start_time'])
            end_time = self.__getRFCTime(exam['date'], exam['end_time'])
            event = {
                'summary' : exam['title'],
                'location': exam['venue'],
                'start' : {
                    'dateTime' : start_time,
                    'timeZone' : time_zone
                },
                'end' : {
                    'dateTime' : end_time,
                    'timeZone' : time_zone
                }
            }
            requests.post(self.__GOOGLE_CALENDAR_EVENT_ENDPOINT, data=json.dumps(event), headers=self.__request_headers, params=self.__request_params)

    def __getRFCTime(self, date, time):
        date_str = str(date) + ' ' + str(time)
        return datetime.strptime(date_str, '%d/%b/%Y %H:%M').isoformat()


    def __parse_exam_info(self, cells):
        if len(cells) < 7:
            return None

        exam = {
            'day' : cells[0].string,
            'date': cells[1].string,
            'start_time' : cells[2].string,
            'end_time' : cells[3].string,
            'venue' : cells[4].contents[1].string,
            'title' : cells[5].string + ' ' + cells[6].string
        }
        return exam

    def __getGoogleAuthToken(self):
        req = requests.post(self.__GOOGLE_LOGIN_ENDPOINT, {
          "accountType": "HOSTED_OR_GOOGLE",
          "Email": self.__GOOGLE_EMAIL,
          "Passwd": self.__GOOGLE_PASSWORD,
          "service": "cl"
        })

        self.__GOOGLE_AUTH_TOKEN = req.text.split("Auth=")[1].replace("\n", "")

imp = ExamImporter()
imp.getAuth()
print 'All done'