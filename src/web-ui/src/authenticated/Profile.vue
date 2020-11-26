<template>
  <Layout>
    <div class="content">

        <!-- Loading Indicator -->
      <div class="container mb-4" v-if="!user">
        <i class="fas fa-spinner fa-spin fa-3x"></i>
      </div>

    <div class="container" v-if="user">
      <h4>{{ user.username }}</h4>
      <h5 v-if="user.persona">{{ user.persona }}</h5>
      <hr/>

      <div class="row text-left">
        <div class="col-md-12 order-md-1">
          <h5 class="mb-3">Select User to Emulate</h5>
          <form class="needs-validation" novalidate>
            <div class="row">
              <div class="col-md-12 mb-3">
                <label for="newUserId">User</label>
                <select class="custom-select" v-model="newUserId" id="newUserId">
                  <option value="">Select User</option>
                  <optgroup label="Your Profile" v-if="authdUser">
                    <option v-bind:key="authdUser.id" v-bind:value="authdUser.id" :selected="user.id === authdUser.id">
                      <span v-if="authdUser.first_name">{{ authdUser.first_name }} {{ authdUser.last_name }}</span><span v-else>{{authdUser.username}}</span>
                    </option>
                  </optgroup>
                  <optgroup label="Sample Shoppers">
                    <option v-for="u in users" v-bind:key="u.id" v-bind:value="u.id" :selected="user.id === u.id">
                      <span v-if="u.first_name">{{ u.first_name }} {{ u.last_name }}</span><span v-else>{{u.username}}</span> ({{ u.persona }})
                    </option>
                  </optgroup>
                </select>
              </div>
            </div>
          </form>
        </div>
      </div>

        <div class="row text-left">

          <div class="col-md-12 order-md-1">
            <h5 class="mb-3">Your Information</h5>
            <form class="needs-validation" novalidate>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="firstName">First name</label>
                  <input type="text" class="form-control" id="firstName" placeholder="" value="" required v-model="user.first_name">
                  <div class="invalid-feedback">
                    Valid first name is required.
                  </div>
                </div>
                <div class="col-md-6 mb-3">
                  <label for="lastName">Last name</label>
                  <input type="text" class="form-control" id="lastName" placeholder="" value="" required v-model="user.last_name">
                  <div class="invalid-feedback">
                    Valid last name is required.
                  </div>
                </div>
              </div>

              <div class="mb-3">
                <label for="email">Email <span class="text-muted">(Optional)</span></label>
                <input type="email" class="form-control" id="email" placeholder="you@example.com" v-model="user.email">
                <div class="invalid-feedback">
                  Please enter a valid email address for shipping updates.
                </div>
              </div>

            </form>
            <button class="btn btn-primary" v-on:click="saveChanges"> <i class="fas fa-spinner fa-spin" v-if="saving"></i> Save Changes </button>
          </div>

        </div>
      </div>

    </div>
  </Layout>
</template>

<script>
import { RepositoryFactory } from '@/repositories/RepositoryFactory'
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler'
import { AmplifyEventBus } from 'aws-amplify-vue';
import { Credentials } from '@aws-amplify/core';

import AmplifyStore from '@/store/store'

import swal from 'sweetalert'

import Layout from '@/components/Layout/Layout'

const UsersRepository = RepositoryFactory.get('users')

export default {
  name: 'Profile',
  components: {
    Layout,
  },
  data () {
    return {  
      errors: [],
      user: null,
      authdUser: null,
      identityId: null,
      saving: false,
      users: [],
      newUserId: AmplifyStore.state.user.id
    }
  },
  created () {
    this.getUser(AmplifyStore.state.user.id)
    this.getAuthdUser()
    this.getUsers()
  },
  methods: {
    async getUser(userID) {
      if (userID && userID.length > 0) {
        const { data } = await UsersRepository.getUserByID(userID)
        this.user = data
      }
      return this.user
    },
    async getAuthdUser() {
      const credentials = await Credentials.get();
      if (credentials && credentials.identityId) {
        this.identityId = credentials.identityId;
        const { data } = await UsersRepository.getUserByIdentityId(credentials.identityId);
        this.authdUser = data
      }
    },
    async getUsers() {
      // More users than we can display in dropdown so limit to 300.
      const { data } = await UsersRepository.get(0, 300);
      this.users = this.users.concat(data);
    },     
    async saveChanges () {
      this.saving = true;

      try {
        const { data } = await UsersRepository.updateUser(this.user)
        this.user = data

        AmplifyStore.commit('setUser', this.user);

        AnalyticsHandler.identify(this.user)

        AmplifyEventBus.$emit('authState', 'profileChanged')

        swal({
          title: "Information Updated",
          icon: "success",
          buttons: {
            cancel: "OK"
          }
        })
      }
      finally {
        this.saving = false;
      }
    }
  },
  watch: { 
    newUserId: function(newVal) {
      this.getUser(newVal)
    }
  }
}
</script>

<style scoped>
</style>