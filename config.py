from datetime import datetime


class DateObject:
    def __init__(self):
        self.year = self.semester = self.courseList = self.emailsSent = self.userList = self.numUsers = ""

    def GetCurrDate(self):
        print("run getdate")
        month = datetime.today().month
        if month > 10:
            self.semester = "spring"
            self.year = str(datetime.today().year + 1)
        else:
            self.semester = "fall"
            self.year = str(datetime.today().year)
        self.courseList = "courseList" + self.semester.title() + self.year
        self.userList = "userList" + self.semester.title() + self.year
        self.emailsSent = "emailsSent" + self.semester.title() + self.year
        self.textsSent = "textsSent" + self.semester.title() + self.year
        self.numUsers = "numUsers" + self.semester.title() + self.year


dateObj = DateObject()
totalEmailsSent = "totalEmailsSent"
totalTextsSent = "totalTextsSent"
totalNumUsers = "totalNumUsers"
