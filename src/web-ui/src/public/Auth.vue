<script setup>
  import { Authenticator } from "@aws-amplify/ui-vue";
  import SecondaryLayout from '@/components/SecondaryLayout/SecondaryLayout.vue';
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

<style>
.amplify-input {
  text-align: left;
}
.amplify-field {
  text-align: left;
}

</style>

