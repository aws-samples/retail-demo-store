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
	"github.com/aws/aws-sdk-go/service/pinpoint"
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

//CreateEndpoint for the user
// func CreateEndpoint(phoneNumberValidateOutput &pinpoint.PhoneNumberValidateOutput, user User) {
	
// }
//UserVerifyAndUpdatePhone func
func UserVerifyAndUpdatePhone(w http.ResponseWriter, r *http.Request){
	enableCors(&w)

	type UserDetails struct {
		userid	string
		phoneNumber string
	}
	var userDetails UserDetails
	user := RepoFindUserByID(userDetails.userid)
	if user.ID == "" {
		fmt.Println("User does not exist. Cannot associate phone number to user.")
	}

	body, err := ioutil.ReadAll(io.LimitReader(r.Body, 1048576))
	if err != nil {
		panic(err)
	}
	if err := r.Body.Close(); err != nil {
		panic(err)
	}
	if err := json.Unmarshal(body, &userDetails); err != nil {
		w.Header().Set("Content-Type", "application/json; charset=UTF-8")
		w.WriteHeader(422) // unprocessable entity
		if err := json.NewEncoder(w).Encode(err); err != nil {
			panic(err)
		}
	}
	// check if the number entered by user is valid
	numberValidaterequest := &pinpoint.NumberValidateRequest{
		PhoneNumber: &userDetails.phoneNumber,
	}
	phoneValidateInput := &pinpoint.PhoneNumberValidateInput{
		NumberValidateRequest: numberValidaterequest,

	}
	res, err := pinpoint_client.PhoneNumberValidate(phoneValidateInput)
	if err != nil {
		fmt.Println("Got error calling PhoneNumberValidate:")
		fmt.Println(err.Error())
	} else {
		fmt.Println(res)
		if (res.NumberValidateResponse.PhoneTypeCode != 0]) {
			panic("Received a phone number that isn't capable of receiving SMS. Cannot create endpoint")
		} else {
			userAttributes = make(map[string][]*string)
			userAttributes["Username"] = &user.Username
			userAttributes["FirstName"] = &user.FirstName
			userAttributes["LastName"] = &user.LastName
			userAttributes["Gender"] = &user.Gender
			userAttributes["Age"] = &user.Age

			endpointRequest := &pinpoint.EndpointRequest{
				Address: &userDetails.phoneNumber,
				ChannelType: "SMS",
				OptOut: "ALL",
				Location: &pinpoint.EndpointLocation {
					PostalCode: res.NumberValidateResponse.ZipCode,
					City: res.NumberValidateResponse.City,
					Country: res.NumberValidateResponse.CountryCodeIso2,
				},
				Demographic: &pinpoint.EndpointDemographic {
					Timezone: res.NumberValidateResponse.Timezone,
				},
				User: &pinpoint.EndpointUser{
					UserAttributes: userAttributes,
					UserId: &userDetails.userid,
				},
			}
			updateEndpointInput := &pinpoint.UpdateEndpointInput{
				ApplicationId: &pinpoint_app_id,
				EndpointId: &userDetails.phoneNumber[1:],
				EndpointRequest: endpointRequest,
			}

			updateEndpointOutput, err = pinpoint_client.UpdateEndpoint(updateEndpointInput)
			if err!= nil{
				fmt.Println("Got error calling UpdateEndpoint:")
				fmt.Println(err.Error())
			} else {
				fmt.Println(updateEndpointOutput)
				//get long code from the ssm param
				getLongCodeResponse, err := ssm_client.GetParameter(&pinpoint.GetParameterInput{
					Name: "retaildemostore-pinpoint-sms-longcode"
				})
				if err!=nil {
					panic(err)
				}
				// send confirmation to the user
				sendMessageAddress = make(map[string]&pinpoint.AddressConfiguration)
				sendMessageAddress[&userDetails.phoneNumber] = &pinpoint.AddressConfiguration {
					ChannelType: "SMS"
				}
				sendMessageInput := &pinpoint.SendMessageInput {
					ApplicationId: &pinpoint_app_id,
					MessageRequest: &pinpoint.MessageRequest {
						Addresses: sendMessageAddress,
						MessageConfiguration: &pinpoint.DirectMessageConfiguration {
							SMSMessage: &pinpoint.SMSMessage {
								Body: "Reply Y to receive one time automated marketing messages at this number. No purchase necessary. T&C apply.",
								MessageType: "TRANSACTIONAL",
								OriginationNumber: getLongCodeResponse.Parameter.Value,
							},
						},
					}
				}
				sendMessageOutput, err := pinpoint_client.SendMessages(sendMessageInput)
				if err!=nil {
					fmt.Println("Got error calling SendMessages:")
					fmt.Println(err.Error())
				} else {
					fmt.Println("Message Sent")
				}
			}
		}
	}
	t := RepoUpdateUser(user)

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
