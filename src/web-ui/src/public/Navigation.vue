<template>
  <div class="navigation">

    <!-- Top Bar-->
    <div class="container">
      <nav class="navbar fixed-top navbar-secondary bg-light">
        <ul class="navbar-nav mr-auto">
          <li class="nav-item text-dark">
            <i class="fab fa-twitter"></i>
            <i class="fab fa-facebook ml-2"></i>
            <i class="fab fa-instagram ml-2"></i>
          </li>
        </ul>
        <ul class="navbar-nav mx-auto d-none d-md-block">
          <li class="nav-item text-dark">
            Free Shipping on All Orders over $100
          </li>                  
        </ul>   
        <ul class="navbar-nav ml-auto">
          <li class="nav-item">
            <router-link class="text-dark pull-right mr-3" :to="{name:'Cart'}"><i class="fas fa-shopping-cart"></i></router-link> 
            <router-link class="text-dark" :to="{name:'Help'}"><i class="fas fa-question-circle"></i></router-link> 
          </li>  
        </ul>                                    
      </nav>  
    </div>

    <!-- Navigation Bar-->
    <div class="container">
      <nav class="navbar navbar-expand-md fixed-top navbar-dark bg-white nav-bar-bottom">
        <router-link class="navbar-brand text-primary mr-0" :to="{name:'Main'}">
          <span class="fa-stack">
            <i class="fa fa-square fa-stack-2x"></i>
            <i class="fa fa-globe-americas fa-stack-1x fa-inverse"></i>
          </span>
          &nbsp;Retail Demo Store  
        </router-link>
        <ul class="navbar-nav ml-auto">
          <li class="nav-item" v-if="!user" >
            <a class="btn btn-outline-dark" href="#" v-on:click="signIn">Sign In</a>
          </li>
          <li class="nav-item dropdown" v-if="user">
            <a class="nav-link dropdown-toggle text-dark" href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              <span v-if="user.first_name">{{ user.first_name }}</span>
              <span v-if="!user.first_name">{{ user.username }}</span>
            </a>
            <div class="dropdown-menu dropdown-menu-right" id="profileDropdown" aria-labelledby="navbarDropdown">
              <span class="dropdown-item-text small" v-if="user.first_name && user.last_name">{{ user.first_name }} {{ user.last_name }} ({{ user.username }})</span>
              <span class="dropdown-item-text small text-muted" v-if="user.persona">{{ user.persona }}</span>
              <div class="dropdown-divider" v-if="user.persona"></div>
              <router-link class="dropdown-item" :to="{name:'Orders'}">Orders</router-link>  
              <router-link class="dropdown-item" :to="{name:'Profile'}">Profile</router-link>  
              <div class="dropdown-divider"></div>
              <a class="dropdown-item" href="#" v-on:click="signOut">Sign Out</a>
            </div>
          </li>        
        </ul>
      </nav>  
    </div>

    <Search/>

  </div>
</template>

<script>
import AmplifyStore from '@/store/store'
import { AmplifyEventBus } from 'aws-amplify-vue';
import { Auth } from 'aws-amplify';
import swal from 'sweetalert';

import Search from './Search.vue'

export default {
  name: 'Navigation',
  components: {
    Search
  },
  props: {
  },
  methods: {
    signIn: function() {
        this.$router.push('/auth')
    },
    signOut: function() {
      let vm = this
      Auth.signOut({ global: true })
        // eslint-disable-next-line no-unused-vars
        .then(data => {
          AmplifyEventBus.$emit('authState', 'signedOut')
          swal("You have been logged out!");
          this.$router.push('/')
          // eslint-disable-next-line
          vm.$forceUpdate()
        })
        .catch(err => swal(err)
      );
    },
  },
  computed: {
    user() { 
      return AmplifyStore.state.user
    }
  }
}
</script>

<style scoped>
.navigation {
  padding-top: 7rem;
}

.nav-bar-bottom {
  margin-top: 40px;
}

#profileDropdown {
  min-width: 5rem;
}
</style>
