import time
import copy
import csv
import datetime
import pickle

import login

# 53548055

api = login.api

requestTime = 0


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

def writeCSVFileOfAnalysisUsers (name, user, create):
	if create is True:
		data = ["ID;PageRank;groups;Friends".split(";")]
		with open(name, 'w', encoding = "utf-8") as file:
			writer = csv.writer(file, delimiter = ';')
			for line in data:
				writer.writerow((line))
	else:
		with open(name, 'a', encoding = "utf-8") as file:
			writer = csv.writer(file, delimiter = ';')
			writer.writerow((user['id'], user['PageRank'], user['groups'], user['friends']))

def writeCSVFileOfAnalysisFriends (name, user, create):
	if create is True:
		data = ["owner;ID;PageRank;groups".split(";")]
		with open(name, 'w', encoding = "utf-8") as file:
			writer = csv.writer(file, delimiter = ';')
			for line in data:
				writer.writerow((line))
	else:
		with open(name, 'a', encoding = "utf-8") as file:
			writer = csv.writer(file, delimiter = ';')
			writer.writerow((user['owner'], user['id'], user['PageRank'], user['groups']))

def getListOfMembers (idOfGroup):
	offset = 0
	request = api.execute.getListOfUsersInGroup(idGroup = idOfGroup, offset = offset, v = 5.73, timeout = 120)
	req()
	b = request['users']
	listOfMembers = []
	for i in b:
		listOfMembers.append(str(i))

	while request['overCount']:
		offset += 25000
		request = api.execute.getListOfUsersInGroup(idGroup = idOfGroup, offset = offset, v = 5.73, timeout = 120)
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
			tempListOfUsers = api.users.get(user_ids = localStrOfUsers, fields = 'contacts', v = 5.83, timeout = 120)
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
	result = api.execute.getGroups(idUser = userID, offset = localOffset, v = 5.74, timeout = 120)
	req()
	listOfGroups = []
	for group in result['groups']:
		for oGroup in officialGroups:
			if str(group) == str(officialGroups[oGroup]):
				listOfGroups.append(oGroup + ' ' + str(group) + ';')

	while result['overCount'] > 0:
		localOffset += 25000
		result = api.execute.getGroups(idUser = userID, offset = localOffset, v = 5.74, timeout = 120)
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
			while True:
				try:
					request = api.execute.getGroupsTwo(strOfUsers = strOfIDs, v = 5.74, timeout = 120)
					req()
					break
				except Exception as e:
					print(e)
					continue

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
		return api.execute.getWall(groupID = ID, offset = offset, v = 5.74, timeout = 120)

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
			request = api.execute.getLikersOfPost(ownerID = ID, itemIDs = strOfIDs, v = 5.74, timeout = 120)
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
			request = api.execute.getRepostersOfPost(ownerID = ID, itemIDs = strOfIDs, v = 5.74, timeout = 120)
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

def FindFriendsInGroups (userID, groupsOfFriends, friendsOfUser):
	global globalIDForFindUsersList, officialGroups
	saveThis = globalIDForFindUsersList

	count = {'теле2' : 0, 'мтс' : 0, 'мегафон' : 0, 'билайн' : 0}
	lstOfFriendsInGroup = []
	for i in range(1, len(friendsOfUser)):
		lstOfGroupsOfUser = []
		globalIDForFindUsersList = friendsOfUser[i]
		groupsOfFriend = list(filter(findUsersList, groupsOfFriends))
		if len(groupsOfFriend) != 0:
			groupsOfFriend = groupsOfFriend[0]
			for j in range(1,len(groupsOfFriend)):
				for offGroup in officialGroups:
					if groupsOfFriend[j] == offGroup:
						count[offGroup] += 1
						lstOfGroupsOfUser.append(str(offGroup))
		if len(lstOfGroupsOfUser) > 0:
			lstOfFriendsInGroup.append({str(friendsOfUser[i]) : lstOfGroupsOfUser})

	globalIDForFindUsersList = saveThis
	return {'count' : count, 'lst' : lstOfFriendsInGroup}

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
			result = api.execute.getFriends(strOfUsers = strOfIDs, v = 5.74, timeout = 120)
			req()
			strOfIDs = ''
			for usersFriends in result:
					listOfUsersFriends.append(list(usersFriends))
					globalFriends += list(usersFriends)[1:]
	globalFriends = list(set(globalFriends))
	response = {'listOfFriends' : listOfUsersFriends, 'global' : globalFriends}
	return response



