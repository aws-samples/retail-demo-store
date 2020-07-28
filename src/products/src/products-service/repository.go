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
	guuuid "github.com/google/uuid"
	"github.com/jinzhu/copier"
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
func RepoFindProduct(id string) Product {

	var product Product

	log.Println("RepoFindProduct: ", id, ddb_table_products)

	keycond := expression.Key("id").Equal(expression.Value(id))
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
		log.Println("get item error " + string(err.Error()))
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

func RepoUpdateProduct(id string, updated_product Product) Product {

	var existing_product Product
	existing_product = RepoFindProduct(id)
	updated_product.URL = "" // URL is generated so ignore if specified
	log.Println("UpdateProducts from", existing_product, updated_product)

	copier.Copy(&existing_product, &updated_product)
	log.Println("after Copier", updated_product)

	av, err := dynamodbattribute.MarshalMap(updated_product)

	if err != nil {
		fmt.Println("Got error calling dynamodbattribute MarshalMap:")
		fmt.Println(err.Error())
		return existing_product
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

	return updated_product

}

func RepoUpdateInventoryDelta(id string, StockDelta int) Product {

	log.Println("RepoUpdateProduct for id, new quantity: ", id, StockDelta)

	var product Product

	// Get the current product
	product = RepoFindProduct(id)
	log.Println("current product stock : ", product.CurrentStock)

	if product.CurrentStock+StockDelta < 0 {
		// ensuring we don't get negative stocks, just down to zero stock
		StockDelta = -product.CurrentStock
	}

	input := &dynamodb.UpdateItemInput{
		ExpressionAttributeValues: map[string]*dynamodb.AttributeValue{
			":stockdelta": {
				N: aws.String(strconv.Itoa(StockDelta)),
			},
			":currstock": {
				N: aws.String(strconv.Itoa(product.CurrentStock)),
			},
		},
		TableName: aws.String(ddb_table_products),
		Key: map[string]*dynamodb.AttributeValue{
			"id": {
				S: aws.String(id),
			},
			"category": {
				S: aws.String(product.Category),
			},
		},
		ReturnValues:        aws.String("UPDATED_NEW"),
		UpdateExpression:    aws.String("set current_stock = current_stock + :stockdelta"),
		ConditionExpression: aws.String("current_stock = :currstock"),
	}

	_, err = dynamoclient.UpdateItem(input)
	if err != nil {
		fmt.Println("Got error calling UpdateItem:")
		fmt.Println(err.Error())
	}
	product.CurrentStock = product.CurrentStock + StockDelta
	// return the updated product
	return product

}

func RepoNewProduct(new_product Product) Product {

	log.Println("RepoNewProduct -->", new_product)

	new_product.ID = guuuid.New().String()
	av, err := dynamodbattribute.MarshalMap(new_product)

	if err != nil {
		fmt.Println("Got error calling dynamodbattribute MarshalMap:")
		fmt.Println(err.Error())
		return new_product
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

	return new_product
}
