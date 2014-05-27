import requests, sys, re, json

cookie = {}
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36'}

class InvalidUsernamePasswordError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class LoginRequiredError(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def login(username,password):
    global cookie
    loginUrl = 'http://218.94.159.102/GlobalLogin/login.jsp?ReturnURL=http%3A%2F%2F218.94.159.102%2Ftss%2Fen%2Fhome%2FpostSignin.html'
    getCookie = requests.get(loginUrl)
    jsessionid = getCookie.cookies['JSESSIONID']
    if jsessionid == '':
        print("jsessionid fetch failed")
    cookie = {'JSESSIONID':jsessionid}
    payload = {'username':username, 'password':password, 'days':'1', 'Submit':'Login'}
    headers = {'Referer': 'http://218.94.159.102/tss/en/home/signin.html?url=http%3A%2F%2F218.94.159.102%2Ftss%2Fen%2Fhome%2F\index.html', 'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36'}
    r = requests.post('http://218.94.159.102/GlobalLogin/loginservlet', data = payload, cookies=cookie, headers=headers)
    if 'Login Failed' in r.text:
        raise(InvalidUsernamePasswordError('Wrong Username or Password'))
    else:
        jsessionid = r.cookies['JSESSIONID']
        cookie = {'JSESSIONID': jsessionid}
    
def isLogin():
    if not cookie:
        return False
    checkUrl = 'http://218.94.159.102/tss/en/home/myhomework.html'
    r = requests.get(checkUrl, cookies=cookie, headers=headers)
    response = r.text
    return 'access the resource' not in response

def getMyCourse():
    if not isLogin():
        raise(LoginRequiredError("Login is required to get MyCourse, use `login(username,password)` to login"))
    url = 'http://218.94.159.102/tss/en/home/mycourse.html'
    r = requests.get(url, cookies=cookie, headers=headers)
    regex = r'<td align="center">(?P<course_id>c\d+)</td>\s*<td >&nbsp;&nbsp;\s*<a href=".*">\s*(?P<course_name>.+)\s*</a>\s*</td>\s*<td >&nbsp;&nbsp;(?P<teacher>.+)</td>\s*<td >(?P<update_time>[ \d\-:]*)</td>'
    finditer = re.finditer(regex,r.text)
    courselist = []
    for match in finditer:
        course = {}
        course['course_id'] = match.group('course_id')
        course['course_name'] = match.group('course_name')
        course['teacher'] = match.group('teacher')
        course['update_time'] = match.group('update_time')
        courselist.append(course)
    return courselist

def getCourseAnnouncement(courseid):
    courseurl = 'http://218.94.159.102/tss/en/'+courseid+'/announcement/index.html'
    r = requests.get(courseurl,cookies = cookie, headers=headers)
    regex = r'<td width="30%">\s+(?P<announce_date>[\d -:]+)&nbsp;&nbsp;&nbsp;&nbsp;\s+</td>\s+<td width="70%">\s+(?P<announce_title>.+)\s+</td>\s+</tr>\s+<tr>\s+<td colspan="2">\s+(?P<announce_text>((.|\s)(?!</td>))+(.|\s))</td>'
    finditer = re.finditer(regex,r.text)
    announcementlist = []
    for match in finditer:
        announcement = {}
        announcement['announce_date'] = match.group('announce_date')
        announcement['announce_title'] = match.group('announce_title')
        announcement['announce_text'] = match.group('announce_text')
        announcementlist.append(announcement)
    return announcementlist

def getCourseAssignment(courseid):
    courseurl = 'http://218.94.159.102/tss/en/'+courseid+'/assignment/index.html'
    r = requests.get(courseurl, cookies=cookie, headers=headers)
    regex = r'Assignment No:</td>\s+<td width="\d+%"> (?P<assignment_number>\d+)</td>\s+</tr>\s+<tr>\s+<td>Due date:</td>\s+<td>(?P<due_date>[\d\-: ]+)</td>\s+</tr>\s+<tr>\s+<td>Description file: </td>\s+<td>((.|\s)(?!</td>))+(.|\s)</td>\s+</tr>\s+<tr>\s+<td> Description:</td>\s+<td> (?P<description>((.|\s)(?!</td>))*(.|\s))</td>'
    finditer = re.finditer(regex,r.text)
    assignmentlist = []
    for match in finditer:
        assignment = {}
        assignment['assignment_number'] = match.group('assignment_number')
        assignment['due_date'] = match.group('due_date')
        assignment['description'] = match.group('description')
        assignmentlist.append(assignment)
    return assignmentlist
