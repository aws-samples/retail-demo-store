
  
# Retail Geofencing and Location-aware Personalization




is an Amazon provision of maps, location indexing, geofencing, user tracking, and routing.
Geofencing can be used to
set off chains of events just when they need to be set off
- when your customer is in the right place, at the right time.
In this demo we use it together with the ecommerce platform and Amazon Pinpoint
to engage customers when they approach physical stores.



Customers are inspired to opt in to share their location by being
provided with personalized offers. These offers can be related to
customer preferences, local stock levels, and more. In this demo
we use Amazon Personalize to select an offer to show to a consumer
that can be redeemed in-store. The consumer has the extra convenience
and we have enaged with them in a targeted fashion and, moreover,
attracted them into our bricks and mortar store where the experience
will be, naturally, more personal than online.


There is also an in-store interface that shows a sample view for store
staff showing orders that are about to be collected, and transactional messaging
for user and store staff around pickup that is triggered by the user approaching
the store for pickup.


Using the Location Services Demo

  

To use the Amazon Location functionality, Location Services must be enabled in your region.
First, ensure you are deploying Retail Demo Store in a region in which
Location is enabled. Next, enable

and "Deploy personalized offers and
pickup notices using Location Services geofencing"
when deploying or updating the solution from CloudFormation.
A Location geofence will be set up for you.
  
  
From any Retail Demo Store "Shop" menu You can access the Location "In-Store View"
where you can see orders made to be collected from in-store. From there you can navigate to
"Location Geofence" where you can see the Location Services-provided map and simulated user
- from here you can initiate
simulations of users travelling close to the default configured store either during a scenario
where Location Services can be used to enable a quick collection of bought products
and related messaging using Pinpoint Transactional Messaging to email, SMS or web
("collection" scenario), or where the user might be inspired to enter the store to make a
new purhcase through the triggering of personalised messages sent using Pinpoint Campaigns
to email, SMS and web, either containing offers chosen with Amazon Personalize or containing
notices about unfinished shopping carts ("purchase" scenario).
  
  
  
If you are in the email "sandbox" for Pinpoint, then all recipient
emails must be verified according to the below process, to ensure
that the emails will be sent.
  
  
After deploying the demo, navigate to your Pinpoint application
called "retaildemostore" in the UI Console
(https://console.aws.amazon.com/pinpoint/home making sure that the region
is the same one in which you deployed your
demo).



Ensure the email channel for the project is set to "Enabled"
(this will be set after Amazon Personalize campaigns
are finished deploying, but you may set it beforehand).

For the email that you used when you deployed the solution
under "Reply-To email address", ensure that the email
address is verified. Select this as your "Default sender address".

For every email to which you plan to send emails,
ensure that the email address is verified.


  
  
Note that you can manage your email and SMS limits within the
"Settings" > "Email" and "Settings" > "SMS and voice"
menus available under your Pinpoint project.
Also note that there are additional limits imposed when your account is
in the Pinpoint "sandbox".
  
  
  
Ensure any phone number in the Pinpoint database
to which you intend to send promotional messages (the "purchase" journey
above - for the "collection" journey, the phone number will be recorded against the order)
has opted in to receive promotional messages. For more information on how to ensure this,
see the  section in the

Pinpoint messaging workshop.
In brief, you need to (in the USA):
  
  
Subscribe to a long-code that supports SMS through the Pinpoint UI so that Pinpoint has a number
to send messages from (this is a requirement in the USA to send messages).

Enable 2-way messaging on that long-code and choose the SNS PinpointIncomingTextAlerts
topic that was deployed along with Retail Demo Store to send messages to, so that responses
to verification SMS messages can be processed to opt in users.

Enter your phone number from the UI to start the verification process and reply to the text
message sent to your phone to opt in.

  


  



import {mapState} from 'vuex';

import ArticleLayout from '../ArticleLayout.vue';
import ArticleFeature from '../ArticleFeature/ArticleFeature.vue';

export default {
  name: 'LocationServices',
  components: {ArticleLayout, ArticleFeature},
  computed: {...mapState({isMobile: (state) => state.modal.isMobile})},
};



.digital-interactions {
  margin-bottom: 9rem;
}

.logo-and-quote--mobile {
  margin-bottom: 20px;
  flex-direction: column;
}

.logo-and-quote--mobile .dominos {
  width: auto;
  max-width: 300px;
}

.cloudformation-text {
  font-family: "Droid Sans Mono", "Courier New", monospace;
}

.subheading {
  font-size: 70%;
  font-weight: bold;
}

.feature-subheading {
  font-size: 100%;
}


