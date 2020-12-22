// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import axios from "axios";

const serviceDomain = process.env.VUE_APP_LOCATION_SERVICE_DOMAIN;
const servicePort = process.env.VUE_APP_LOCATION_SERVICE_PORT;
const baseURL = `${serviceDomain}:${servicePort}`;

const connection = axios.create({
    baseURL
})

export default {
    async get_store_location() {
        return await connection.get(`store_location`);
    },
    async get_customer_route() {
        return await connection.get(`customer_route`);
    }
}
