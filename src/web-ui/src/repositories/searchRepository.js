// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import axios from "axios";

const serviceDomain = process.env.VUE_APP_SEARCH_SERVICE_DOMAIN;
const servicePort = process.env.VUE_APP_SEARCH_SERVICE_PORT;
const baseURL = `${serviceDomain}:${servicePort}`;

const connection = axios.create({
    baseURL
})

const resource = "/search";

export default {
    searchProducts(val) {
        if (!val || val.length == 0)
            throw "val required"
        return connection.get(`${resource}/products?searchTerm=${val}`)
    },
}