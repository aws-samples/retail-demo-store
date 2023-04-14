// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import axios from "axios";
import resolveBaseURL from './resolveBaseURL'

const baseURL = resolveBaseURL(
    import.meta.env.VITE_LOCATION_SERVICE_DOMAIN,
    import.meta.env.VITE_LOCATION_SERVICE_PORT,
    import.meta.env.VITE_LOCATION_SERVICE_PATH
)

const connection = axios.create({
    baseURL
})

export default {
    async get_store_location() {
        return await connection.get(`store_location`);
    },
    async get_customer_route() {
        return await connection.get(`customer_route`);
    },
    async get_cstore_location() {
        return await connection.get(`cstore_location`);
    },
    async get_cstore_route() {
        return await connection.get(`cstore_route`);
    },
}