def collectInfoFromUsers (groupID):
	global isSetGroupOperator, globalIDForFindUsersList, officialGroups

	lstOfDataOfUsers = []
	filteredLstOfDataOfUsers = []

	WriteCSVFileOfUsers('users.csv', 'Empty', True)
	WriteCSVFileOfUsers('usersProfitable.csv', 'Empty', True)
	listOfMembersID = getListOfMembers(str(groupID))

	print(datetime.datetime.now().strftime("%d-%m-%Y %H:%M"))
	listOfUsers = getInfoOfUsers(listOfMembersID)
	print(datetime.datetime.now().strftime("%d-%m-%Y %H:%M"))
	listOdUsersGroups = getGroupsOfUsersTwo(listOfMembersID) #определение isSetGroupOperator происходит здесь
	print(datetime.datetime.now().strftime("%d-%m-%Y %H:%M"))

	print('Анализ друзей?')
	startFriends = input()


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

		lstOfDataOfUsers.append(copy.deepcopy(DataOfUser))


	if str(startFriends) == '1':
		dictOfFriendsInGroup = {}
		countOfUsersFriends = {}
		lstOfOffGroups = []
		filteredLstOfDataOfUsers = []
		for group in officialGroups:
			lstOfOffGroups.append(str(group))
		setOfOffGroups = set(lstOfOffGroups)
		lstOfAnalysisWithFriends = []

		for DataOfUser in lstOfDataOfUsers:
			setUserOper = set(list(DataOfUser['operator']))
			setUserGroups = set(DataOfUser['groups'])
			if (setOfOffGroups & setUserGroups) | (setOfOffGroups & setUserOper):
				lstOfAnalysisWithFriends.append(DataOfUser['id'])
				filteredLstOfDataOfUsers.append(copy.deepcopy(DataOfUser))



		response = getFriendsOfUsers(lstOfAnalysisWithFriends)

		globalFriends = response['global']
		friendsOfUsers = response['listOfFriends']

		for userFriends in friendsOfUsers:
			countOfUsersFriends[userFriends[0]] = len(userFriends) - 1

		with open('countOfUsersFriends.pickle', 'wb') as f:
			pickle.dump(countOfUsersFriends, f)

		with open('filteredLstOfDataOfUsers.pickle', 'wb') as f:
			pickle.dump(filteredLstOfDataOfUsers, f)

		groupsOfFriends = getGroupsOfUsersTwo(globalFriends)


	for DataOfUser in filteredLstOfDataOfUsers:
		if str(startFriends) == '1':
			setUserOper = set(list(DataOfUser['operator']))
			setUserGroups = set(DataOfUser['groups'])

			if (setOfOffGroups & setUserGroups) | (setOfOffGroups & setUserOper):
				saveThis = globalIDForFindUsersList
				globalIDForFindUsersList = DataOfUser['id']

				friendsOfUser = list(filter(findUsersList, friendsOfUsers))

				if len(friendsOfUser) != 0:
					response = FindFriendsInGroups(DataOfUser['id'], groupsOfFriends, list(filter(findUsersList, friendsOfUsers))[0])
					localOper = response['count']
					dictOfFriendsInGroup[DataOfUser['id']] = response['lst']
					globalIDForFindUsersList = saveThis

					DataOfUser['fTele2'] = localOper['теле2']
					DataOfUser['fMTS'] = localOper['мтс']
					DataOfUser['fMegafon'] = localOper['мегафон']
					DataOfUser['fBeeline'] = localOper['билайн']

				else:
					DataOfUser['fTele2'] = 0
					DataOfUser['fMTS'] = 0
					DataOfUser['fMegafon'] = 0
					DataOfUser['fBeeline'] = 0

			else:
				DataOfUser['fTele2'] = 0
				DataOfUser['fMTS'] = 0
				DataOfUser['fMegafon'] = 0
				DataOfUser['fBeeline'] = 0

	for DataOfUser in lstOfDataOfUsers:
		WriteCSVFileOfUsers('users.csv', DataOfUser, False)

	with open('dictOfFriendsInGroup.pickle', 'wb') as f:
		pickle.dump(dictOfFriendsInGroup, f)



