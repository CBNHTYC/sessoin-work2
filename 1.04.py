import vk
import requests
import json
import time
import copy
import csv

# 53548055

token = '9e74e23a1042a17048a7fe3296cf3b0de33b840ebfdce86c35c4a07e113131dc621681630339610f30375'
session = vk.Session(access_token = token)
api = vk.API(session)
requestTime = 0;


class User:
    ID = ''
    phone = ''
    operator = ''
    groups = ''


operators = {
    'мтс': [918, 978, 988, 989], 'билайн': [903, 905, 906, 909, 960, 961, 962, 963, 964, 965, 966, 967, 968, 969],
    'теле2': [900, 901, 902, 908, 952, 953, 995], 'мегафон': [928, 929, 938, 999]
}

officialGroups = {
    'мтс': 8458649, 'билайн': 26514504, 'теле2': 18098621, 'мегафон': 3785
}


def req ():
    global requestTime
    requestTime += 1
    if requestTime == 3:
        time.sleep(1)
        requestTime = 0


def GetUser (user):
    listOfNubers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    try:
        userId = str(user['id'])
    except:
        userId = str(0)
    try:
        if len(user['mobile_phone']) <= 20:
            strPhone = user['mobile_phone']
            countOfNumbers = 0
            for s in strPhone:
                if s.isdigit():
                    countOfNumbers += 1
            if countOfNumbers >= 10:

                userPhone = str(user['mobile_phone'])
            else:
                userPhone = str(0)
        else:
            userPhone = str(0)
    except:
        userPhone = str(0)

    operator = getOperatorOfUser(userPhone)
    user = {
        'id': userId, 'userPhone': userPhone, 'operator': operator, 'groups': ''
    }
    return user


def WriteCSVFileOfUsers (name, user, create):
    if create is True:
        data = ["ID;phone;operator;groups".split(";")]
        with open(name, 'w', encoding = "utf-8") as file:
            writer = csv.writer(file, delimiter = ';')
            for line in data:
                writer.writerow((line))
    else:
        with open(name, 'a', encoding = "utf-8") as file:
            writer = csv.writer(file, delimiter = ';')
            writer.writerow((user['id'], user['userPhone'], user['operator'], user['groups']))


def getListOfMembers (idOfGroup):  # возвращает не более 25 000 человек за раз. Параметр - строковая переменная.
    '''
    r = requests.post('https://api.vk.com/method/execute.getListOfUsersInGroup?idGroup='+idOfGroup+'&access_token='+token+'&v='+'5.83')
    req()

    a = r.json()
    print(a)
    b = a['response']
    '''
    offset = 0
    request = api.execute.getListOfUsersInGroup(idGroup = idOfGroup, offset = offset, v = 5.73, timeout = 30)
    req()
    b = request['users']
    listOfMembers = []
    for i in b:
        listOfMembers.append(str(i))

    while request['overCount']:
        offset += 25000
        request = api.execute.getListOfUsersInGroup(idGroup = idOfGroup, offset = offset, v = 5.73, timeout = 30)
        req()
        b = request['users']
        for i in b:
            listOfMembers.append(str(i))

    print(len(listOfMembers))
    return (listOfMembers)


def getOperatorOfUser (phone):
    global operators
    action = False
    if phone[0] == '+':
        if phone[1] == '7':
            action = True
    if phone[0] == '7' or phone[0] == '8' or phone[0] == '9' or phone[0] == '(':
        action = True
    if action:
        i = phone.find('9')
        currOper = ''
        if i <= 4:
            currOper = phone[i:i + 3:1]
        for oper in operators:
            for code in operators[oper]:
                if currOper == str(code):
                    return (oper)
        return currOper
    else:
        return 'UnknownOper'


def getInfoOfUsers (listOfUsers):
    localStrOfUsers = ''
    totalCount = len(listOfUsers)
    count = 0
    localListOfUsers = []
    for user in listOfUsers:
        count += 1
        localStrOfUsers = localStrOfUsers + user
        if (count != 1000) and (totalCount - count > 0):
            localStrOfUsers = localStrOfUsers + ','
        else:
            # print(localStrOfUsers)
            tempListOfUsers = api.users.get(user_ids = localStrOfUsers, fields = 'contacts', v = 5.83, timeout = 30)
            req()

            for user in tempListOfUsers:
                localListOfUsers.append(copy.deepcopy(user))
            time.sleep(0.35)
            totalCount -= count
            count = 0
            localStrOfUsers = ''
    return (localListOfUsers)


def getGroupsOfUser (userID):
    global officialGroups
    localOffset = 0
    result = api.execute.getGroups(idUser = userID, offset = localOffset, v = 5.74, timeout = 30)
    req()
    listOfGroups = []
    for group in result['groups']:
        for oGroup in officialGroups:
            if str(group) == str(officialGroups[oGroup]):
                listOfGroups.append(oGroup + ' ' + str(group) + ';')

    while result['overCount'] > 0:
        localOffset += 25000
        result = api.execute.getGroups(idUser = userID, offset = localOffset, v = 5.74, timeout = 30)
        req()
        for group in result['groups']:
            for oGroup in officialGroups:
                if str(group) == str(officialGroups[oGroup]):
                    listOfGroups.append(oGroup + ' ' + str(group) + ';')
    return listOfGroups


def getGroupsOfUsersTwo (listOfUsers):
    global officialGroups
    strOfIDs = ''
    listOfUsersGroups = []
    t = 1
    for i in range(len(listOfUsers)):
        listOfUsersGroups.append(list())
        strOfIDs += str(listOfUsers[i])
        if ((i + 1) % 24) and (i != (len(listOfUsers) - 1)):
            strOfIDs += ','
        if (not (i + 1) % 24) or (i == (len(listOfUsers) - 1)):
            query = api.execute.getGroupsTwo(strOfUsers = strOfIDs, v = 5.74, timeout = 30)
            req()
            strOfIDs = ''
            result = query['list']
            if t == 1:
                t = 2
            for usersGroups in result:
                try:
                    tmpList = []
                    for group in usersGroups:
                        for offGroup in officialGroups:
                            if group == officialGroups[offGroup]:
                                tmpList.append(offGroup + ' ' + str(group) + ';')
                    listOfUsersGroups.append(list(tmpList))
                except:
                    listOfUsersGroups.append(list())
    return listOfUsersGroups


def getWall (ID, offset):
    try:
        return api.wall.get(ogroupID = ID, offset = offset, v = 5.74)
    except Exception as e:
        print(str(e))
        print(';;;')
        error = 'error'
        return error


def getListOfPosts (GROUP, timeRange):
    offset = 0
    listOfPosts = []

    while True:
        wall = getWall(GROUP, offset)
        req()
        if wall != 'error':
            for post in wall:
                if int(post['date']) < timeRange:
                    break
                else:
                    listOfPosts.append(post)
        offset += 2500

    return listOfPosts


def main ():
    WriteCSVFileOfUsers('users.csv', 'Empty', True)
    listOfMembersID = getListOfMembers('33025155')
    listOfUsers = getInfoOfUsers(listOfMembersID)
    listOdUsersGroups = getGroupsOfUsersTwo(listOfMembersID)

    for i in range(len(listOfUsers)):
        DataOfUser = GetUser(listOfUsers[i])
        DataOfUser['groups'] = listOdUsersGroups[i]
        WriteCSVFileOfUsers('users.csv', DataOfUser, False)
    getGroupsOfUsersTwo(listOfMembersID)


main()

# 29270122
# 53548055
