<script setup>
  import { Authenticator } from "@aws-amplify/ui-vue";
  import "@aws-amplify/ui-vue/styles.css";
</script>

<template>
  <SecondaryLayout>
    <authenticator :sign-up-attributes="['username', 'password','email']" >
      <template v-slot:sign-up-header>
        <div style="padding: var(--amplify-space-large); text-align: left">
          We require you to enter an email address to send a code to verify your account.<br/>
          Passwords must contain at least 8 characters, including an uppercase letter, a lowercase letter, a special character, and a number.
        </div>
      </template>
    </authenticator>    
  </SecondaryLayout>
</template>

<script>
import SecondaryLayout from '@/components/SecondaryLayout/SecondaryLayout.vue';

export default {
  name: 'Auth',
  components: {
    SecondaryLayout
  },
  data() {
    return {
      showingSignUp: undefined,
      authConfig: {
        signInConfig: {
          header: 'Sign In'
        },
        signUpConfig: {
          hideAllDefaults: true,
          header: 'Create account',
          signUpFields: [
            {
              label: 'Email',
              key: 'email',
              type: 'email',
              required: true
            },
            {
              label: 'Password',
              key: 'password',
              type: 'password',
              required: true
            },
            {
              label: 'Username',
              key: 'username',
              type: 'string',
              required: true
            },
          ]
        }
      }
    }
  }
}
</script>

<style>
/* Amplify Auth Form Styling */

div[data-test="sign-in-section"],
div[data-test="sign-up-section"],
div[data-test="verify-contact-section"],
div[data-test="require-new-password-section"],
div[data-test="federated-sign-in-section"],
div[data-test="confirm-sign-up-section"],
div[data-test="confirm-sign-in-section"],
div[data-test="set-mfa-section"],
div[data-test="forgot-password-section"] {
  box-shadow: none;
}

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

/* Set font-size to 18px to disable auto-zoom on mobile Safari */
div[data-test="sign-in-section"] input,
div[data-test="sign-up-section"] input,
div[data-test="verify-contact-section"] input,
div[data-test="require-new-password-section"] input,
div[data-test="federated-sign-in-section"] input,
div[data-test="confirm-sign-up-section"] input,
div[data-test="confirm-sign-in-section"] input,
div[data-test="set-mfa-section"] input,
div[data-test="forgot-password-section"] input {
  font-size: 18px !important;
  padding: .5em;
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
  color: var(--blue-500) !important;
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
