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

listOfOfficialGaroups = [8458649,26514504,18098621,3785]

isSetGroupOperator = {
	'мтс' : 0, 'билайн': 0,
	'теле2': 0, 'мегафон': 0
}

globalIDForFindUsersList = ''

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
		'id': userId, 'userPhone': userPhone, 'operator': operator, 'groups': '', 'lTele2' : '', 'lMTS' : '',
		'lMegafon' : '', 'lBeeline' : '', 'rTele2' : '', 'rMTS' : '', 'rMegafon' : '', 'rBeeline' : '',
		'fTele2' : '', 'fMTS' : '', 'fMegafon' : '', 'fBeeline' : ''
	}
	return user


def WriteCSVFileOfUsers (name, user, create):
	if create is True:
		data = ["ID;phone;operator;groups;lTele2;rTele2;lMTS;rMTS;lMegafon;rMegafon;lBeeline;rBeeline;fTele2;fMTS;fMegafon;fBeeline".split(";")]
		with open(name, 'w', encoding = "utf-8") as file:
			writer = csv.writer(file, delimiter = ';')
			for line in data:
				writer.writerow((line))
	else:
		with open(name, 'a', encoding = "utf-8") as file:
			writer = csv.writer(file, delimiter = ';')
			writer.writerow((user['id'], user['userPhone'], user['operator'], user['groups'], user['lTele2'], user['rTele2'], user['lMTS'], user['rMTS'], user['lMegafon'], user['rMegafon'], user['lBeeline'], user['rBeeline'], user['fTele2'], user['fMTS'], user['fMegafon'], user['fBeeline']))


def getListOfMembers (idOfGroup):
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

			for user1 in tempListOfUsers:
				localListOfUsers.append(copy.deepcopy(user1))
			time.sleep(0.35)
			totalCount -= count
			count = 0
			localStrOfUsers = ''
	return (localListOfUsers)


def getGroupsOfUser (userID):
	global officialGroups, isSetGroupOperator
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
					isSetGroupOperator[oGroup] = 1
					listOfGroups.append(oGroup + ' ' + str(group) + ';')
	return listOfGroups

def isContainOffGroup (listOfGroupsID):
	global listOfOfficialGaroups

	offGrousp = set(listOfOfficialGaroups)
	userGroups = set(listOfGroupsID)
	isContain = offGrousp & userGroups
	if len(isContain) == 0:
		return False
	else:
		return True

def getGroupsOfUsersTwo (listOfUsers):
	global officialGroups, isSetGroupOperator, listOfOfficialGaroups
	setOfOffGroups = set(listOfOfficialGaroups)
	strOfIDs = ''
	listOfUsersGroups = []
	checkOffGroup = True
	for i in range(len(listOfUsers)):
		strOfIDs += str(listOfUsers[i])
		if ((i + 1) % 25) and (i != (len(listOfUsers) - 1)):
			strOfIDs += ','
		if (not (i + 1) % 25) or (i == (len(listOfUsers) - 1)):
			request = api.execute.getGroupsTwo(strOfUsers = strOfIDs, v = 5.74, timeout = 30)
			req()
			strOfIDs = ''
			result = request['list']

			tmpListOfUsersGroups = list(filter(isContainOffGroup,list(result)))
			for tmpList in tmpListOfUsersGroups:
				tmpUserID = tmpList[0]
				tmpList = list(setOfOffGroups & set(tmpList))

				if checkOffGroup:
					checkOffGroup = False
					for offGroup in officialGroups:
						if len(set([officialGroups[offGroup]]) & set(tmpList)) > 0:
							isSetGroupOperator[offGroup] = 1
						if isSetGroupOperator[offGroup] == 0:
							checkOffGroup = True

				if len(tmpList) != 0:
					for j in range(len(tmpList)):
						for offGroup in officialGroups:
							if tmpList[j] == officialGroups[offGroup]:
								tmpList[j] = offGroup
					tmpList.insert(0,tmpUserID)
					listOfUsersGroups.append(list(tmpList))
				else:
					listOfUsersGroups.append(list())

	return listOfUsersGroups


def getWall (ID, offset):
	try:
		return api.execute.getWall(groupID = ID, offset = offset, v = 5.74, timeout = 30)

	except Exception as e:
		print(str(e))
		print(';;;')
		error = 'error'
		return error


