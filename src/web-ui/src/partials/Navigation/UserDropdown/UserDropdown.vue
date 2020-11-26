<template>
  <div>
    <router-link v-if="!user" to="/auth" class="user-dropdown-button btn btn-outline-dark">Sign In</router-link>

    <button
      v-if="user"
      id="navbarDropdown"
      class="user-dropdown-button btn btn-outline-dark dropdown-toggle"
      data-toggle="dropdown"
      aria-haspopup="true"
      aria-expanded="false"
    >
      {{ username }}
    </button>
    <div v-if="user" class="dropdown-menu" aria-labelledby="navbarDropdown">
      <span class="dropdown-item-text small" v-if="user.first_name && user.last_name"
        >{{ user.first_name }} {{ user.last_name }} ({{ user.username }})</span
      >
      <span class="dropdown-item-text small text-muted" v-if="user.persona">{{ user.persona }}</span>
      <div class="dropdown-divider" v-if="user.persona"></div>
      <router-link class="dropdown-item" to="/orders">Orders</router-link>
      <router-link class="dropdown-item" to="/profile">Profile</router-link>
      <div class="dropdown-divider"></div>
      <button class="dropdown-item" @click="signOut">Sign Out</button>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { AmplifyEventBus } from 'aws-amplify-vue';
import { Auth } from 'aws-amplify';
import swal from 'sweetalert';

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
    }),
  },
  methods: {
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
  border-color: var(--grey-600);
}

.user-dropdown-button:hover,
.user-dropdown-button:focus {
  background: var(--grey-600);
}
</style>
