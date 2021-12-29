// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

import (
	"log"
	"os"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	//"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/service/pinpoint"
	"github.com/aws/aws-sdk-go/service/ssm"
	"github.com/aws/aws-sdk-go/service/dynamodb"
)

//var sess *session.Session
var sess, err = session.NewSession(&aws.Config{})

var ddbTableUsers = os.Getenv("DDB_TABLE_USERS")

var pinpoint_app_id = os.Getenv("PINPOINT_APP_ID")
var pinpoint_client = pinpoint.New(sess)
var ssm_client = ssm.New(sess)

var dynamoClient *dynamodb.DynamoDB

// Connect Stuff
func init() {
    log.Println("Creating dynamo client")
	dynamoClient = dynamodb.New(sess)
}
