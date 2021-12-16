<template>
  <div>
    <ul class="nav nav-tabs">
      <li class="nav-item" @click="() => selectTopic('environment')">
        <div class="nav-link btn-link" v-bind:class="{ active: selectedTopic === 'environment' }">
          Sustainability
        </div>
      </li>
      <li class="nav-item" @click="() => selectTopic('sourcing')">
        <div class="nav-link btn-link" v-bind:class="{ active: selectedTopic === 'sourcing' }">
          Sourcing
        </div>
      </li>
      <li class="nav-item" @click="() => selectTopic('live')">
        <div class="nav-link btn-link" v-bind:class="{ active: selectedTopic === 'live' }">
          Live
        </div>
      </li>
    </ul>
    <div class="tab-content p-3">
      <div class="tab-pane fade show active">
        <div class="mb-2 experiment align-items-center text-muted small">
          You are being shown this based on your browsing habits
        </div>
        <div v-if="selectedTopic === 'environment'">
          <div class="mb-2">
            <i class="fa fa-leaf mr-1"></i> Production emissions: 2.60kg CO<sub>2</sub>
          </div>
          <div>
            This product is produced responsibly and is compliant with our climate pledge
          </div>
        </div>
        <div v-else-if="selectedTopic === 'sourcing'">
          <div class="mb-2">
            <i class="fa fa-industry mr-1"></i> This product is manufactured in the USA
          </div>
          <div>
            All materials for the product are ethically sourced from our trusted suppliers around the world
          </div>
        </div>
        <div v-else-if="selectedTopic === 'live'">
          <div class="mb-2">
            <i class="fa fa-video mr-1"></i> Watch live streams with similar products
          </div>
          <div>
            <router-link to="/live">Click here</router-link> to watch a live stream featuring this product and other influencer favourites!
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {mapState} from "vuex";

const validTopics = ['environment', 'sourcing', 'live']

export default {
  name: "ProductDeepDive",
  data: function () {
    return {
      selectedTopic: null
    }
  },
  created() {
    this.selectedTopic = this.preferredTopic
  },
  methods: {
    selectTopic(topicName) {
      if (validTopics.includes(topicName)) {
        this.selectedTopic = topicName
      } else {
        console.error('Invalid topic name selected')
      }
    },
  },
  computed: {
    ...mapState(['user']),
    preferredTopic() {
      let prefersEnv = ['instruments', 'electronics', 'furniture', 'groceries', 'books']
      let prefersSourcing = ['outdoors', 'accessories', 'tools', 'housewares', 'seasonal']
      let prefersLive = ['beauty', 'homedecor', 'apparel', 'footwear', 'floral']
      let userPersonaFirst = this.user?.persona.split('_')[0].toLowerCase()
      if (prefersEnv.includes(userPersonaFirst)) {
        return 'environment'
      } else if (prefersSourcing.includes(userPersonaFirst)) {
        return 'sourcing'
      } else if (prefersLive.includes(userPersonaFirst)) {
        return 'live'
      } else {
        // Catch all, in case further personas are added in future
        return 'environment'
      }
    }
  }
}
</script>

<style scoped>
.nav-link {
  cursor: pointer;
}

.tab-content {
  border-bottom: var(--grey-300) 1px solid;
  border-left: var(--grey-300) 1px solid;
  border-right: var(--grey-300) 1px solid;
  border-bottom-left-radius: 0.25rem;
  border-bottom-right-radius: 0.25rem;
}
</style>