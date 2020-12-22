<template>
  <div :class="{ 'get-started-container': true, mobile: isMobile }">
    <h1 class="heading mb-4 text-center">Select A Shopper</h1>

    <div class="explanation mb-5">
      <p>
        The dataset used to power the Retail Demo Store has thousands of shoppers, each one with different age, gender,
        shopping interests, and browsing history. This demo allows you to select shoppers from this dataset.
      </p>

      <p>Select a fictitious shopper by using one of the options below.</p>
    </div>

    <div class="button-container mb-5 d-flex justify-content-center">
      <button
        type="button"
        class="auto-select btn btn-lg btn-outline-primary"
        @click="autoSelectShopper"
        data-toggle="tooltip"
        data-placement="bottom"
        title="Randomly select a shopper from the current Retail Demo Store users dataset"
        ref="autoSelectShopper"
      >
        Auto select shopper
      </button>
      <button
        type="button"
        class="choose-shopper btn btn-lg btn-primary"
        @click="chooseAShopper"
        data-toggle="tooltip"
        data-placement="bottom"
        title="Select a shopper from the current Retail Demo Store users dataset based on demographics and shopping preferences"
        ref="chooseAShopper"
      >
        Choose a shopper
      </button>
    </div>

    <hr class="mb-5" />

    <div>
      <p>
        Alternatively, you can use your
        <a href="#" @click="useDefaultProfile" class="default-profile">default profile</a> to go through the cold user
        path to see how recommendations are personalized throughout based on browsing behavior.
      </p>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler';
import { AmplifyEventBus } from 'aws-amplify-vue';

import { RepositoryFactory } from '@/repositories/RepositoryFactory';

const UsersRepository = RepositoryFactory.get('users');

export default {
  name: 'GetStarted',
  computed: {
    ...mapState({ isMobile: (state) => state.modal.isMobile }),
  },
  mounted() {
    // eslint-disable-next-line no-undef
    $([this.$refs.autoSelectShopper, this.$refs.chooseAShopper]).tooltip();
  },
  beforeDestroy() {
    // eslint-disable-next-line no-undef
    $([this.$refs.autoSelectShopper, this.$refs.chooseAShopper]).tooltip('dispose');
  },
  methods: {
    ...mapActions(['setUser']),
    chooseAShopper() {
      this.$emit('chooseAShopper');
    },
    async autoSelectShopper() {
      const { data } = await UsersRepository.getRandomUser();

      this.$emit('autoSelectShopper', {
        assignedShopper: data[0],
      });
    },
    async useDefaultProfile() {
      const cognitoUser = await this.$Amplify.Auth.currentAuthenticatedUser();

      const { data: user } = await UsersRepository.getUserByUsername(cognitoUser.username);

      this.setUser(user);

      AnalyticsHandler.identify(user);

      AmplifyEventBus.$emit('authState', 'profileChanged');

      this.$emit('useDefaultProfile');
    },
  },
};
</script>

<style scoped>
.get-started-container {
  max-width: 800px;
  margin: auto;
}

.heading {
  margin-top: 15%;
  font-size: 1.75rem;
}

.explanation {
  font-size: 1.15rem;
}

.mobile .button-container {
  flex-direction: column;
  align-items: center;
}

.auto-select,
.choose-shopper {
  flex: 1;
}

.mobile .auto-select,
.mobile .choose-shopper {
  width: 100%;
  max-width: 350px;
}

.auto-select {
  margin-right: 16px;
  color: var(--blue-500);
}

.auto-select {
  border-color: var(--blue-500);
}

.mobile .auto-select {
  margin-right: 0px;
  margin-bottom: 16px;
}

.choose-shopper {
  background-color: var(--blue-500);
  border-color: var(--blue-500);
}

.auto-select:hover,
.auto-select:focus,
.choose-shopper:hover,
.choose-shopper:focus {
  background-color: var(--blue-600);
  border-color: var(--blue-600);
  color: var(--white);
}

.default-profile {
  color: var(--blue-600);
}
</style>
