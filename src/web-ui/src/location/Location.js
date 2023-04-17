// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { RestClient } from '@aws-amplify/api-rest';

const resourceName = import.meta.env.VITE_LOCATION_RESOURCE_NAME;
const awsRegion = import.meta.env.VITE_AWS_REGION

class Location {
    region = awsRegion
    api = new RestClient({
        headers: { accept: 'application/json' },
    });

    async getRequest(service, endpoint, nextToken = null) {
        const queryStringParameters = {};
        if (nextToken) {
            queryStringParameters['next-token'] = nextToken;
        }

        return await this.api.get(
            {
                endpoint: `https://${service}.geo.${this.region}.amazonaws.com${endpoint}`,
                service: 'geo',
                region: this.region,
            },
            { queryStringParameters }
        );
    }

    async postRequest(service, endpoint, body = {}) {
        return await this.api.post(
            {
                endpoint: `https://${service}.geo.${this.region}.amazonaws.com${endpoint}`,
                service: 'geo',
                region: this.region,
            }, { body }
        );
    }

    async getMaps(nextToken = null) {
        return this.getRequest('maps', '/maps/v0/maps', nextToken)
    }

    async getGeofences() {
        return this.postRequest('geofencing', `/geofencing/v0/collections/${resourceName}/list-geofences`)
    }

    async getDevicePositions(deviceIds) {
        const query = new URLSearchParams();
        deviceIds.forEach(deviceId => {
            query.append('device-ids', deviceId)
        })

        return this.getRequest('tracking', `/tracking/v0/trackers/${resourceName}/positions?${query}`)
    }

    async updateDevicePositions(positions) {
        const timestamp = new Date();
        const isoString = timestamp.toISOString()

        let body = {Updates: []}
        positions.map(position => {
            body.Updates.push({...position, SampleTime: isoString})
        })

        return this.postRequest('tracking', `/tracking/v0/trackers/${resourceName}/positions`, body)
    }
}

export default Location;