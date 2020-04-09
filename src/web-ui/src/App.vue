<template>
  <div id="app">
    <Navigation/>
    <router-view class="text-center"/>
    <Footer/>
  </div>
</template>

<script>
import Navigation from './public/Navigation.vue'
import Footer from './public/Footer.vue'

export default {
  name: 'app',
  components: {
    Navigation,
    Footer
  },
  data () {
    return {
      errors: []
    }
  },
  mounted () {
  },
  methods: {
  }
}
</script>

<style>
body {
  background: #FFF;
}

/* Amplify Auth Form Styling */

/* On xs screens, override default min-width on forms to prevent overflow */
@media (max-width: 576px) {
  div[data-test="sign-in-section"],
  div[data-test="sign-up-section"],
  div[data-test="verify-contact-section"],
  div[data-test="require-new-password-section"],
  div[data-test="federated-sign-in-section"],
  div[data-test="confirm-sign-up-section"],
  div[data-test="confirm-sign-in-section"],
  div[data-test="set-mfa-section"],
  div[data-test="forgot-password-section"] {
    min-width: initial !important;
  }
}

/* Set font-size to 16px to disable auto-zoom on mobile Safari */
div[data-test="sign-in-section"] input,
div[data-test="sign-up-section"] input,
div[data-test="verify-contact-section"] input,
div[data-test="require-new-password-section"] input,
div[data-test="federated-sign-in-section"] input,
div[data-test="confirm-sign-up-section"] input,
div[data-test="confirm-sign-in-section"] input,
div[data-test="set-mfa-section"] input,
div[data-test="forgot-password-section"] input {
  font-size: 16px !important;
}

/* Make links in form text/labels more noticeable */
div[data-test="sign-in-section"] a,
div[data-test="sign-up-section"] a,
div[data-test="verify-contact-section"] a,
div[data-test="require-new-password-section"] a,
div[data-test="federated-sign-in-section"] a,
div[data-test="confirm-sign-up-section"] a,
div[data-test="confirm-sign-in-section"] a,
div[data-test="set-mfa-section"] a,
div[data-test="forgot-password-section"] a {
  color: #007bff !important;
}

/* Make error messages stand out and match bootstrap alert-error */
div[data-test="sign-in-section"] div.error,
div[data-test="sign-up-section"] div.error,
div[data-test="verify-contact-section"] div.error,
div[data-test="require-new-password-section"] div.error,
div[data-test="federated-sign-in-section"] div.error,
div[data-test="confirm-sign-up-section"] div.error,
div[data-test="confirm-sign-in-section"] div.error,
div[data-test="set-mfa-section"] div.error,
div[data-test="forgot-password-section"] div.error {
  color: #721c24;
  background-color: #f8d7da;
  position: relative;
  padding: .75rem 1.25rem;
  margin-top: 1rem;
  border: 1px solid #f5c6cb;
  border-radius: .25rem;
}
</style>