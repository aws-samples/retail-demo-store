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
)

var users Users
var usersById map[string]int
var usersByUsername map[string]int
var usersByIdentityId map[string]int

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
	}

	log.Println("Users successfully loaded into memory structures")

	return r, nil
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

		if len(t.IdentityId) > 0 {
			u.IdentityId = t.IdentityId
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
	t.ID = strconv.Itoa(idx)
	users = append(users, t)
	usersById[t.ID] = idx
	usersByUsername[t.Username] = idx
	return t, nil
}
