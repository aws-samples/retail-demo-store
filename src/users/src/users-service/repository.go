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
	"fmt"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/dynamodb/dynamodbattribute"
)

var users Users
var usersById map[string]int
var usersByUsername map[string]int
var usersByIdentityId map[string]int
var usersByPrimaryPersona map[string][]int
var usersByAgeRange map[string][]int
var usersClaimedByIdentityId map[int]bool


// Init
func init() {

	usersById = make(map[string]int)
	usersByUsername = make(map[string]int)
	usersByIdentityId = make(map[string]int)
	usersByPrimaryPersona = make(map[string][]int)
	usersByAgeRange = make(map[string][]int)
	usersClaimedByIdentityId = make(map[int]bool)
	doLoadFromFile, _ := getenvBool("LOAD_USERS_FROM_FILE")
	log.Println("LOAD_USERS_FROM_FILE: ", doLoadFromFile)

    err := loadUsersDB()
    if err != nil {
        log.Panic("Unable to load users dynamo: ", err)
        return
    }
    if len(users) == 0 {
      if doLoadFromFile {

        err := loadUsersFile("/bin/data/users.json.gz")
        //loadedUsers, err := loadUsersFile("/bin/data/users.json.gz")
        if err != nil {
            log.Panic("Unable to load users file: ", err)
        }
      }
	}
	// users = loadedUsers
}

func loadUsersFile(filename string) (error) {

	log.Println("Attempting to load users file: ", filename)

	var r Users

	file, err := os.Open(filename)
    if err != nil {
        log.Println("Got error opening gzip file:")
        log.Println(err.Error())
        return err
    }

	defer file.Close()

	gz, err := gzip.NewReader(file)
    if err != nil {
        log.Println("Got error reading gzip file:")
        log.Println(err.Error())
        return err
    }

	defer gz.Close()

	dec := json.NewDecoder(gz)

	err = dec.Decode(&r)
    if err != nil {
        log.Println("Got error decoding gzip file:")
        log.Println(err.Error())
        return err
    }

	// Load maps with user array index
	for _, u := range r {
	    _, err := RepoCreateUser(u, true)
	    if err != nil {
			log.Println("Got error creating user:")
			log.Println(err.Error())
		    return err
	    }
		//usersById[u.ID] = i
		//usersByUsername[u.Username] = i
		//usersByPrimaryPersona[strings.Split(u.Persona, "_")[0]] = append(usersByPrimaryPersona[strings.Split(u.Persona, "_")[0]],i)
		//usersByAgeRange[getAgeRange(u.Age)] = append(usersByAgeRange[getAgeRange(u.Age)], i)
	}

	log.Println("Users successfully loaded into memory structures from file")

	return nil
	//return r, nil
}


