// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import axios from "axios";
import resolveBaseURL from './resolveBaseURL'

const baseURL = resolveBaseURL(
    import.meta.env.VITE_VIDEOS_SERVICE_DOMAIN,
    import.meta.env.VITE_VIDEOS_SERVICE_PORT,
    import.meta.env.VITE_VIDEOS_SERVICE_PATH
)

const connection = axios.create({
    baseURL
})

export default {
    async get() {
        return await connection.get(`stream_details`)
    },
}