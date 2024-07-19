// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { Amplify } from 'aws-amplify';
import { get, post } from 'aws-amplify/api';

const existingConfig = Amplify.getConfig();

const resourceName = import.meta.env.VITE_LOCATION_RESOURCE_NAME;
const awsRegion = import.meta.env.VITE_AWS_REGION

Amplify.configure({
    ...existingConfig,
    API: {
      ...existingConfig.API,
      REST: {
        ...existingConfig.API?.REST,
        maps: {
          endpoint:
            `https://maps.geo.${awsRegion}.amazonaws.com$`,
          region: awsRegion,
          service: 'geo'
        },
        geofencing: {
            endpoint:
              `https://geofencing.geo.${awsRegion}.amazonaws.com`,
            region: awsRegion,
            service: 'geo'
        },
        tracking: {
            endpoint:
              `https://tracking.geo.${awsRegion}.amazonaws.com`,
            region: awsRegion,
            service: 'geo'
        }
      }
    }
  });

class Location {

    async getRequest(service, endpoint, nextToken = null) {
        const queryStringParameters = {};
        if (nextToken) {
            queryStringParameters['next-token'] = nextToken;
        }
        const restOperation = get({ 
            apiName: service,
            path: endpoint,
            options: {
                queryParams: queryStringParameters,
                headers: {
                    accept: 'application/json'
                }
            }
          });
        return await restOperation.response
        
    }

    async postRequest(service, endpoint, payload = {}) {
        const restOperation = post({ 
            apiName: service,
            path: endpoint,
            options: {
                headers: {
                    accept: 'application/json'
                },
                body: payload
            }
          });
        const { body } = await restOperation.response;
        return await body.json()
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

        let payload = {Updates: []}
        positions.map(position => {
          payload.Updates.push({...position, SampleTime: isoString})
        })

        return this.postRequest('tracking', `/tracking/v0/trackers/${resourceName}/positions`, payload)
    }
}

export default Location;