func loadUsersDB() (error) {

	log.Println("loadUsersDB: ")

	// Build the query input parameters
	params := &dynamodb.ScanInput{
		TableName: aws.String(ddbTableUsers),
	}
	// Make the DynamoDB Query API call
	result, err := dynamoClient.Scan(params)

	if err != nil {
		log.Println("Got error scan expression:")
		log.Println(err.Error())
	}

	log.Println("loadUsersDB / items found =  ", len(result.Items))

	for _, i := range result.Items {
		user := User{}

		err = dynamodbattribute.UnmarshalMap(i, &user)

		if err != nil {
			log.Println("Got error unmarshalling:")
			log.Println(err.Error())
		}

	    _, err := RepoCreateUser(user, false)
	    if err != nil {
			log.Println("Got error creating user:")
			log.Println(err.Error())
		    return err
	    }
	}

    log.Println("Users successfully loaded into memory structures from DB")

	return nil
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

// RepoFindRandomUsersByPrimaryPersonaAndAgeRage Function
func RepoFindRandomUsersByPrimaryPersonaAndAgeRange (primaryPersona string , ageRange string, count int) Users {
	var unclaimedUsers Users
	var primaryPersonaFilteredUserIds = RepoFindUsersIdByPrimaryPersona(primaryPersona)
	var ageRangeFilteredUserIds = RepoFindUserIdsByAgeRange(ageRange)
	rand.Seed(time.Now().UnixNano())
	rand.Shuffle(len(ageRangeFilteredUserIds), func(i, j int) { ageRangeFilteredUserIds[i], ageRangeFilteredUserIds[j] = ageRangeFilteredUserIds[j], ageRangeFilteredUserIds[i] })
	for _, idx := range ageRangeFilteredUserIds {
			if len(unclaimedUsers) >= count {
				break
			}
			if containsInt(primaryPersonaFilteredUserIds,idx) && !(usersClaimedByIdentityId[idx]) {
			    if users[idx].SelectableUser {
				    log.Println("User found matching filter criteria:", idx)
				    unclaimedUsers = append(unclaimedUsers, users[idx])
				}
			}	
	}
	return unclaimedUsers
}


// RepoClaimUser Function
// Function used to map which shopper user ids have been claimed by the user Id.
func RepoClaimUser(userId int ) bool{
	log.Println("An identity has claimed the user id:" , userId)
	usersClaimedByIdentityId[userId]= true
	return true
}

func RepoFindRandomUser(count int) Users {
	rand.Seed(time.Now().UnixNano())
	var randomUserId int
	var randomUsers Users 
	if len(users)>0  {
		for (len(randomUsers)< count){
				randomUserId = rand.Intn(len(users))	
				log.Println("Random number Selected:",randomUserId)
				if randomUserId!=0 {
					if !(usersClaimedByIdentityId[randomUserId]) {
					    if users[randomUserId].SelectableUser {
						    log.Println("Random user id selected:",randomUserId)
						    randomUsers = append(randomUsers,RepoFindUserByID(strconv.Itoa(randomUserId)))
						    log.Println("Random users :",randomUsers)
						}
					} 
				}
		}
	}
	return randomUsers
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
func RepoUpdateUser(user User) User {
	if idx, ok := usersById[user.ID]; ok {

		existingUser := &users[idx]

		log.Printf("RepoUpdateUser from %#v to %#v", existingUser, user)

		existingUser.FirstName = user.FirstName
		existingUser.LastName = user.LastName
		existingUser.Email = user.Email
		existingUser.Addresses = user.Addresses
		existingUser.SignUpDate = user.SignUpDate
		existingUser.LastSignInDate = user.LastSignInDate
		existingUser.PhoneNumber = user.PhoneNumber

		if len(existingUser.IdentityId) > 0 && existingUser.IdentityId != user.IdentityId {
			delete(usersByIdentityId, existingUser.IdentityId)
		}

		existingUser.IdentityId = user.IdentityId

		if len(user.IdentityId) > 0 {
			usersByIdentityId[user.IdentityId] = idx
		}

		log.Printf("Updating user in dynamodb")

        av, err := dynamodbattribute.MarshalMap(existingUser)

        if err != nil {
            fmt.Println("Got error calling dynamodbattribute MarshalMap:")
            fmt.Println(err.Error())
            return user
        }

        input := &dynamodb.PutItemInput{
            Item:      av,
            TableName: aws.String(ddbTableUsers),
        }

        _, err = dynamoClient.PutItem(input)
        if err != nil {
            fmt.Println("Got error calling PutItem:")
            fmt.Println(err.Error())
        }

		return RepoFindUserByID(user.ID)
	}

	// return empty User if not found
	return User{}
}

// RepoCreateUser Function
func RepoCreateUser(user User, addToDynamo bool) (User, error) {
    log.Printf("RepoCreateUser --> %#v", user)

	if _, ok := usersByUsername[user.Username]; ok {
		return User{}, errors.New("User with this username already exists")
	}

	idx := len(users)

	if len(user.ID) > 0 {
		// ID provided by caller (provisionally created on storefront or external simulation) so make
		// sure it's not already taken.
		if _, ok := usersById[user.ID]; ok {
			return User{}, errors.New("User with this ID already exists")
		}
	} else {
		user.ID = strconv.Itoa(idx)
	}

	users = append(users, user)
	usersById[user.ID] = idx
	usersByUsername[user.Username] = idx
	if len(user.IdentityId) > 0 {
		usersByIdentityId[user.IdentityId] = idx
	}
	if len(user.Persona) > 0 {
		usersByPrimaryPersona[strings.Split(user.Persona, "_")[0]] = append(usersByPrimaryPersona[strings.Split(user.Persona, "_")[0]], idx)
		usersByAgeRange[getAgeRange(user.Age)] = append(usersByAgeRange[getAgeRange(user.Age)], idx)
	}

    if addToDynamo {
        log.Printf("Adding to dynamo")
        av, err := dynamodbattribute.MarshalMap(user)

        if err != nil {
            fmt.Println("Got error calling dynamodbattribute MarshalMap:")
            fmt.Println(err.Error())
            return user, err
        }

        input := &dynamodb.PutItemInput{
            Item:      av,
            TableName: aws.String(ddbTableUsers),
        }

        _, err = dynamoClient.PutItem(input)
        if err != nil {
            fmt.Println("Got error calling PutItem:")
            fmt.Println(err.Error())
            return user, err
        }
    }
	return user, nil
}

func getenvBool(key string) (bool, error) {
    s := os.Getenv(key)
    if err != nil {
        return false, err
    }
    v, err := strconv.ParseBool(s)
    if err != nil {
        return false, err
    }
    return v, nil
}
