// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import axios from "axios";

const serviceDomain = process.env.VUE_APP_VIDEOS_SERVICE_DOMAIN;
const servicePort = process.env.VUE_APP_VIDEOS_SERVICE_PORT;
const baseURL = `${serviceDomain}:${servicePort}`;

const connection = axios.create({
    baseURL
})

export default {
    async get() {
        let resp = await connection.get(`stream_details`)
        for (let stream of resp.data.streams) {
            stream['thumb_url'] = baseURL + '/' + stream['thumb_url'];
        }
        return resp;
    },
}