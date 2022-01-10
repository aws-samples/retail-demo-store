// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import axios from "axios";

const serviceDomain = process.env.VUE_APP_RECOMMENDATIONS_SERVICE_DOMAIN;
const servicePort = process.env.VUE_APP_RECOMMENDATIONS_SERVICE_PORT;
const baseURL = `${serviceDomain}:${servicePort}`;

const connection = axios.create({
    baseURL
})

const resource = "/favorite"

export default {
    getIsFavorited(username, productId) {
        const result = connection.get(`${resource}/by_user_and_product?username=${username}&productId=${productId}`)
        return result
    },
    getUserFavorites(username) {
        const result = connection.get(`${resource}/by_user?username=${username}`)
        return result
    },
    setIsFavorited(username, productId, favorited) {
        let payload = {
            username: username,
            productId: productId,
            favorited: favorited
        }
        return connection.post(`${resource}`, payload)
    },
}