def analysisOfPageRank(dictOfFriendsInGroup,filteredLstOfDataOfUsers,countOfUsersFriends):
	totalCountOfFriends = 0
	lstOfFriendsInGroup = []
	countOfFriendsFriends = {}

	for user in countOfUsersFriends:
		totalCountOfFriends += float(countOfUsersFriends[user])

	for owner in dictOfFriendsInGroup:
		for dict in dictOfFriendsInGroup[owner]:
			for friend in dict:
				lstOfFriendsInGroup.append(str(friend))


	response = getFriendsOfUsers(lstOfFriendsInGroup)

	lstOfFriendsFriends = response['listOfFriends']

	for friends in lstOfFriendsFriends:
		countOfFriendsFriends[str(friends[0])] = len(friends) - 1
		totalCountOfFriends += len(friends) - 1

	writeCSVFileOfAnalysisUsers('analysUsers.csv', 'Empty', True)
	writeCSVFileOfAnalysisFriends('analysFriends.csv', 'Empty', True)

	for DataUser in filteredLstOfDataOfUsers:
		newDataUser = {'id':'', 'groups': '', 'friends': '', 'PageRank' : ''}
		friendInfo = {'owner' : '', 'id':'', 'groups': '', 'friends': '', 'PageRank' : ''}
		lstOfFriends = []
		newDataUser['id'] = DataUser['id']
		newDataUser['groups'] = DataUser['groups']

		for count in  countOfUsersFriends:
			if str(DataUser['id']) ==  str(count):
				newDataUser['PageRank'] = str(float(countOfUsersFriends[count])/totalCountOfFriends)

		for owner in dictOfFriendsInGroup:
			if str(owner) == str(DataUser['id']):
				print()
				print(dictOfFriendsInGroup[owner])
				for dict in dictOfFriendsInGroup[owner]:
					print(dict)
					for friend in dict:
						lstOfFriends.append(str(friend))
						lstOfGroups = dict[friend]
						friendInfo['owner'] = str(owner)
						friendInfo['id'] = str(friend)
						friendInfo['groups'] = lstOfGroups
						for count in countOfFriendsFriends:
							if str(count) == str(friend):
								friendInfo['PageRank'] = str(float(countOfFriendsFriends[count])/totalCountOfFriends)
						writeCSVFileOfAnalysisFriends('analysFriends.csv', friendInfo, False)

		newDataUser['friends'] = lstOfFriends
		writeCSVFileOfAnalysisUsers('analysUsers.csv', newDataUser, False)



def main():
	print('Collect info from users: y/n')
	while True:
		print('Press the key')
		startCollect = str(input())
		if startCollect == 'y' or startCollect == 'Y':
			collectInfoFromUsers(53548055)
			break
		else:
			if startCollect == 'n' or startCollect == 'N':
				print('aaa')
				break
			else:
				print('Wrong key pressed')

	with open('dictOfFriendsInGroup.pickle', 'rb') as f:
		dictOfFriendsInGroup = pickle.load(f)

	with open('filteredLstOfDataOfUsers.pickle', 'rb') as f:
		lstOfDataOfUsers = pickle.load(f)

	with open('countOfUsersFriends.pickle', 'rb') as f:
		countOfUsersFriends = pickle.load(f)

	analysisOfPageRank (dictOfFriendsInGroup,lstOfDataOfUsers,countOfUsersFriends)

main()

# 29270122
# 53548055
# 33025155
#10 мая 2018  1525954425
#20 apr 2018  1524245807
#276469165,82092146;120781447,169777391
