<template>
  <ArticleLayout>
    <template #heading>Real-Time User Segmentation</template>

    <p>
      Amazon Pinpoint enables organizations to create user segments - or groups of customers - based on their behavior
      across web/mobile applications, interactions over email, text, push notifications, and other channels, or based on
      stored data. This is important in retail environments because customers deliver valuable intent data across
      in-store, e-commerce, and customer engagement channels. Pinpoint enables organizations to create a single event
      bus of all these interactions to inform segmentation, personalized messaging, and analytics.
    </p>

    <p class="real-time-segments">
      These segments can often be created and responded to in real-time. Here, your clickstreams in the Retail Demo
      Store application are ingested by Amazon Pinpoint to create new user segments in real-time. These segments are
      then used to deliver the targeted messages that receive throughout the demo.
    </p>

    <ArticleFeature>
      <template #title>AWS Messaging And Targeting Blog</template>

      <template #default>
        <div :class="{ 'd-flex': true, 'logo-and-quote--mobile': isMobile }">
          <div class="disney mr-3"><img src="/disney.png" alt="" class="img-fluid" /></div>
          <Quote class="disney-quote mb-2">
            <template #quote>
              “We want to send messages through dynamic segmentation. When we send a push notification, we need to
              dynamically segment immediately. When we call Amazon Pinpoint to say “Create this segment right now, for
              this game event that’s happening right now, and then create this campaign right now, and then send it, and
              Pinpoint does all of that in milliseconds.”
            </template>

            <template #attribution>
              <div>Billy Liu, Senior Director</div>
              <div>Disney Streaming Services</div>
            </template>
          </Quote>
        </div>

        <p class="mb-0">
          Read full AWS Messaging &amp; Targeting Blog post:
          <a
            href="https://aws.amazon.com/blogs/messaging-and-targeting/how-disney-streaming-services-uses-amazon-pinpoint-to-send-personalized-messages-to-millions-of-users-in-real-time/"
            target="_blank"
            rel="noreferrer noopener"
            >How Disney Streaming Services Uses Amazon Pinpoint to Send Personalized Messages to Millions of Users in
            Real Time</a
          >
        </p>
      </template>
    </ArticleFeature>
  </ArticleLayout>
</template>

<script>
import { mapState } from 'vuex';

import ArticleLayout from '../ArticleLayout';
import ArticleFeature from '../ArticleFeature/ArticleFeature';
import Quote from '../Quote/Quote';

export default {
  name: 'UserSegmentation',
  components: { ArticleLayout, ArticleFeature, Quote },
  computed: { ...mapState({ isMobile: (state) => state.modal.isMobile }) },
};
</script>

<style scoped>
.real-time-segments {
  margin-bottom: 9rem;
}

.logo-and-quote--mobile {
  flex-direction: column;
  align-items: center;
}

.logo-and-quote--mobile .disney {
  width: auto;
  max-width: 300px;
}

.disney {
  width: 220px;
}

.disney-quote {
  flex: 1;
}
</style>
