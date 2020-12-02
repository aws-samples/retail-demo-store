// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import axios from "axios";

const serviceDomain = process.env.VUE_APP_RECOMMENDATIONS_SERVICE_DOMAIN;
const servicePort = process.env.VUE_APP_RECOMMENDATIONS_SERVICE_PORT;
const baseURL = `${serviceDomain}:${servicePort}`;

const connection = axios.create({
    baseURL
})

const related = "/related"
const recommendations = "/recommendations"
const rerank = "/rerank"
const chooseDiscounted = "/choose_discounted"
const experimentOutcome = "/experiment/outcome"
const resetTracker = "/reset/realtime"

export default {
    getRelatedProducts(userID, currentItemID, numResults, feature) {
        return connection.get(`${related}?userID=${userID}&currentItemID=${currentItemID}&numResults=${numResults}&feature=${feature}&fullyQualifyImageUrls=1`)
    }, 
    getRecommendationsForUser(userID, currentItemID, numResults, feature) {
        return connection.get(`${recommendations}?userID=${userID}&currentItemID=${currentItemID}&numResults=${numResults}&feature=${feature}&fullyQualifyImageUrls=1`)
    }, 
    getRerankedItems(userID, items, feature) {
        let payload = {
            userID: userID,
            items: items,
            feature: feature
        }
        
        return connection.post(`${rerank}`, payload)
    },
    chooseDiscounts(userID, items, feature) {
        let payload = {
            userID: userID,
            items: items,
            feature: feature
        }
        return connection.post(`${chooseDiscounted}`, payload) // inserts discount and discounted keys into items
    },
    recordExperimentOutcome(correlationId) {
        let payload = {
            correlationId: correlationId
        }
        return connection.post(`${experimentOutcome}`, payload)
    },
    resetRealtimeRecommendations() {
        return connection.post(`${resetTracker}`, {})
    }
}