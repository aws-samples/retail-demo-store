// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

import (
	"compress/gzip"
	"encoding/json"
	"errors"
	"log"
	"os"
	"strconv"
	"strings"
	"math/rand"
	"time"
)

var users Users
var usersById map[string]int
var usersByUsername map[string]int
var usersByIdentityId map[string]int
var usersByPrimaryPersona map[string][]int
var usersByAgeRange map[string][]int
var usersClaimedByIdentityId map[int]string


// Init
func init() {
	loadedUsers, err := loadUsers("/bin/data/users.json.gz")
	if err != nil {
		log.Panic("Unable to load users file: ", err)
	}
	users = loadedUsers
}

func loadUsers(filename string) (Users, error) {

	log.Println("Attempting to load users file: ", filename)

	var r Users
	usersById = make(map[string]int)
	usersByUsername = make(map[string]int)
	usersByIdentityId = make(map[string]int)
	usersByPrimaryPersona = make(map[string][]int)
	usersByAgeRange = make(map[string][]int)
	usersClaimedByIdentityId = make(map[int]string)

	file, err := os.Open(filename)
	if err != nil {
		return r, err
	}

	defer file.Close()

	gz, err := gzip.NewReader(file)
	if err != nil {
		return r, err
	}

	defer gz.Close()

	dec := json.NewDecoder(gz)

	err = dec.Decode(&r)
	if err != nil {
		return r, err
	}

	// Load maps with user array index
	for i, u := range r {
		usersById[u.ID] = i
		usersByUsername[u.Username] = i
		usersByPrimaryPersona[strings.Split(u.Persona, "_")[0]] = append(usersByPrimaryPersona[strings.Split(u.Persona, "_")[0]],i)
		usersByAgeRange[getAgeRange(u.Age)] = append(usersByAgeRange[getAgeRange(u.Age)], i)	
	}

	log.Println("Users successfully loaded into memory structures")

	return r, nil
}

func getAgeRange(age int) string{
	if age < 18 {
	     return ""
	}else if age < 25 {
		return "18-24"
	}else if age < 35 {
		return "25-34"
	}else if age < 45 {
		return "35-44"
	}else if age < 55 {
		return "45-54"
	}else if age < 70 {
		return "54-70"
	}else {
		return "70-and-above"
	}
}

// containsInt returns a bool indicating whether the given []int contained the given int
func containsInt(slice []int, value int) bool {
	for _, v := range slice {
		if value == v {
			return true
		}
	}
	return false
}

// RepoFindUsersIdByAgeRange Function
func RepoFindUserIdsByAgeRange(ageRange string) []int {
	return usersByAgeRange[ageRange]	 
}

// RepoFindUsersIdByPrimaryPersona Function
func RepoFindUsersIdByPrimaryPersona(persona string) []int {
	return usersByPrimaryPersona[persona]
}

// RepoFindRandomUserByPrimaryPersonaAndAgeRage Function
func RepoFindRandomUserByPrimaryPersonaAndAgeRange (primaryPersona string , ageRange string) User {
	var primaryPersonaFilteredUserIds = RepoFindUsersIdByPrimaryPersona(primaryPersona)
	var ageRangeFilteredUserIds = RepoFindUserIdsByAgeRange(ageRange)
	rand.Seed(time.Now().UnixNano())
	rand.Shuffle(len(ageRangeFilteredUserIds), func(i, j int) { ageRangeFilteredUserIds[i], ageRangeFilteredUserIds[j] = ageRangeFilteredUserIds[j], ageRangeFilteredUserIds[i] })
	for _, idx := range ageRangeFilteredUserIds {
		if containsInt(primaryPersonaFilteredUserIds,idx) && len(usersClaimedByIdentityId[idx])==0 {
			log.Println("User found matching filter criteria:", idx)
			return users[idx]
		}
	}
	log.Println("No User found matching filter criteria")
	return User{}	
}


// RepoClaimUser Function
// Function used to map which shopper user ids have been claimed by the user Id.
func RepoClaimUser(userId int , identityID string) bool{
	log.Println("An identity has claimed the user id:" , userId)
	usersClaimedByIdentityId[userId]= identityID
	return true
}

func RepoFindRandomUser () User {
	rand.Seed(time.Now().UnixNano())
	randomUserFound := false
	var randomUserId int
	if len(users)>0 {
		for !randomUserFound {
			randomUserId = rand.Intn(len(users))	
			log.Println("Random number Selected:",randomUserId)
			if randomUserId!=0 {
				if len(usersClaimedByIdentityId[randomUserId])==0 {
					randomUserFound =true;
				} 
			}
		}
		log.Println("Random user returned with userId:",randomUserId)
		return users[randomUserId]
	}
	return User{}	
}

// RepoFindUserByID Function
func RepoFindUserByID(id string) User {
	if idx, ok := usersById[id]; ok {
		return users[idx]
	} else {
		return User{}
	}
}

// RepoFindUserByUsername Function
func RepoFindUserByUsername(username string) User {
	if idx, ok := usersByUsername[username]; ok {
		return users[idx]
	} else {
		return User{}
	}
}

// RepoFindUserByIdentityID Function
func RepoFindUserByIdentityID(identityID string) User {
	if idx, ok := usersByIdentityId[identityID]; ok {
		return users[idx]
	} else {
		return User{}
	}
}

// RepoUpdateUser Function
func RepoUpdateUser(t User) User {
	if idx, ok := usersById[t.ID]; ok {
		u := &users[idx]
		u.FirstName = t.FirstName
		u.LastName = t.LastName
		u.Email = t.Email
		u.Addresses = t.Addresses
		u.SignUpDate = t.SignUpDate
		u.LastSignInDate = t.LastSignInDate

		if len(u.IdentityId) > 0 && u.IdentityId != t.IdentityId {
			delete(usersByIdentityId, u.IdentityId)
		}

		u.IdentityId = t.IdentityId

		if len(t.IdentityId) > 0 {
			usersByIdentityId[t.IdentityId] = idx
		}

		return RepoFindUserByID(t.ID)
	}

	// return empty User if not found
	return User{}
}

// RepoCreateUser Function
func RepoCreateUser(t User) (User, error) {
	if _, ok := usersByUsername[t.Username]; ok {
		return User{}, errors.New("User with this username already exists")
	}

	idx := len(users)

	if len(t.ID) > 0 {
		// ID provided by caller (provisionally created on storefront) so make
		// sure it's not already taken.
		if _, ok := usersById[t.ID]; ok {
			return User{}, errors.New("User with this ID already exists")
		}
	} else {
		t.ID = strconv.Itoa(idx)
	}

	users = append(users, t)
	usersById[t.ID] = idx
	usersByUsername[t.Username] = idx
	if len(t.IdentityId) > 0 {
		usersByIdentityId[t.IdentityId] = idx
	}

	return t, nil
}
