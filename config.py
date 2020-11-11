from datetime import datetime


class DateObject:
    def __init__(self):
        self.year = self.semester =self.courseList = self.emailsSent = ""

    def GetCurrDate(self):
        print("run getdate")
        month=datetime.today().month
        if month > 9:
            self.semester = "spring"
            self.year = str(datetime.today().year + 1)
        else:
            self.semester = "fall"
            self.year = str(datetime.today().year)
        self.courseList = "courseList" + self.semester.title() + self.year
        self.emailsSent = "emailsSent" + self.semester.title() + self.year
        self.textsSent = "textsSent" + self.semester.title() + self.year


dateObj = DateObject()
totalEmailsSent = "totalEmailsSent"
totalTextsSent = "totalTextsSent"
