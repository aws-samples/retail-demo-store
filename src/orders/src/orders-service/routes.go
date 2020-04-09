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
		"OrdersIndex",
		"GET",
		"/orders/all",
		OrderIndex,
	},
	Route{
		"OrderShowByID",
		"GET",
		"/orders/id/{orderID}",
		OrderShowByID,
	},
	Route{
		"OrderShowByUsername",
		"GET",
		"/orders/username/{username}",
		OrderIndexByUsername,
	},
	Route{
		"OrderCreate",
		"POST",
		"/orders",
		OrderCreate,
	},
	Route{
		"OrderCreate",
		"OPTIONS",
		"/orders",
		OrderCreate,
	},
}
