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

// Per the Amplitude Recommendation API spec:  https://developers.amplitude.com/docs/user-profile-api
// and the Recommendations spec:  https://help.amplitude.com/hc/en-us/articles/360059626072-Use-recommendations-in-personalization-campaigns 
const amplitudeAPI = axios.create({
    baseURL: 'https://profile-api.amplitude.com',
    headers: { 'Authorization': `Api-Key ${process.env.VUE_APP_AMPLITUDE_SECRET_API_KEY}`}
});

const popular = "/popular"
const related = "/related"
const recommendations = "/recommendations"
const rerank = "/rerank"
const chooseDiscounted = "/choose_discounted"
const couponOffer = "/coupon_offer"
const experimentOutcome = "/experiment/outcome"
const amplitudeUserProfile = "/v1/userprofile"

export default {
    getPopularProducts(userID, currentItemID, numResults, feature) {
        let params = {
            userID: userID,
            currentItemID: currentItemID,
            numResults: numResults,
            feature: feature
        }

        return connection.get(popular, { params: params })
    },
    getRelatedProducts(userID, currentItemID, currentItemCategory, numResults, feature) {
        let params = {
            userID: userID,
            currentItemID: currentItemID,
            currentItemCategory: currentItemCategory,
            numResults: numResults,
            feature: feature
        }

        return connection.get(related, { params: params })
    },

    // TODO:  Add Amplitude Profile API switch here
    getAmplitudeRecommendationsForUser(userID) {
        let ampID = String(userID).padStart(5, '0');
        console.log(`Getting Amplitude recommendations for userID ${ampID}`);
        let params = {
            user_id: ampID,
            rec_id: process.env.VUE_APP_AMPLITUDE_RECOMMENDATION_ID
        };

        return amplitudeAPI.get(amplitudeUserProfile, { params: params });
    },

    getRecommendationsForUser(userID, currentItemID, numResults, feature) {
        let params = {
            userID: userID,
            currentItemID: currentItemID,
            numResults: numResults,
            feature: feature
        }

        return connection.get(recommendations, { params: params })
    },
    getRerankedItems(userID, items, feature) {
        let payload = {
            userID: userID,
            items: items,
            feature: feature
        }

        return connection.post(rerank, payload)
    },
    chooseDiscounts(userID, items, feature) {
        let payload = {
            userID: userID,
            items: items,
            feature: feature
        }
        return connection.post(chooseDiscounted, payload) // inserts discount and discounted keys into items
    },
    getCouponOffer(userID) {
        return connection.get(`${couponOffer}?userID=${userID}`)
    },
    recordExperimentOutcome(correlationId) {
        let payload = {
            correlationId: correlationId
        }
        return connection.post(experimentOutcome, payload)
    }
}