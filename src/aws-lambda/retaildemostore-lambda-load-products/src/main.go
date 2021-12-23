// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

import (
	"context"
	"errors"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"time"

	"github.com/aws/aws-lambda-go/cfn"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/dynamodb/dynamodbattribute"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
	"gopkg.in/yaml.v2"
)

// Product Struct
// using omitempty as a DynamoDB optimization to create indexes
type Product struct {
	ID             string   `json:"id" yaml:"id"`
	URL            string   `json:"url" yaml:"url"`
	SK             string   `json:"sk" yaml:"sk"`
	Name           string   `json:"name" yaml:"name"`
	Category       string   `json:"category" yaml:"category"`
	Style          string   `json:"style" yaml:"style"`
	Description    string   `json:"description" yaml:"description"`
	Aliases        []string `json:"aliases" yaml:"aliases"` // keywords for use with e.g. Alexa
	Price          float32  `json:"price" yaml:"price"`
	Image          string   `json:"image" yaml:"image"`
	Featured       string   `json:"featured,omitempty" yaml:"featured,omitempty"`
	GenderAffinity string   `json:"gender_affinity,omitempty" yaml:"gender_affinity,omitempty"`
	CurrentStock   int      `json:"current_stock" yaml:"current_stock"`
}

// Products Array
type Products []Product

// Category Struct
type Category struct {
	ID                string `json:"id" yaml:"id"`
	Name              string `json:"name" yaml:"name"`
	Image             string `json:"image" yaml:"image"`
	HasGenderAffinity bool   `json:"has_gender_affinity" yaml:"has_gender_affinity"`
}

// Categories Array
type Categories []Category

var (
	// DefaultHTTPGetAddress Default Address
	DefaultHTTPGetAddress = "https://checkip.amazonaws.com"

	// ErrNoIP No IP found in response
	ErrNoIP = errors.New("No IP in HTTP response")

	// ErrNon200Response non 200 status code in response
	ErrNon200Response = errors.New("Non 200 Response found")

	// aws
	sess, err = session.NewSession(&aws.Config{})

	// s3
	// Create a downloader with the session and default options
	s3downloader = s3manager.NewDownloader(sess)

	// dynamod
	dynamoclient = dynamodb.New(sess)

	returnstring string
)

// DynamoDBPutItem - upserts item in DDB table
func DynamoDBPutItem(item map[string]*dynamodb.AttributeValue, ddbtable string) {
	input := &dynamodb.PutItemInput{
		Item:      item,
		TableName: aws.String(ddbtable),
	}
	_, err = dynamoclient.PutItem(input)
	if err != nil {
		fmt.Println("Got error calling PutItem:")
		fmt.Println(err.Error())
	}
}

func loadData(s3bucket, s3file, ddbtable, datatype string) (string, error) {

	start := time.Now()

	var products Products
	var categories Categories

	localfile := "/tmp/load.yaml"

	log.Println("Attempting to load "+datatype+" file: ", s3bucket, s3file, localfile)

	file, err := os.Create(localfile)
	if err != nil {
		log.Println(err)
	}

	numBytes, err := s3downloader.Download(file,
		&s3.GetObjectInput{
			Bucket: aws.String(s3bucket),
			Key:    aws.String(s3file),
		})

	if err != nil {
		log.Println(err)
	}

	log.Println("Downloaded", file.Name(), numBytes, "bytes", " in ", time.Since(start))

	bytes, err := ioutil.ReadFile(file.Name())
	if err != nil {
		return "local ReadFile failed", err
	}

	switch datatype {
	case "products":
		err = yaml.Unmarshal(bytes, &products)

		for _, item := range products {

			av, err := dynamodbattribute.MarshalMap(item)

			if err != nil {
				return "dynamodbattribute.MarshalMap error", err
			}
			DynamoDBPutItem(av, ddbtable)
		}

	case "categories":
		err = yaml.Unmarshal(bytes, &categories)

		for _, item := range categories {

			av, err := dynamodbattribute.MarshalMap(item)

			if err != nil {
				return "dynamodbattribute.MarshalMap error", err
			}
			DynamoDBPutItem(av, ddbtable)
		}
	default:
		log.Println("Unknown datatype " + datatype)
	}

	log.Println("Loaded in ", time.Since(start))

	return "data loaded from" + s3bucket + s3file + ddbtable + datatype + time.Since(start).String(), nil
}

// HandleRequest - handles Lambda request
func HandleRequest(ctx context.Context, event cfn.Event) (physicalResourceID string, data map[string]interface{}, err error) {

    fmt.Printf("Received event: %s!", event )

	if event.RequestType == "Create" || event.RequestType == "Update" {
		Bucket, _ := event.ResourceProperties["Bucket"].(string)
		File, _ := event.ResourceProperties["File"].(string)
		Table, _ := event.ResourceProperties["Table"].(string)
		Datatype, _ := event.ResourceProperties["Datatype"].(string)

		log.Println("Importing ", Bucket, File, " to ", Table, Datatype)
		returnstring, err = loadData(Bucket, File, Table, Datatype)
		data = map[string]interface{}{"return": returnstring}
		return returnstring, data, err
	}

	return "", map[string]interface{}{}, nil
}

func main() {
	lambda.Start(cfn.LambdaWrap(HandleRequest))
}
