// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

import (
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path"

	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/eventbridge"
	"github.com/gorilla/mux"
)

var EventBus = os.Getenv("EVENT_BUS")

var eventBridgeClient *eventbridge.EventBridge

func init() {
	mySession := session.Must(session.NewSession())

	eventBridgeClient = eventbridge.New(mySession)
}

// Index Handler
func Index(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "Welcome to the Carts Web Service")
}

// CartIndex Handler
func CartIndex(w http.ResponseWriter, r *http.Request) {
	enableCors(&w)

	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusOK)

	var values []Cart
	for _, value := range carts {
		values = append(values, value)
	}

	if err := json.NewEncoder(w).Encode(values); err != nil {
		panic(err)
	}
}

// CartShowByID Handler
func CartShowByID(w http.ResponseWriter, r *http.Request) {
	enableCors(&w)

	vars := mux.Vars(r)
	cartID := vars["cartID"]

	if err := json.NewEncoder(w).Encode(RepoFindCartByID(cartID)); err != nil {
		panic(err)
	}
}

func sendEvent(eventType string, cart Cart) {
	cartJsonBytes, _ := json.Marshal(cart)
	cartJson := string(cartJsonBytes)

	source := "CartService"

	// write event to event bridge after successfully persisting cart
	params := &eventbridge.PutEventsInput{
		Entries: []*eventbridge.PutEventsRequestEntry{
			{
				EventBusName: &EventBus,
				Detail: &cartJson,
				DetailType: &eventType,
				Source: &source,
			},
		},
	}

	res, err := eventBridgeClient.PutEvents(params)
	if err != nil || *res.FailedEntryCount > int64(0) {
		// we could write to a dead letter queue here
		log.Println("Sending event(s) to event bus failed.")
		log.Println(err)
		log.Println(res)
	}
	log.Println(res)
}

//CartUpdate Func
func CartUpdate(w http.ResponseWriter, r *http.Request) {
	enableCors(&w)
	if (*r).Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	}

	var cart Cart
	body, err := ioutil.ReadAll(io.LimitReader(r.Body, 1048576))
	if err != nil {
		panic(err)
	}
	if err := r.Body.Close(); err != nil {
		panic(err)
	}
	if err := json.Unmarshal(body, &cart); err != nil {
		w.Header().Set("Content-Type", "application/json; charset=UTF-8")
		w.WriteHeader(422) // unprocessable entity
		if err := json.NewEncoder(w).Encode(err); err != nil {
			panic(err)
		}
	}

	id := path.Base(r.URL.Path)

	t := RepoUpdateCart(id, cart)

	sendEvent("CartUpdatedEvent", t)

	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusCreated)
	if err := json.NewEncoder(w).Encode(t); err != nil {
		panic(err)
	}
}

//CartCreate Func
func CartCreate(w http.ResponseWriter, r *http.Request) {
	enableCors(&w)
	if (*r).Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	}

	var cart Cart
	body, err := ioutil.ReadAll(io.LimitReader(r.Body, 1048576))
	if err != nil {
		panic(err)
	}
	if err := r.Body.Close(); err != nil {
		panic(err)
	}
	if err := json.Unmarshal(body, &cart); err != nil {
		w.Header().Set("Content-Type", "application/json; charset=UTF-8")
		w.WriteHeader(422) // unprocessable entity
		if err := json.NewEncoder(w).Encode(err); err != nil {
			panic(err)
		}
	}

	t := RepoCreateCart(cart)

	sendEvent("CartCreatedEvent", t)

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