def getListOfPosts (ID, timeRange):
	offset = 0
	listOfPosts = []
	boo = True
	while boo:
		wall = getWall(ID, offset)
		req()
		if wall != 'error':
				for i in range(len(wall)):
					if int(wall[i]['date']) < int(timeRange) and i != 0:
						boo = False
						break
					else:
						listOfPosts.append(copy.deepcopy(wall[i]))
				offset += 2500
		else:
			print('error in getListOfPosts')
			break
	return listOfPosts

def getLikesOfPost (ID, listOfPosts):
	listOfLikers = []
	strOfIDs = ''
	for i in range (len(listOfPosts)):
		strOfIDs += str(listOfPosts[i]['id'])
		if ((i + 1) % 25) and (i != (len(listOfPosts) - 1)):
			strOfIDs += ','
		if (not (i + 1) % 25) or (i == (len(listOfPosts) - 1)):
			request = api.execute.getLikersOfPost(ownerID = ID, itemIDs = strOfIDs, v = 5.74, timeout = 30)
			req()
			strOfIDs = ''
			for lst in request:
				tempLst = []
				for id in lst['items']:
					tempLst.append(str(id))
				listOfLikers.append(list(tempLst))
	return listOfLikers

def getRepostsOfPost (ID, listOfPosts):
	listOfLikers = []
	strOfIDs = ''
	for i in range(len(listOfPosts)):
		strOfIDs += str(listOfPosts[i]['id'])
		if ((i + 1) % 25) and (i != (len(listOfPosts) - 1)):
			strOfIDs += ','
		if (not (i + 1) % 25) or (i == (len(listOfPosts) - 1)):
			request = api.execute.getRepostersOfPost(ownerID = ID, itemIDs = strOfIDs, v = 5.74, timeout = 30)
			req()
			strOfIDs = ''
			for lst in request:
				tempLst = []
				for id in lst['items']:
					tempLst.append(str(id))
				listOfLikers.append(list(tempLst))
	return listOfLikers

def countOfLikesAndReposts (userID, ListOfLikers, listOfReposters):
	likes = 0
	reposts = 0
	for lst in ListOfLikers:
		for id in lst:
			if id == userID:
				likes += 1
	if likes > 0:
		for lst in listOfReposters:
			for id in lst:
				if id == userID:
					reposts += 1

	response = {'likes' : likes, 'reposts' : reposts}
	return response

def countOfFriendsInGroups (groupsOfFriends, friendsOfUser):
	global globalIDForFindUsersList, officialGroups
	saveThis = globalIDForFindUsersList

	count = {'теле2' : 0, 'мтс' : 0, 'мегафон' : 0, 'билайн' : 0}
	for i in range(1, len(friendsOfUser)):
		globalIDForFindUsersList = friendsOfUser[i]
		groupsOfFriend = list(filter(findUsersList, groupsOfFriends))
		if len(groupsOfFriend) != 0:
			groupsOfFriend = groupsOfFriend[0]
			for j in range(1,len(groupsOfFriend)):
				for offGroup in officialGroups:
					if groupsOfFriend[j] == offGroup:
						count[offGroup] += 1

	globalIDForFindUsersList = saveThis
	return count

def findUsersList(lst):
	global globalIDForFindUsersList

	if str(lst[0]) == str(globalIDForFindUsersList):
		return True
	else:
		return False

def getFriendsOfUsers(listOfUsers):
	strOfIDs = ''
	globalFriends = []
	listOfUsersFriends = []
	for i in range(len(listOfUsers)):
		strOfIDs += str(listOfUsers[i])
		if ((i + 1) % 25) and (i != (len(listOfUsers) - 1)):
			strOfIDs += ','
		if (not (i + 1) % 25) or (i == (len(listOfUsers) - 1)):
			result = api.execute.getFriends(strOfUsers = strOfIDs, v = 5.74, timeout = 30)
			req()
			strOfIDs = ''
			for usersFriends in result:
					listOfUsersFriends.append(list(usersFriends))
					globalFriends += list(usersFriends)[1:]
	globalFriends = list(set(globalFriends))
	response = {'listOfFriends' : listOfUsersFriends, 'global' : globalFriends}
	return response



