// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

const AWS = require('aws-sdk');
const SSM = new AWS.SSM();
const mParticle = require('mparticle');
const reportActions = ["purchase", "view_detail", "add_to_cart", "checkout","add_to_wishlist"];
const personalizeEvents = new AWS.PersonalizeEvents();
const personalizeRuntime = new AWS.PersonalizeRuntime();
const axios = require('axios');

exports.handler = async function (event, context) {
    // Load all of our environment variables from SSM
    try {
        let params = {
            Names: ['/retaildemostore/services_load_balancers/products',
                    '/retaildemostore/webui/mparticle_s2s_api_key',
                    '/retaildemostore/webui/mparticle_s2s_secret_key',
                    'retaildemostore-personalize-event-tracker-id',
                    'retaildemostore-product-recommendation-campaign-arn'],
            WithDecryption: false
        };
        let responseFromSSM = await SSM.getParameters(params).promise();
        
        for(const param of responseFromSSM.Parameters) {
            if( param.Name === '/retaildemostore/services_load_balancers/products') {
                var productsServiceURL = param.Value;
            } else if (param.Name === '/retaildemostore/webui/mparticle_s2s_api_key') {
                var mpApiKey = param.Value;
            } else if (param.Name === '/retaildemostore/webui/mparticle_s2s_secret_key') {
                var mpApiSecret = param.Value;
            } else if (param.Name === 'retaildemostore-personalize-event-tracker-id') {
                var personalizeTrackerID = param.Value; 
            } else if (param.Name === 'retaildemostore-product-recommendation-campaign-arn') {
                var personalizeCampaignARN = param.Value;
            }
        }
        
        // Init mParticle libraries for the function invocation
        var mpApiInstance = new mParticle.EventsApi(new mParticle.Configuration(mpApiKey, mpApiSecret));
    } catch (e) {
        console.log("Error getting SSM parameter for loadbalancer.");
        console.log(e); 
        throw e;   
    }

    for (const record of event.Records) {
        const payloadString = Buffer.from(record.kinesis.data, 'base64').toString('ascii');
        const payload = JSON.parse(payloadString);
        const events = payload.events;
        var amazonPersonalizeUserId;
        
        // First, get the mParticle user ID from the events payload.  In this example, mParticle will send all the events
        // for a particular user in a batch to this lambda.
        // retreive the mParticle user id which is available for anonymous and known customer profiles
        var anonymousID = events[0].data.custom_attributes.mpid.toString();
        
        // if the customer profile is known then replace the Amazon Personalize User id with the actual
        // personalize Id captured from the user's profile
        if(payload.user_attributes && payload.user_attributes.amazonPersonalizeId)
            amazonPersonalizeUserId = payload.user_attributes.amazonPersonalizeId; 
        else
            amazonPersonalizeUserId = anonymousID;
        // Verify in mParticle's payload if there is a customer id set within the customer profile
        // this will be used for identity resolution later on within mParticle.
        var customerId = null;
        if(payload.user_identities){
                for (const identityRecord of payload.user_identities)
                {
                    if(identityRecord.identity_type==="customer_id")
                        customerId = identityRecord.identity; 
                }
            }

        var params = {
            sessionId: payload.message_id,
            userId: amazonPersonalizeUserId,
            trackingId: personalizeTrackerID,
            eventList: []
        };

        for (const e of events) {
            if (e.event_type === "commerce_event" && reportActions.indexOf(e.data.product_action.action) >= 0) {
                const timestamp = Math.floor(e.data.timestamp_unixtime_ms / 1000);
                const action = e.data.product_action.action;
                const event_id = e.data.event_id;

                // Build the list of events for the user session...
                for (const product of e.data.product_action.products) {
                    const purchasedItem = { itemId: product.id, discount:"No" };
                    params.eventList.push({
                        properties: purchasedItem,
                        sentAt: timestamp,
                        eventId: event_id,
                        eventType: action
                    });
                }
            }
        }
        
        // Send the events to Amazon Personalize for training purposes
        try {
            await personalizeEvents.putEvents(params).promise();
        } catch (e) {
            console.log(`ERROR - Could not put events - ${e}`);
        }
        
        // Get Recommendations from Personalize for the user ID we got up top
        let recommendationsParams = {
            // Select campaign based on variant
            campaignArn: personalizeCampaignARN,
            numResults: '5',
            userId: amazonPersonalizeUserId
        };
              
        try {
            var recommendations = await personalizeRuntime.getRecommendations(recommendationsParams).promise();
        } catch (e) {
            console.log(`ERROR - Could not get recommendations - ${e}`);
        }
            
        // Reverse Lookup the product ids to actual product name using the product service url
        let itemList = [];
        var productNameList = [];
        for (let item of recommendations.itemList) {
            itemList.push(item.itemId);
            var productRequestURL = `${productsServiceURL}/products/id/${item.itemId}`;
            var productInfo = await axios.get(productRequestURL);
            productNameList.push(productInfo.data.name);
        }

            
        //build the mParticle object and send it to mParticle
        let batch = new mParticle.Batch(mParticle.Batch.Environment.development);

        // if the customer profile is anonymous, we'll use the mParticle ID to tie this recommendation back to the anonymous user
        // else we will use the customer Id which was provided earlier
        if(customerId == null) {
            batch.mpid = anonymousID;
        } else {
            batch.user_identities = new mParticle.UserIdentities();
            batch.user_identities.customerid = customerId; // identify the user via the customer id 
        }    
        batch.user_attributes = {};
        batch.user_attributes.product_recs = itemList;
        batch.user_attributes.product_recs_name=productNameList;
        
        
        // Create an Event Object using an event type of Other
        let event = new mParticle.AppEvent(mParticle.AppEvent.CustomEventType.other, 'AWS Product Personalization Recs Update');
        event.custom_attributes = {product_recs: itemList.join()};
        batch.addEvent(event);
        var body = [batch]; // {[Batch]} Up to 100 Batch objects
        console.log(event);
        console.log(batch);
        let mp_callback = function(error, data, response) {
            if (error) {
                console.error(error);
            } else {
                console.log('API called successfully.');
            }
        };
    
        // Send to Event to mParticle
        try{
             await mpApiInstance.uploadEvents(body, mp_callback);
        }catch(e)
        {
              console.log("Error Uploading Recommendations back to mParticle.");
             console.log(e); 
                throw e;   
        }
    }
};
