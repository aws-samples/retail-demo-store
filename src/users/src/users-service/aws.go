// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

import (
	"os"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/pinpoint"
)

//var sess *session.Session
var sess, err = session.NewSession(&aws.Config{})

var pinpoint_app_id = os.Getenv("PINPOINT_APP_ID")
var pinpoint_sms_long_code = os.Getenv("PINPOINT_SMS_LONG_CODE")
var pinpoint_client = pinpoint.New(sess)

// Connect Stuff
func init() {
	
}
