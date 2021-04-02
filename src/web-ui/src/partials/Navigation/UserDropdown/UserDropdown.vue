<template>
  <div>
    <router-link v-if="!user" to="/auth" class="user-dropdown-button login-button btn">Sign In</router-link>

    <button
      v-if="user"
      id="navbarDropdown"
      :class="{ 'user-dropdown-button btn text-left text-lg-right': true, username: !user.persona }"
      data-toggle="dropdown"
      aria-haspopup="true"
      aria-expanded="false"
    >
      <template v-if="user.persona">
        <div class="shopper">Shopper:</div>

        <div>
          <div>{{ username }} - {{ user.age }} years - {{ gender }}</div>
          <div>{{ formattedPreferences }}</div>
        </div>
      </template>

      <template v-else>{{ username }}</template>
    </button>

    <div v-if="user" class="dropdown-menu px-3" aria-labelledby="navbarDropdown">
      <a href="#" @click="switchShopper" class="dropdown-item">
        <div class="dropdown-item-title">
          Switch shoppers
        </div>
        <div>Select another shopper with different shopping preferences</div>
      </a>

      <div class="dropdown-divider"></div>

      <router-link to="/orders" class="dropdown-item">
        <div class="dropdown-item-title">Orders</div>
        <div>View orders placed by the current shopper profile</div>
      </router-link>

      <div class="dropdown-divider"></div>

      <button class="dropdown-item dropdown-item-title" @click="signOut">Sign Out</button>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { AmplifyEventBus } from 'aws-amplify-vue';
import { Auth } from 'aws-amplify';
import swal from 'sweetalert';

import { Modals } from '@/partials/AppModal/config';

export default {
  name: 'UserDropdown',
  computed: {
    ...mapState({
      user: (state) => state.user,
      username() {
        // first_name can be an empty string - should be validated against in the future
        if (!this.user) return null;
        if (!this.user.first_name) return this.user.username;
        return this.user.first_name;
      },
      gender() {
        if (!this.user || !this.user.gender) return null;

        switch (this.user.gender) {
          case 'M':
            return 'Male';
          case 'F':
            return 'Female';
        }

        throw new Error('Gender not accounted for');
      },
      formattedPreferences() {
        if (!this.user || !this.user.persona) return null;

        return this.user.persona
          .split('_')
          .map((pref) =>
            pref
              .split(' ')
              .map((word) => [word[0].toUpperCase(), ...word.slice(1)].join(''))
              .join(' '),
          )
          .join(', ');
      },
    }),
  },
  methods: {
    ...mapActions(['openModal']),
    switchShopper() {
      this.openModal(Modals.ShopperSelect);
    },
    signOut() {
      Auth.signOut({ global: true })
        .then(() => {
          AmplifyEventBus.$emit('authState', 'signedOut');
          swal('You have been logged out!');
        })
        .catch(swal);
    },
  },
};
</script>

<style scoped>
.user-dropdown-button {
  border: none;
  background: none;
  font-size: 0.85rem;
  line-height: 1.15rem;
}

.login-button {
  border-color: var(--grey-600);
  font-size: 1rem;
}

.shopper {
  font-weight: bold;
  color: var(--blue-600);
}

.username {
  font-size: 1rem;
}

.dropdown-menu {
  max-width: 350px;
}

.dropdown-item {
  white-space: normal;
}

.dropdown-item-title {
  color: var(--blue-600);
}

.dropdown-item:active .dropdown-item-title,
.dropdown-item-title:active {
  color: var(--white);
}
</style>
