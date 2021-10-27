// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

const AWS = require('aws-sdk');
const JSONBig = require('json-bigint')({ storeAsString: true });
const mParticle = require('mparticle');
const trackingId = process.env.PERSONALISE_TRACKING_ID;
const campaignArn = process.env.PERSONALISE_CAMPAIGN_ARN;
const reportActions = ["purchase", "view_detail", "add_to_cart", "checkout","add_to_wishlist"];
const mpApiKey = process.env.MPARTICLE_S2S_API_KEY;
const mpApiSecret = process.env.MPARTICLE_S2S_SECRET_KEY;
const personalizeEvents = new AWS.PersonalizeEvents();
const personalizeRuntime = new AWS.PersonalizeRuntime();
const mpApiInstance = new mParticle.EventsApi(new mParticle.Configuration(mpApiKey, mpApiSecret));
const axios = require('axios');

exports.handler = function (event, context) {
    var eventList = [];
    var mpid;
    
    // TODO:  ADD SERVICE DISCOVERY CALL HERE TO GET THE PRODUCTS SERVICE FOR LOOKUP LATER
    
    for (const record of event.Records) {
        const payloadString = Buffer.from(record.kinesis.data, 'base64').toString('ascii');
        const payload = JSON.parse(payloadString);
        const events = payload.events;
        mpid = payload.mpid.toString();

        // First, get the mParticle user ID from the payload.  In this example, mParticle will send all the events
        // for a particular user in a batch to this lambda.

        var amazonPersonalizeUserId = mpid;
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

        const sessionId = payload.message_id;
        let params = {
            sessionId: sessionId,
            userId: amazonPersonalizeUserId,
            trackingId: trackingId
        };

        // Check for variant and assign one if not already assigned
        var variantAssigned;
        var variant;
        if(payload.user_attributes && payload.user_attributes.ml_variant) {
            variantAssigned = Boolean(payload.user_attributes.ml_variant); 
            variant = variantAssigned ? payload.user_attributes.ml_variant : Math.random() > 0.5 ? "A" : "B";
        }
        for (const e of events) {
            if (e.event_type === "commerce_event" && reportActions.indexOf(e.data.product_action.action) >= 0) {
                const timestamp = Math.floor(e.data.timestamp_unixtime_ms / 1000);
                const action = e.data.product_action.action;
                const event_id = e.data.event_id;
                const discount = Math.random() > 0.5 ? "Yes" : "No";
                for (const product of e.data.product_action.products) {
                    const obj = {itemId: product.id,discount: discount};

                    if(eventList.length > 10){
                        eventList.shift();
                        
                    }
                    eventList.push({
                        properties: obj,
                        sentAt: timestamp,
                        eventId: event_id,
                        eventType: action
                    });
                }
            }
        }

        if(eventList.length > 10)
        {
            var lastTenRecords = eventList.length / 2;
            eventList = eventList.slice(lastTenRecords);
        }
        if (eventList.length > 0) {
            params.eventList = eventList;
                personalizeEvents.putEvents(params, async function(err, data) {
                if (err) {
                    console.log(err);
                    console.log(err, err.stack);
                } else {
                    //getProductPersonalization
                    let params = {
                      // Select campaign based on variant
                      campaignArn: campaignArn,
                      numResults: '5',
                      userId: amazonPersonalizeId
                    };
                    personalizeRuntime.getRecommendations(params, async function(err, data) {
                      if (err) {
                        console.log(err);
                          console.log(err, err.stack);
                      } else {
                          let batch = new mParticle.Batch(mParticle.Batch.Environment.development);
                          batch.mpid = mpid;
                          let itemList = [];
                          var productNameList = [];
                          let promises = [];
                          for (let item of data.itemList) {
                              itemList.push(item.itemId);
                              var url = "https://products.stridesolution.com/products/id/"+item.itemId;
                              
                              promises.push(axios.get(url));
                              promises.push(
                                axios.get(url).then(response => {
                                  // do something with response
                                  productNameList.push(response.data.name);
                                })
                              );
                          }

                          await Promise.all(promises).then(() => console.log(productNameList));
                          batch.user_attributes = {};
                          batch.user_attributes.product_recs = itemList;
                          // Record variant on mParticle user profile
                          if (!variantAssigned) {
                              batch.user_attributes.ml_variant = variant
                              batch.user_attributes.product_recs_name=productNameList;
                          }
    
                          let event = new mParticle.AppEvent(mParticle.AppEvent.CustomEventType.other, 'AWS Product Personalization Recs Update');
                          event.custom_attributes = {product_recs: itemList.join()};
                          batch.addEvent(event);
                          var body = [batch]; // {[Batch]} Up to 100 Batch objects
                          
                          let mp_callback = async function(error, data, response) {
                              if (error) {
                                  console.error(error);
                                } else {
                                  console.log('API called successfully.');
                                }
                              };
                        
                          mpApiInstance.bulkUploadEvents(body, mp_callback);
                      }
                    });
                }
            });
        }
    }
};