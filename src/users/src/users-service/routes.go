// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

import "net/http"

// Route Struct
type Route struct {
	Name        string
	Method      string
	Pattern     string
	HandlerFunc http.HandlerFunc
}

// Routes Array
type Routes []Route

var routes = Routes{
	Route{
		"Index",
		"GET",
		"/",
		Index,
	},
	Route{
		"UsersIndex",
		"GET",
		"/users/all",
		UserIndex,
	},
	Route{
		"UserShowByID",
		"GET",
		"/users/id/{userID}",
		UserShowByID,
	},
	Route{
		"UserShowByUsername",
		"GET",
		"/users/username/{username}",
		UserShowByUsername,
	},
	Route{
		"UserShowByIdentityId",
		"GET",
		"/users/identityid/{identityID}",
		UserShowByIdentityId,
	},
	Route{
		"UserCreate",
		"POST",
		"/users",
		UserCreate,
	},
	Route{
		"UserCreate",
		"OPTIONS",
		"/users",
		UserCreate,
	},
	Route{
		"UserUpdate",
		"PUT",
		"/users/id/{userID}",
		UserUpdate,
	},
	Route{
		"UserUpdate",
		"OPTIONS",
		"/users/id/{userID}",
		UserUpdate,
	},
}
