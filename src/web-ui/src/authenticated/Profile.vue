<template>
  <div class="content">

      <!-- Loading Indicator -->
    <div class="container mb-4" v-if="!user">
      <i class="fas fa-spinner fa-spin fa-3x"></i>
    </div>

    <div class="container" v-if="user">
      <h4>{{ user.username }}</h4>
      <h5>{{ user.persona }}</h5>
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
                  <option v-for="u in users" v-bind:key="u.id" v-bind:value="u.id" :selected="user.id === u.id">{{ u.first_name }} {{ u.last_name }} - {{ u.persona }}</option>
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

      <h4>Admin</h4>
      <hr/>
      <button type="button" class="btn btn-primary" data-toggle="modal" data-target="#exampleModal">
        Reset Personalize Campaigns
      </button>
      <div class="modal fade" id="exampleModal" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
        <div class="modal-dialog" role="document">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="exampleModalLabel">Confirm</h5>
              <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div class="modal-body text-left">
              Resetting Personalize campaigns will remove all Personalize resources & interactions and retrain campaigns from scratch.
              <br><br>
              This process takes approximately 3 hours and no campaigns will be available during this time.
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
              <button type="button" class="btn btn-warning" v-on:click="resetRealtime" data-dismiss="modal">Reset Personalize Campaigns</button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { RepositoryFactory } from '@/repositories/RepositoryFactory'
import { AnalyticsHandler } from '@/analytics/AnalyticsHandler'
import { AmplifyEventBus } from 'aws-amplify-vue';

import AmplifyStore from '@/store/store'

import swal from 'sweetalert'

const UsersRepository = RepositoryFactory.get('users')
const RecommendationsRepository = RepositoryFactory.get('recommendations');

export default {
  name: 'Profile',
  components: {
  },
  props: {
  },
  data () {
    return {  
      errors: [],
      user: null,
      saving: false,
      users: [],
      newUserId: AmplifyStore.state.user.id
    }
  },
  created () {
    this.getUser(AmplifyStore.state.user.id)
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
    async getUsers() {
      // More users than we can display in dropdown so limit to 300.
      const start = Math.max(0, parseInt(AmplifyStore.state.user.id) - 100)
      const { data } = await UsersRepository.get(start, start + 300)
      this.users = data
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
    },
    resetRealtime() {

      RecommendationsRepository.resetRealtimeRecommendations().then(function(res) {
        let title = "";
        if (res.status === 200) {
          title = "Product recommendations set for retrain. This takes approximately 3 hours and in the meantime the recommender is not available."
        } else {
          title = "Product recommendations retrain may not have worked this time " +
              "(status=" + res.status + "): More info: " + res.data
        }
        swal({
          title: title,
          icon: "success",
          buttons: {
            cancel: "OK",
          }
        }).then((value) => {
          switch (value) {
            case "cancel":
              break;
          }
        });
      });
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