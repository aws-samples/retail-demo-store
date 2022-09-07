/*
  Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.
  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

const AWS = require('aws-sdk');
const SSM = new AWS.SSM();
const personalizeEvents = new AWS.PersonalizeEvents();
const personalizeRuntime = new AWS.PersonalizeRuntime();

exports.tealiumPersonalizeEventHandler = async (event) => {
  console.log('--- Tealium Event INCOMING ---');
  console.log(JSON.stringify(event, null, 2));

  // Load all of our environment variables from SSM
  try {
    let params = {
      Names: ['/retaildemostore/services_load_balancers/products',
        '/retaildemostore/personalize/event-tracker-id',
        '/retaildemostore/personalize/recommended-for-you-arn'],
      WithDecryption: false
    };
    let responseFromSSM = await SSM.getParameters(params).promise();

    for (const param of responseFromSSM.Parameters) {
      if (param.Name === '/retaildemostore/services_load_balancers/products') {
        var productsServiceURL = param.Value;
      } else if (param.Name === '/retaildemostore/personalize/event-tracker-id') {
        var personalizeTrackerID = param.Value;
      } else if (param.Name === '/retaildemostore/personalize/recommended-for-you-arn') {
        var personalizeARN = param.Value;
      }
    }
  } catch (e) {
    console.log("Error getting SSM parameters.");
    console.log(e);
    throw e;
  }

  var amazonPersonalizeUserId;

  // First, get the Tealium user ID from the events payload.  In this example, Tealium will send all the events
  // for a particular user in a batch to this lambda.
  var anonymousID = event.detail.visitor_id;

  // if the customer profile is known then replace the Amazon Personalize User id with the actual
  // personalize Id captured from the user's profile
  if (event.detail.udo.userId)
    amazonPersonalizeUserId = event.detail.udo.userId;
  else
    amazonPersonalizeUserId = anonymousID;

  var params = {
    sessionId: event.detail.udo.tealium_session_id,
    userId: amazonPersonalizeUserId,
    trackingId: personalizeTrackerID,
    eventList: []
  };

  const timestamp = Math.floor(e.data.timestamp_unixtime_ms / 1000);
  const action = event.detail.udo.;
  const event_id = e.data.event_id;

  // Build the list of events for the user session...
  for (const product of e.data.product_action.products) {
    const purchasedItem = { itemId: product.id, discount: "No" };
    params.eventList.push({
      properties: purchasedItem,
      sentAt: timestamp,
      eventId: event_id,
      eventType: action
    });
  }

  // Send the events to Amazon Personalize for training purposes
  try {
    await personalizeEvents.putEvents(params).promise();
  } catch (e) {
    console.log(`ERROR - Amazon Personalize putEvents: ${e}`);
  }
}