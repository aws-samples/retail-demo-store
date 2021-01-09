<template>
  <ArticleLayout>
    <template #heading>Real time personalization based on real time user activity</template>

    <p>
      Amazon Personalize can capture live events from your users to achieve real-time personalization. Amazon
      Personalize can blend real-time user activity data with existing user profile and item information to recommend
      the most relevant items, according to the user’s current session and activity.
    </p>

    <p>
      Do you have the infrastructure in place for real-time click streaming events back into Personalize? If not, don’t
      worry, we can help!
    </p>

    <div class="d-flex flex-wrap justify-content-center text-center">
      <div class="service mx-2">
        <h3 class="service-heading">BUILD</h3>
        <p>Learn more about the AWS services available to build real-time streaming capabilities</p>
      </div>
      <div class="service mx-2">
        <h3 class="service-heading">BUY</h3>
        <p>
          AWS is partnering with multiple partners to translate and send your data to Amazon Personalize in the right
          format.
        </p>
      </div>
    </div>

    <div class="mb-4">
      <img src="/personalization-architecture.png" alt="personalization architecture" class="img-fluid" />
    </div>

    <section class="provisioning-container">
      <h2 class="provisioning-heading">Provisioning capacity for real-time recommendations</h2>

      <p>
        Customers are charged based on the transaction-per-second (TPS) capacity provisioned or used, whichever is
        greater. When creating an Amazon Personalize campaign, a customer sets their minimum TPS capacity. TPS capacity
        is measured on a TPS-hour basis (rounded up to the nearest hour). If the customer’s transaction load exceeds the
        minimum provisioned capacity, Amazon Personalize will auto-scale based on the customer’s needs. In most cases
        when a customer starts with Amazon Personalize, we recommend provisioning the minimum (1 TPS), then
        experimenting to see the impact of Personalize for users. These learnings will help inform how to scale based on
        their needs to avoid unexpected charges due to over-provisioning.
      </p>
    </section>

    <ArticleFeature class="mb-4">
      <template #default>
        <div :class="{'logo-and-quote--mobile': isMobile}">
          <div class="keen"><img src="/keen.png" alt="" class="img-fluid" /></div>
          <p>
            KEEN is a values led, independently owned outdoor footwear brand with a mission to responsibly create
            original and versatile products, improve lives, and inspire outside adventure. Founded in 2003, KEEN ignited
            a revolution in the footwear industry with the introduction of the Newport sandal, launching the concept of
            Hybrid footwear into the market and setting KEEN on a path of driving consistent product innovation that
            exists today.
          </p>
        </div>

        <Quote>
          <template #quote>
            "Over the past two years KEEN has been working to improve the way we engage our customers to bring them
            increasingly relevant content for their outdoor footwear needs. Our goal is to educate our customers on the
            best footwear options based on their desired outdoor activities. To really bring this capability to life we
            turned to AWS and our partnership with Data in the Raw and develop a solution powered by Amazon Personalize
            to use purchase and browsing history to best tailor recommendations and content for our customers along
            their purchasing journey. With the initial use we looked to improve the experience for our browse abandon
            customers through our email program. Initial results are encouraging, our open rates, Rev/M Sends, and Opt
            out Rates were very healthy to begin with but with the implementation of Amazon Personalize we are seeing,
            email CTR is up 67% over our control messaging. Rev/M Sends is up 49%, and because the content is even more
            relevant, our Opt out Rate has dropped 36%. But where the rubber hits the road for me is on revenue. Test
            emails have shown a 12.5% increase in revenue versus the control. It is clear that the AWS has given us
            another ‘arrow in our quiver’. My only regret is this capability didn’t exist two years ago when we started
            this journey."
          </template>

          <template #attribution>
            <div>Kristina Smith, Director Global Digital Marketing</div>
            <div>KEEN Inc.</div>
          </template>
        </Quote>
      </template>
    </ArticleFeature>

    <ArticleFeature class="mt-4">
      <template #default>
        <div>
          <div class="data-in-the-raw mb-3"><img src="/data-in-the-raw.png" alt="" class="img-fluid" /></div>
          <p>
            Data in the Raw helps online retailers and content producers build scalable analytics and machine learning
            infrastructures. With just one JavaScript tag, Data in the Raw can start automatically capturing users’
            unfiltered web data, from which they create a custom behavioral CRM on AWS. That CRM can be used with
            business intelligence software and can help enable personalization, conversion rate optimization, user
            experience/user interaction analysis, attribution modeling, and more. The company describes their offering
            as a self-service big data pipeline to AWS.
          </p>
        </div>

        <Quote>
          <template #quote>
            “In this time of one-size-fits-all personalization and expensive customer data platforms, Data in the Raw is
            different. Unlike other platforms that sell users back their own data, our affordable pricing already
            includes ownership of raw clickstream data. With the recent release of Amazon Personalize, our clients are
            now shifting away from boring and bloated personalization platforms to build experiences that reach their
            customers more efficiently. Not only do our clients save thousands of dollars using Data in the Raw and
            Amazon Personalize, they have ultimate control over their own data and freedom to build what works for them.
            With our core values of data democratization, Data in the Raw and Amazon Personalize are the perfect match.”
          </template>

          <template #attribution>
            <div>Andrew Duffle, Co-Founder</div>
            <div>Data in the Raw</div>
          </template>
        </Quote>
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
  name: 'RealTimePersonalization',
  components: { ArticleLayout, ArticleFeature, Quote },
  computed: { ...mapState({ isMobile: (state) => state.modal.isMobile }) },
};
</script>

<style scoped>
.provisioning-container {
  margin-bottom: 9rem;
}

.provisioning-heading {
  font-size: 1.5rem;
}

.service {
  width: 400px;
}

.service-heading {
  font-size: 1rem;
}

.logo-and-quote--mobile .keen {
  float: none;
  margin: auto;
  width: auto;
  max-width: 300px;
}

.keen {
  float: left;
  margin-right: 20px;
  width: 220px;
}

.data-in-the-raw {
  width: 50%;
  margin: auto;
}
</style>
