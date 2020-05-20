// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"strconv"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/dynamodb/dynamodbattribute"
	"github.com/aws/aws-sdk-go/service/dynamodb/expression"

	yaml "gopkg.in/yaml.v2"
)

var products Products
var categories Categories
var exp_true bool = true

// Root/base URL to use when building fully-qualified URLs to product detail view.
var web_root_url = os.Getenv("WEB_ROOT_URL")

func init() {
}

func loadData() {

	err := loadProducts("/bin/data/products.yaml")
	if err != nil {
		log.Panic("Unable to load products file.")
	}

	err = loadCategories("/bin/data/categories.yaml")
	if err != nil {
		log.Panic("Unable to load category file.")
	}
}

func loadProducts(filename string) error {
	start := time.Now()

	log.Println("Attempting to load products file: ", filename)

	var r Products

	bytes, err := ioutil.ReadFile(filename)
	if err != nil {
		return err
	}

	err = yaml.Unmarshal(bytes, &r)
	if err != nil {
		return err
	}

	for _, item := range r {

		av, err := dynamodbattribute.MarshalMap(item)

		if err != nil {
			return err
		}

		input := &dynamodb.PutItemInput{
			Item:      av,
			TableName: aws.String(ddb_table_products),
		}

		_, err = dynamoclient.PutItem(input)
		if err != nil {
			fmt.Println("Got error calling PutItem:")
			fmt.Println(err.Error())

		}

	}
	log.Println("Products loaded in ", time.Since(start))

	return nil
}

func loadCategories(filename string) error {

	start := time.Now()

	log.Println("Attempting to load categories file: ", filename)

	var r Categories

	bytes, err := ioutil.ReadFile(filename)
	if err != nil {
		return err
	}

	err = yaml.Unmarshal(bytes, &r)
	if err != nil {
		return err
	}
	for _, item := range r {
		av, err := dynamodbattribute.MarshalMap(item)

		if err != nil {
			return err
		}

		input := &dynamodb.PutItemInput{
			Item:      av,
			TableName: aws.String(ddb_table_categories),
		}

		_, err = dynamoclient.PutItem(input)
		if err != nil {
			fmt.Println("Got error calling PutItem:")
			fmt.Println(err.Error())

		}

	}

	log.Println("Categories loaded in ", time.Since(start))

	return nil
}

func SetProductURL(p Product) Product {
	if len(web_root_url) > 0 {
		p.URL = web_root_url + "/#/product/" + p.ID
	}

	return p
}

func SetCategoryURL(c Category) Category {
	if len(web_root_url) > 0 {
		c.URL = web_root_url + "/#/category/" + c.Name
	}

	return c
}

// RepoFindProduct Function
func RepoFindProduct(id int) Product {

	var product Product

	log.Println("RepoFindProduct: ", strconv.Itoa(id), ddb_table_products)

	keycond := expression.Key("id").Equal(expression.Value(strconv.Itoa(id)))
	expr, err := expression.NewBuilder().WithKeyCondition(keycond).Build()
	// Build the query input parameters
	params := &dynamodb.QueryInput{
		ExpressionAttributeNames:  expr.Names(),
		ExpressionAttributeValues: expr.Values(),
		KeyConditionExpression:    expr.KeyCondition(),
		ProjectionExpression:      expr.Projection(),
		TableName:                 aws.String(ddb_table_products),
	}
	// Make the DynamoDB Query API call
	result, err := dynamoclient.Query(params)

	if err != nil {
		log.Println("get item error" + string(err.Error()))
		return product
	}

	err = dynamodbattribute.UnmarshalMap(result.Items[0], &product)

	if err != nil {
		panic(fmt.Sprintf("Failed to unmarshal Record, %v", err))
	}

	product = SetProductURL(product)

	log.Println("RepoFindProduct returning: ", product.Name, product.Category)

	// return the uniq item returned.
	return product
}

