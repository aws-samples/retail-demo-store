// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
import { get, post } from 'aws-amplify/api';

const apiName = 'demoServices';

const popular = "/popular"
const related = "/related"
const recommendations = "/recommendations"
const rerank = "/rerank"
const chooseDiscounted = "/choose_discounted"
const couponOffer = "/coupon_offer"
const experimentOutcome = "/experiment/outcome"

export default {
    async getPopularProducts(userID, currentItemID, numResults, feature) {
        let params = {
            userID: userID,
            currentItemID: currentItemID,
            numResults: numResults,
            feature: feature
        }
        const restOperation = get({
            apiName: apiName,
            path: popular,
            options: {
                queryParams: params
              }
        });
        return restOperation.response;
    },
    async getRelatedProducts(userID, currentItemID, currentItemCategory, numResults, feature) {
        let params = {
            userID: userID,
            currentItemID: currentItemID,
            currentItemCategory: currentItemCategory,
            numResults: numResults,
            feature: feature
        }
        const restOperation = get({
            apiName: apiName,
            path: related,
            options: {
                queryParams: params
              }
        });
        return restOperation.response;
    },
    async getRecommendationsForUser(userID, currentItemID, numResults, feature) {
        let params = {
            userID: userID,
            currentItemID: currentItemID,
            numResults: numResults,
            feature: feature
        }
        const restOperation = get({
            apiName: apiName,
            path: recommendations,
            options: {
                queryParams: params
              }
        });
        return restOperation.response;
    },
    async getRerankedItems(userID, items, feature) {
        let payload = {
            userID: userID,
            items: items,
            feature: feature
        }
        const restOperation = post({
            apiName: apiName,
            path: rerank,
            options: {
                body: payload
              }
        });
        return restOperation.response;
    },
    async chooseDiscounts(userID, items, feature) {
        let payload = {
            userID: userID,
            items: items,
            feature: feature
        }
        const restOperation = post({
            apiName: apiName,
            path: chooseDiscounted,
            options: {
                body: payload
              }
        });
        const { body } = await restOperation.response;
        return body.json(); // inserts discount and discounted keys into items
    },
    async getCouponOffer(userID) {
        const restOperation = get({
            apiName: apiName,
            path: couponOffer,
            options: {
                queryParams: {
                    userID: userID
                }
              }
        });
        const { body } = await restOperation.response;
        return body.json();
    },
    async recordExperimentOutcome(correlationId) {
        let payload = {
            correlationId: correlationId
        }
        const restOperation = post({
            apiName: apiName,
            path: experimentOutcome,
            options: {
                body: payload
              }
        });
        const { body } = await restOperation.response;
        return body.json();
    }
}