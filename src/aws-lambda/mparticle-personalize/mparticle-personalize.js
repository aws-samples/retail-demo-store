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
    // Load all of our variables from SSM
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
                var trackingId = param.Value; 
            } else if (param.Name === 'retaildemostore-product-recommendation-campaign-arn') {
                var campaignArn = param.Value;
            }
        }
        
        // Init mParticle libraries for the function invocation
        var mpApiInstance = new mParticle.EventsApi(new mParticle.Configuration(mpApiKey, mpApiSecret));
        console.log(`GOT PARAMS!`);
    } catch (e) {
        console.log("Error getting SSM parameter for loadbalancer.");
        console.log(e); 
        throw e;   
    }

    for (const record of event.Records) {
        const payloadString = Buffer.from(record.kinesis.data, 'base64').toString('ascii');
        const payload = JSON.parse(payloadString);
        const events = payload.events;
        
        console.log(`EVENTS: ${JSON.stringify(events)}`);
        
        let anonymousID = payload.mpid.toString();

        // First, get the mParticle user ID from the payload.  In this example, mParticle will send all the events
        // for a particular user in a batch to this lambda.
        var amazonPersonalizeUserId = anonymousID;
        if(payload.user_attributes && payload.user_attributes.amazonPersonalizeId)
            amazonPersonalizeUserId = payload.user_attributes.amazonPersonalizeId;

        /* 
        
        THIS APPEARS TO BE UNUSED??

        var amazonUserId = mpid;
        if(payload.user_identities){
            for (const identityRecord of payload.user_identities)
            {
                if(identityRecord.identity_type==="customer_id")
                    amazonUserId = identityRecord.identity;
            }
        }*/

        let params = {
            sessionId: payload.message_id,
            userId: amazonPersonalizeUserId,
            trackingId: trackingId,
            eventList: []
        };

        // Check for variant and assign one if not already assigned
        /*var variantAssigned;
        var variant;
        if(payload.user_attributes && payload.user_attributes.ml_variant) {
            variantAssigned = Boolean(payload.user_attributes.ml_variant); 
            variant = variantAssigned ? payload.user_attributes.ml_variant : Math.random() > 0.5 ? "A" : "B";
        }*/
        
        for (const e of events) {
            if (e.event_type === "commerce_event" && reportActions.indexOf(e.data.product_action.action) >= 0) {
                const timestamp = Math.floor(e.data.timestamp_unixtime_ms / 1000);
                const action = e.data.product_action.action;
                const event_id = e.data.event_id;
                const discount = Math.random() > 0.5 ? "Yes" : "No";
                for (const product of e.data.product_action.products) {
                    const purchasedItem = { itemId: product.id,
                                  discount: discount };
                    params.eventList.push({
                        properties: purchasedItem,
                        sentAt: timestamp,
                        eventId: event_id,
                        eventType: action
                    });
                }
            }
        }
        
        console.log(JSON.stringify(params));
        
        // Send the events to Amazon Personalize for training purposes
        try {
            await personalizeEvents.putEvents(params).promise();
        } catch (e) {
            console.log(`ERROR - Could not put events - ${e}`);
        }
        
        // Get Recommendations from Personalize for the user ID we got up top
        let recommendationsParams = {
            // Select campaign based on variant
            campaignArn: campaignArn,
            numResults: '5',
            userId: amazonPersonalizeUserId
        };
              
        try {
            var recommendations = await personalizeRuntime.getRecommendations(recommendationsParams).promise();
            console.log(`RECOMMENDATIONS - ${JSON.stringify(recommendations)}`);
        } catch (e) {
            console.log(`ERROR - Could not get recommendations - ${e}`);
        }
    }
};

/*        
        if(eventList.length > 10)
        {
            var lastTenRecords = eventList.length / 2;
            eventList = eventList.slice(lastTenRecords);
        }
        if (eventList.length > 0) {
            

            paramsPut.eventList = eventList;
            try{
                //put Events into Personalize
                await personalizeEvents.putEvents(paramsPut).promise().then(async function(data, err){
                    if (err) {
                        console.log(err);
                        console.log(err, err.stack);
                    } else {
                    console.log("AWS Personalization Put Events Successful");
                        return Promise.resolve(data); 
                    }
                });
            }catch(e){
                console.log("Put Event Personalize");
                console.log(e);
            }

            //get Recommendation from Personalize

            let params = {
                // Select campaign based on variant
                campaignArn: campaignArn,
                numResults: '5',
                userId: amazonPersonalizeUserId
              };
              console.log(params);

              try{
                var recommendationData = await personalizeRuntime.getRecommendations(params).promise().then(async function(data,err){
                    console.log("AWS Personalization Get Recommendation Start");
                    if (err) {
                        console.log(err);
                        console.log(err, err.stack);
                    }
                    if (!err)
                    {
                        return Promise.resolve(data.itemList); 
                        console.log("AWS Personalization Get Recommendation Successful");
                    }
                   
                   
                });
            }catch(e)
            {
                console.log("Get Event Personalize");
                console.log(e);    
            }
            
            
            let itemList = [];
            var productNameList = [];
            let promises = [];
            for (let item of recommendationData) {
                itemList.push(item.itemId);
                var productRequestURL = `${productsServiceURL}/products/id/${item.itemId}`;
                promises.push(axios.get(productRequestURL));
                promises.push(
                 axios.get(productRequestURL).then(response => {
                // do something with response
                productNameList.push(response.data.name);
                 })
                 );
             }
             
            await Promise.all(promises).then(() => console.log(productNameList));
              let batch = new mParticle.Batch(mParticle.Batch.Environment.development);

                        // if the customer profile is anonymous, we'll use the mParticle ID to tie this recommendation back to the anonymous user
                        // else we will use the customer Id which was provided earlier
                        if(customerId == null){
                            batch.mpid = mpid;
                        }
                        else{
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
                          let mp_callback = async function(error, data, response) {
                              if (error) {
                                  console.error(error);
                                } else {
                                  console.log('API called successfully.');
                                }
                              };
                        
                         // Send to Event to mParticle
                          await mpApiInstance.bulkUploadEvents(body, mp_callback);
        }
    }
};
*/
