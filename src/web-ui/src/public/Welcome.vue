<template>
  <Layout :showNav="false" :showFooter="false" :backgroundColor="'var(--aws-squid-ink)'">
    <div class="container mb-2 text-left">
      <header class="px-3 px-md-5">
        <h1 class="heading my-5 text-center">Welcome to the Retail Demo Store!</h1>

        <p>
          The Retail Demo Store is a demo platform to demonstrate how AWS infrastructure and services can be used to
          build personalized customer experiences across multiple channels of engagement.
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

        <!-- make both links to go /auth until we have dedicated sign in and create account pages -->
        <div class="auth-cta my-5 d-flex flex-column flex-sm-row justify-content-end align-items-center">
          <div class="login-cta d-flex align-items-center">
            *Have an account?<router-link to="/auth" class="sign-in btn btn-link">Sign in</router-link>
          </div>
          <router-link to="/auth" class="create-account btn btn-primary">Create an account</router-link>
        </div>
      </header>

      <section class="info py-3 px-3 py-md-4 px-md-5">
        <p>
          *To keep the click-through data fresh, this demo resets every day at 11 pm EST. Accounts created more than 24
          hours prior would be deleted as well. If your account has been deleted, go ahead and create a new one.
        </p>
        <p class="mb-0">
          This project also comes with a collection of workshops that are designed to walk a technical audience, either
          in a group setting or self-paced as an individual, through adding enhanced functionality to the Retail Demo
          Store. There are workshops for adding search, personalization, experimentation framework, user messaging, and
          more. For an overview of the Retail Demo Store, its architecture, and workshops, please see the
          <a
            href="https://github.com/aws-samples/retail-demo-store/tree/master/workshop"
            target="_blank"
            rel="noopener noreferrer"
            class="workshop-link"
            >workshop welcome notebook page</a
          >.
        </p>
      </section>
    </div>
  </Layout>
</template>

<script>
import Layout from './components/Layout';
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

.auth-cta,
.login-cta {
  gap: 20px;
}

.sign-in {
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

.info {
  border-radius: 8px;
  background: var(--aws-deep-squid-ink);
}

.workshop-link {
  color: var(--blue-500);
}
</style>