// RepoFindProductByCategory Function
func RepoFindProductByCategory(category string) Products {

	log.Println("RepoFindProductByCategory: ", category)

	var f Products

	keycond := expression.Key("category").Equal(expression.Value(category))
	proj := expression.NamesList(expression.Name("id"),
		expression.Name("category"),
		expression.Name("name"),
		expression.Name("image"),
		expression.Name("style"),
		expression.Name("description"),
		expression.Name("price"),
		expression.Name("gender_affinity"))
	expr, err := expression.NewBuilder().WithKeyCondition(keycond).WithProjection(proj).Build()

	if err != nil {
		log.Println("Got error building expression:")
		log.Println(err.Error())
	}

	// Build the query input parameters
	params := &dynamodb.QueryInput{
		ExpressionAttributeNames:  expr.Names(),
		ExpressionAttributeValues: expr.Values(),
		KeyConditionExpression:    expr.KeyCondition(),
		ProjectionExpression:      expr.Projection(),
		TableName:                 aws.String(ddb_table_products),
		IndexName:                 aws.String("category-index"),
	}
	// Make the DynamoDB Query API call
	result, err := dynamoclient.Query(params)

	if err != nil {
		log.Println("Got error QUERY expression:")
		log.Println(err.Error())
	}

	log.Println("RepoFindProductByCategory / items found =  ", len(result.Items))

	for _, i := range result.Items {
		item := Product{}

		err = dynamodbattribute.UnmarshalMap(i, &item)

		if err != nil {
			log.Println("Got error unmarshalling:")
			log.Println(err.Error())
		} else {
			item = SetProductURL(item)
		}

		f = append(f, item)
	}

	return f
}

// RepoFindFeatured Function
func RepoFindFeatured() Products {

	log.Println("RepoFindFeatured | featured=true")

	var f Products

	filt := expression.Name("featured").Equal(expression.Value("true"))
	expr, err := expression.NewBuilder().WithFilter(filt).Build()

	if err != nil {
		log.Println("Got error building expression:")
		log.Println(err.Error())
	}

	// Build the query input
	// using index for performance (few items are featured)
	params := &dynamodb.ScanInput{
		ExpressionAttributeNames:  expr.Names(),
		ExpressionAttributeValues: expr.Values(),
		FilterExpression:          expr.Filter(),
		ProjectionExpression:      expr.Projection(),
		TableName:                 aws.String(ddb_table_products),
		IndexName:                 aws.String("id-featured-index"),
	}
	// Make the DynamoDB Query API call
	result, err := dynamoclient.Scan(params)

	if err != nil {
		log.Println("Got error scan expression:")
		log.Println(err.Error())
	}

	log.Println("RepoFindProductFeatured / items found =  ", len(result.Items))

	for _, i := range result.Items {
		item := Product{}

		err = dynamodbattribute.UnmarshalMap(i, &item)

		if err != nil {
			log.Println("Got error unmarshalling:")
			log.Println(err.Error())
		} else {
			item = SetProductURL(item)
		}

		f = append(f, item)
	}

	return f
}

// TODO: implement some caching
func RepoFindALLCategories() Categories {

	log.Println("RepoFindALLCategories: ")

	var f Categories

	// Build the query input parameters
	params := &dynamodb.ScanInput{
		TableName: aws.String(ddb_table_categories),
	}
	// Make the DynamoDB Query API call
	result, err := dynamoclient.Scan(params)

	if err != nil {
		log.Println("Got error scan expression:")
		log.Println(err.Error())
	}

	log.Println("RepoFindALLCategories / items found =  ", len(result.Items))

	for _, i := range result.Items {
		item := Category{}

		err = dynamodbattribute.UnmarshalMap(i, &item)

		if err != nil {
			log.Println("Got error unmarshalling:")
			log.Println(err.Error())
		} else {
			item = SetCategoryURL(item)
		}

		f = append(f, item)
	}

	return f
}

// RepoFindALLProduct Function
func RepoFindALLProduct() Products {

	log.Println("RepoFindALLProduct: ")

	var f Products

	// Build the query input parameters
	params := &dynamodb.ScanInput{
		TableName: aws.String(ddb_table_products),
	}
	// Make the DynamoDB Query API call
	result, err := dynamoclient.Scan(params)

	if err != nil {
		log.Println("Got error scan expression:")
		log.Println(err.Error())
	}

	log.Println("RepoFindALLProduct / items found =  ", len(result.Items))

	for _, i := range result.Items {
		item := Product{}

		err = dynamodbattribute.UnmarshalMap(i, &item)

		if err != nil {
			log.Println("Got error unmarshalling:")
			log.Println(err.Error())
		} else {
			item = SetProductURL(item)
		}

		f = append(f, item)
	}

	return f
}
