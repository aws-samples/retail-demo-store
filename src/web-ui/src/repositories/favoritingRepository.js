// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import axios from "axios";

const serviceDomain = process.env.VUE_APP_RECOMMENDATIONS_SERVICE_DOMAIN;
const servicePort = process.env.VUE_APP_RECOMMENDATIONS_SERVICE_PORT;
const baseURL = `${serviceDomain}:${servicePort}`;

const connection = axios.create({
    baseURL
})

export default {
    getIsFavorited(username, productId) {
        const result = connection.get(`/is_favorited?username=${username}&productId=${productId}`)
        return result
    },
    getUserFavorites(username) {
        const result = connection.get(`/favorites?username=${username}`)
        return result
    },
    setIsFavorited(username, productId, favorited) {
        const payload = {
            username: username,
            productId: productId,
            favorite: favorited
        }
        return connection.post(`/favorite`, payload)
    },
}