def main ():
	global isSetGroupOperator, globalIDForFindUsersList

	WriteCSVFileOfUsers('users.csv', 'Empty', True)
	listOfMembersID = getListOfMembers('109491482')


	listOfUsers = getInfoOfUsers(listOfMembersID)
	listOdUsersGroups = getGroupsOfUsersTwo(listOfMembersID) #определение isSetGroupOperator происходит здесь


	response = getFriendsOfUsers(listOfMembersID)
	globalFriends = response['global']
	friendsOfUsers = response['listOfFriends']
	groupsOfFriends = getGroupsOfUsersTwo(globalFriends)


	if isSetGroupOperator['теле2']:
		listOfPostsT2 = getListOfPosts(-18098621, 1524245807)
		listOfLikersT2 = getLikesOfPost(-18098621, listOfPostsT2)
		listOfRepostersT2 = getRepostsOfPost(-18098621, listOfPostsT2)
	if isSetGroupOperator['билайн']:
		listOfPostsBee = getListOfPosts(-26514504, 1524245807)
		listOfLikersBee = getLikesOfPost(-26514504, listOfPostsBee)
		listOfRepostersBee = getRepostsOfPost(-26514504, listOfPostsBee)
	if isSetGroupOperator['мтс']:
		listOfPostsMTS = getListOfPosts(-8458649, 1524245807)
		listOfLikersMTS = getLikesOfPost(-8458649, listOfPostsMTS)
		listOfRepostersMTS = getRepostsOfPost(-8458649, listOfPostsMTS)
	if isSetGroupOperator['мегафон']:
		listOfPostsMega = getListOfPosts(-3785, 1524245807)
		listOfLikersMega = getLikesOfPost(-3785, listOfPostsMega)
		listOfRepostersMega = getRepostsOfPost(-3785, listOfPostsMega)


	for i in range(len(listOfUsers)):
		DataOfUser = GetUser(listOfUsers[i])

		for lst in listOdUsersGroups:
			if lst:
				if str(lst[0]) == str(DataOfUser['id']):
					DataOfUser['groups'] = lst[1:len(lst):1]
					break

		if DataOfUser['groups']:
			for oper in DataOfUser['groups']:
				lstOfLikers = []
				lstOfReposters = []
				if oper == 'теле2':
					lstOfLikers = listOfLikersT2
					lstOfReposters = listOfRepostersT2
					lOper = 'lTele2'
					rOper = 'rTele2'
				if oper == 'мтс':
					lstOfLikers = listOfLikersMTS
					lstOfReposters = listOfRepostersMTS
					lOper = 'lMTS'
					rOper = 'rMTS'
				if oper == 'мегафон':
					lstOfLikers = listOfLikersMega
					lstOfReposters = listOfRepostersMega
					lOper = 'lMegafon'
					rOper = 'rMegafon'
				if oper == 'билайн':
					lstOfLikers = listOfLikersBee
					lstOfReposters = listOfRepostersBee
					lOper = 'lBeeline'
					rOper = 'rBeeline'

				response = countOfLikesAndReposts(DataOfUser['id'],lstOfLikers,lstOfReposters)
				likes = response['likes']
				reposts = response['reposts']
				if likes:
					DataOfUser[lOper] = likes
				if reposts:
					DataOfUser[rOper] = reposts

		saveThis = globalIDForFindUsersList
		globalIDForFindUsersList = DataOfUser['id']

		friendsOfUser = list(filter(findUsersList, friendsOfUsers))
		print('$$$$')
		print(friendsOfUser)
		print('$$$$')
		if len(friendsOfUser) != 0:
			response = countOfFriendsInGroups(groupsOfFriends, list(filter(findUsersList, friendsOfUsers))[0])
			globalIDForFindUsersList = saveThis

			DataOfUser['fTele2'] = response['теле2']
			DataOfUser['fMTS'] = response['мтс']
			DataOfUser['fMegafon'] = response['мегафон']
			DataOfUser['fBeeline'] = response['билайн']
		else:
			DataOfUser['fTele2'] = 0
			DataOfUser['fMTS'] = 0
			DataOfUser['fMegafon'] = 0
			DataOfUser['fBeeline'] = 0

		WriteCSVFileOfUsers('users.csv', DataOfUser, False)

main()

# 29270122
# 53548055
# 33025155
#10 мая 2018  1525954425
#20 apr 2018  1524245807
#276469165,82092146;120781447,169777391
