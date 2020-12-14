<template>
  <Layout :showNav="false" :showFooter="false" :showTextAlerts="false" :showDemoGuide="false" backgroundColor="var(--aws-squid-ink)">
    <div class="container mb-2 text-left">
      <h1 class="heading my-5 text-center">Welcome to the Retail Demo Store!</h1>

      <p>
        The Retail Demo Store is a demo platform to demonstrate how AWS infrastructure and services can be used to build
        personalized customer experiences across multiple channels of engagement.
      </p>

      <p>
        The Retail Demo Store mimics an online store with products, users and user-interactions to showcase the
        personalized product recommendations a shopper would receive based on historical and real time click-through
        behavior.
      </p>

      <div class="mt-2 d-flex flex-column flex-lg-row align-items-lg-center">
        <div class="mb-2 mb-lg-0">AWS Services Included:</div>

        <ul
          class="service-list mb-0 pl-0 flex-grow-1 d-flex flex-column flex-lg-row justify-content-lg-around font-weight-bold"
        >
          <li v-for="service in services" :key="service.text" class="mb-2 mb-lg-0">
            <ServiceBadge :text="service.text" :src="service.src"></ServiceBadge>
          </li>
        </ul>
      </div>

      <div class="mt-2 mb-4 my-sm-5 d-flex flex-column align-items-center align-items-sm-end">
        <div class="d-flex flex-column flex-sm-row align-items-center">
          <div class="login-cta d-flex justify-content-center align-items-center">
            Have an account?<router-link to="/auth" class="sign-in btn btn-link">Sign in</router-link>
          </div>
          <router-link to="/auth?signup=true" class="create-account mt-3 mt-sm-0 ml-sm-3 btn btn-primary"
            >Create an account</router-link
          >
        </div>

        <router-link to="/" class="mt-3 skip-login btn btn-link">Skip login for now</router-link>
      </div>
    </div>
  </Layout>
</template>

<script>
import Layout from '@/components/Layout/Layout'
import ServiceBadge from './components/ServiceBadge';

export default {
  name: 'Welcome',
  components: {
    Layout,
    ServiceBadge,
  },
  data() {
    return {
      services: [
        {
          text: 'Amazon Personalize',
          src: '/personalize.svg',
        },
        {
          text: 'Amazon Pinpoint',
          src: '/pinpoint.svg',
        },
        {
          text: 'Amazon Lex',
          src: '/lex.svg',
        },
      ],
    };
  },
};
</script>

<style scoped>
.container {
  margin-top: 10vh;
  color: var(--white);
}

.service-list {
  list-style-type: none;
}

.sign-in,
.skip-login {
  color: var(--amazon-orange);
}

.create-account {
  border-color: var(--amazon-orange);
  border-radius: 4px;
  background: var(--amazon-orange);
}

.create-account:hover,
.create-account:focus {
  background: var(--amazon-orange-light);
  border-color: var(--amazon-orange-light);
}
</style>
