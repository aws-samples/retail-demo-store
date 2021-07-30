// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

import (
	"log"
	"net/http"
	"os"
)

func main() {
	port, exists := os.LookupEnv("PORT")
	if !exists {
		port = "80"
	}

	router := NewRouter()
	log.Fatal(http.ListenAndServe(":" + port, router))
}