// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import axios from "axios";
import ProductsRepository from "./productsRepository"

const serviceDomain = process.env.VUE_APP_RECOMMENDATIONS_SERVICE_DOMAIN;
const servicePort = process.env.VUE_APP_RECOMMENDATIONS_SERVICE_PORT;
const baseURL = `${serviceDomain}:${servicePort}`;

const connection = axios.create({
    baseURL
})

export default {
    getAlerts(username) {
        const result = connection.get(`/customer_alerts?username=${username}`)
        return result
    },
    async getCampaignDetails(campaignName, username) {

       switch(campaignName) {
           case "360furniture": {
               const { data } = await ProductsRepository.getProductsByCategory('furniture')
               let intermediate = data
               if (username && username.length>0 && /lana/.test(username)) {
                    intermediate = intermediate.filter(
                        (product)=>/SADDLE|LEATHER|KHAKI/.test(product['name'].toUpperCase()))
                }
               const campaignDetails = {"title": "360 Day Furniture Sale!",
                                        "products": intermediate,
                                        "subtitle": ""}
               return campaignDetails
           }
           default: {
               return null;
           }
       }

    }
}