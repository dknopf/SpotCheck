from datetime import datetime


class DateObject:
    def __init__(self):
        self.year = self.semester =self.courseList = self.emailsSent = ""

    def GetCurrDate(self):
        print("run getdate")
        # global year
        # global semester
        month=datetime.today().month
        if month > 9:
            self.semester = "spring"
            self.year = str(datetime.today().year + 1)
        else:
            self.semester = "fall"
            self.year = str(datetime.today().year)
        self.courseList = "courseList" + self.semester.title() + self.year
        self.emailsSent = "emailsSent" + self.semester.title() + self.year


dateObj = DateObject()
totalEmailsSent = "totalEmailsSent"

# def GetDate():
#     print("run getdate")
#     # global year
#     # global semester
#     month=datetime.today().month
#     if month > 9:
#         semester = "spring"
#         year = str(datetime.today().year + 1)
#     else:
#         semester = "fall"
#         year = str(datetime.today().year)
#     return year, semester

# year, semester = GetDate()

# courseList1 = "courseList" + semester.title() + year

# def courseList():
#      return("courseList" + semester.title() + year)
# def emailsSent():
#     return ("emailsSent" + semester.title() + year)