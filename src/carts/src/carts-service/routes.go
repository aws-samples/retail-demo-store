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
		"CartsIndex",
		"GET",
		"/carts/all",
		CartIndex,
	},
	Route{
		"CartShowByID",
		"GET",
		"/carts/id/{cartID}",
		CartShowByID,
	},
	Route{
		"CartCreate",
		"POST",
		"/carts",
		CartCreate,
	},
	Route{
		"CartCreate",
		"OPTIONS",
		"/carts",
		CartCreate,
	},
	Route{
		"CartUpdate",
		"PUT",
		"/carts/id/{cartID}",
		CartUpdate,
	},
	Route{
		"CartUpdate",
		"OPTIONS",
		"/carts/id/{cartID}",
		CartUpdate,
	},
}
