// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

import (
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"net/http"
	"strconv"

	"github.com/gorilla/mux"
)

var MAX_RANDOM_USER_COUNT_PER_REQEUST int = 20

// Index Handler
func Index(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "Welcome to the Users Web Service")
}

// UserIndex Handler
func UserIndex(w http.ResponseWriter, r *http.Request) {

	enableCors(&w)

	var offset = 0
	var count = 20

	var keys = r.URL.Query()
	var offsetParam = keys.Get("offset")
	if len(offsetParam) > 0 {
		i, err := strconv.Atoi(offsetParam)
		if err != nil {
			panic(err)
		}

		if i < 0 {
			http.Error(w, "Offset must be >= 0", http.StatusUnprocessableEntity)
			return
		}
		offset = i
	}

	var countParam = keys.Get("count")
	if len(countParam) > 0 {
		i, err := strconv.Atoi(countParam)
		if err != nil {
			panic(err)
		}

		if i < 1 {
			http.Error(w, "Count must be > 0", http.StatusUnprocessableEntity)
			return
		}

		if i > 10000 {
			http.Error(w, "Count exceeds maximum value; please use paging by offset", http.StatusUnprocessableEntity)
			return
		}

		count = i
	}

	w.Header().Set("Content-Type", "application/json; charset=UTF-8")

	var end = offset + count
	if end > len(users) {
		end = len(users)
	}

	ret := make([]User, 0, count)

	idx := offset
	for len(ret) < count && idx < len(users) {
		// Do NOT return any users with an associated identity ID.
		if len(users[idx].IdentityId) == 0 {
			ret = append(ret, users[idx])
		}
		idx++
	}

	if err := json.NewEncoder(w).Encode(ret); err != nil {
		panic(err)
	}
}

// UserShowByID Handler
func UserShowByID(w http.ResponseWriter, r *http.Request) {

	enableCors(&w)

	vars := mux.Vars(r)
	userID := vars["userID"]

	if err := json.NewEncoder(w).Encode(RepoFindUserByID(userID)); err != nil {
		panic(err)
	}
}

// UserShowByUsername Handler
func UserShowByUsername(w http.ResponseWriter, r *http.Request) {

	enableCors(&w)

	vars := mux.Vars(r)
	username := vars["username"]

	if err := json.NewEncoder(w).Encode(RepoFindUserByUsername(username)); err != nil {
		panic(err)
	}
}

// UserShowByIdentityId handler
func UserShowByIdentityId(w http.ResponseWriter, r *http.Request) {
	enableCors(&w)

	vars := mux.Vars(r)
	identityID := vars["identityID"]

	if err := json.NewEncoder(w).Encode(RepoFindUserByIdentityID(identityID)); err != nil {
		panic(err)
	}
}

// ClaimUser handler
func ClaimUser(w http.ResponseWriter, r *http.Request) {
	
	enableCors(&w)
	if (*r).Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	}
	var userId int
	vars := mux.Vars(r)
	userIdVar := vars["userID"]
	userId, err := strconv.Atoi(userIdVar)
	if err != nil {
		panic(err)
	}
	if err := json.NewEncoder(w).Encode(RepoClaimUser(userId)); err != nil {
		panic(err)
	}
} 

// GetRandomUser handler
func GetRandomUser(w http.ResponseWriter, r *http.Request) {
	enableCors(&w)

	var keys = r.URL.Query()
	var count = 1
	var countParam = keys.Get("count")
	if len(countParam) > 0 {
		i, err := strconv.Atoi(countParam)
		if err != nil {
			panic(err)
		}
		if i <= 0 || i > MAX_RANDOM_USER_COUNT_PER_REQEUST { 
			http.Error(w, fmt.Sprintf("Count must be grater than 0 and less than %d", MAX_RANDOM_USER_COUNT_PER_REQEUST) , http.StatusUnprocessableEntity)
			return
		}
		count = i
	}
	if err := json.NewEncoder(w).Encode(RepoFindRandomUser(count)); err != nil {
		panic(err)
	}
}

// GetFilteredUser handler
func GetUnclaimedUsers(w http.ResponseWriter, r *http.Request) {

	enableCors(&w)

	var keys = r.URL.Query()
	
	primaryPersona := keys.Get("primaryPersona")
	ageRange := keys.Get("ageRange")
	var count = 1
	var countParam = keys.Get("count")
	if len(countParam) > 0 {
		i, err := strconv.Atoi(countParam)
		if err != nil {
			panic(err)
		}
		if i <= 0 || i > MAX_RANDOM_USER_COUNT_PER_REQEUST { 
			http.Error(w, fmt.Sprintf("Count must be greater than 0 and less than %d", MAX_RANDOM_USER_COUNT_PER_REQEUST) , http.StatusUnprocessableEntity)
			return
		}
		count = i
	}
	
	if err := json.NewEncoder(w).Encode(RepoFindRandomUsersByPrimaryPersonaAndAgeRange(primaryPersona,ageRange,count)); err != nil {
		panic(err)
	}
}
//UserUpdate Func
func UserUpdate(w http.ResponseWriter, r *http.Request) {
	enableCors(&w)
	if (*r).Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	}

	var user User
	body, err := ioutil.ReadAll(io.LimitReader(r.Body, 1048576))
	if err != nil {
		panic(err)
	}
	if err := r.Body.Close(); err != nil {
		panic(err)
	}
	if err := json.Unmarshal(body, &user); err != nil {
		w.Header().Set("Content-Type", "application/json; charset=UTF-8")
		w.WriteHeader(422) // unprocessable entity
		if err := json.NewEncoder(w).Encode(err); err != nil {
			panic(err)
		}
	}

	t := RepoUpdateUser(user)
	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusCreated)
	if err := json.NewEncoder(w).Encode(t); err != nil {
		panic(err)
	}
}

//UserCreate Func
func UserCreate(w http.ResponseWriter, r *http.Request) {
	enableCors(&w)
	if (*r).Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	}

	var user User
	body, err := ioutil.ReadAll(io.LimitReader(r.Body, 1048576))
	if err != nil {
		panic(err)
	}
	if err := r.Body.Close(); err != nil {
		panic(err)
	}
	if err := json.Unmarshal(body, &user); err != nil {
		w.Header().Set("Content-Type", "application/json; charset=UTF-8")
		w.WriteHeader(422) // unprocessable entity
		if err := json.NewEncoder(w).Encode(err); err != nil {
			panic(err)
		}
	}

	t, err := RepoCreateUser(user)
	if err != nil {
		panic(err)
	}

	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusCreated)
	if err := json.NewEncoder(w).Encode(t); err != nil {
		panic(err)
	}
}

// enableCors
func enableCors(w *http.ResponseWriter) {
	(*w).Header().Set("Access-Control-Allow-Origin", "*")
	(*w).Header().Set("Access-Control-Allow-Methods", "POST, PUT, GET, OPTIONS")
	(*w).Header().Set("Access-Control-Allow-Headers", "Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization")
}
