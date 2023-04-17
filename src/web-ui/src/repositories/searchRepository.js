// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import axios from "axios";
import resolveBaseURL from './resolveBaseURL'

const baseURL = resolveBaseURL(
    import.meta.env.VITE_SEARCH_SERVICE_DOMAIN,
    import.meta.env.VITE_SEARCH_SERVICE_PORT,
    import.meta.env.VITE_SEARCH_SERVICE_PATH
)

const connection = axios.create({
    baseURL
})

const resource = "/search";

export default {
    searchProducts(val, size = 10, offset = 0) {
        if (!val || val.length == 0)
            throw "val required"
        return connection.get(`${resource}/products?searchTerm=${val}&size=${size}&offset=${offset}`)
    },
}