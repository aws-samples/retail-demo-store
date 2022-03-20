// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import axios from "axios";
import resolveBaseURL from './resolveBaseURL'

const baseURL = resolveBaseURL(
    process.env.VUE_APP_RECOMMENDATIONS_SERVICE_DOMAIN,
    process.env.VUE_APP_RECOMMENDATIONS_SERVICE_PORT,
    process.env.VUE_APP_RECOMMENDATIONS_SERVICE_PATH
)

const connection = axios.create({
    baseURL
})

const popular = "/popular"
const related = "/related"
const recommendations = "/recommendations"
const rerank = "/rerank"
const chooseDiscounted = "/choose_discounted"
const couponOffer = "/coupon_offer"
const experimentOutcome = "/experiment/outcome"
const resetTracker = "/reset/realtime"

export default {
    getPopularProducts(userID, currentItemID, numResults, feature) {
        return connection.get(`${popular}?userID=${userID}&currentItemID=${currentItemID}&numResults=${numResults}&feature=${feature}&fullyQualifyImageUrls=1`)
    },
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
    getCouponOffer(userID) {
        return connection.get(`${couponOffer}?userID=${userID}`)
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