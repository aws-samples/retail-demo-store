<template>
  <div :class="{ mobile: isMobile }">
    <h1 class="heading mb-5 text-center">Select A Shopper</h1>
    <div class="button-container d-flex justify-content-center">
      <button
        type="button"
        class="use-default-profile btn btn-lg"
        @click="useDefaultProfile"
        data-toggle="tooltip"
        data-placement="bottom"
        title="Switch back to the profile associated with your login credentials"
        ref="useDefaultProfile"
      >
        Use default profile
      </button>
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
    $([this.$refs.autoSelectShopper, this.$refs.chooseAShopper, this.$refs.useDefaultProfile]).tooltip();
  },
  beforeDestroy() {
    // eslint-disable-next-line no-undef
    $([this.$refs.autoSelectShopper, this.$refs.chooseAShopper, this.$refs.useDefaultProfile]).tooltip('dispose');
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
.heading {
  margin-top: 20%;
  font-size: 1.75rem;
}

.mobile .button-container {
  flex-direction: column;
  align-items: center;
}

.auto-select,
.choose-shopper,
.use-default-profile {
  width: 300px;
}

.mobile .auto-select,
.mobile .choose-shopper,
.mobile .use-default-profile {
  width: 100%;
  max-width: 350px;
}

.auto-select,
.use-default-profile {
  margin-right: 16px;
  color: var(--blue-500);
}

.auto-select {
  border-color: var(--blue-500);
}

.mobile .auto-select,
.mobile .use-default-profile {
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
.choose-shopper:focus,
.use-default-profile:hover,
.use-default-profile:focus {
  background-color: var(--blue-600);
  border-color: var(--blue-600);
  color: var(--white);
}
</style>
