<template>
  <div class="content">
    <div class="container">
      <h3>Customer Support</h3>

      <!-- Checking backend indicator -->
      <div class="container mb-4" v-if="checkingBackend">
        <i class="fas fa-spinner fa-spin fa-3x"></i>
      </div>

      <!-- Backend configured -->
      <div v-if="backendConfigured">
        <p>Support available 24/7/365. For immediate assistance please ask a question using the form below and our virtual assistant will direct your request.
        </p>
        <div class="row">
          <div class="col-sm">
            <amplify-chatbot v-bind:chatbotConfig="chatbotConfig" id="chatBot"></amplify-chatbot>
          </div>
          <div class="col-sm">
            <div class="card-deck">
              <div class="card card-recommend mb-3" v-for="card in responseCards" v-bind:key="card.title">
                <img class="card-img-top" :src="card.imageUrl" :alt="card.title">
                <div class="card-body">
                  <h6 class="card-title">{{ card.title }}</h6>
                  <p class="card-text"><small>{{ card.subTitle }}</small></p>
                  <a class="btn btn-secondary btn-block mt-auto" :href="card.attachmentLinkUrl">Learn more...</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Backend NOT configured -->
      <div v-if="!checkingBackend && !backendConfigured">
        <p>The virtual assistant does not appear to be configured for this deployment.
        </p>
      </div>

      <div v-if="error" class="error">
        {{ error }}
      </div>

    </div>
  </div>
</template>

<script>
import { Interactions } from 'aws-amplify';
import { AmplifyEventBus } from 'aws-amplify-vue';

export default {
  name: 'Help',
  components: {
  },
  props: {
  },
  data () {
    return {
      checkingBackend: false,
      backendConfigured: null,
      error: null,
      responseCards: null
    }
  },
  created () {
    this.checkBackend()
  },
  async mounted() {
    AmplifyEventBus.$on('chatResponse', async (response) => {
      var botCtr = document.getElementById('chatBot');
      botCtr.scrollTop = botCtr.scrollHeight;
      if (response.responseCard && response.responseCard.genericAttachments) {
        this.responseCards = response.responseCard.genericAttachments
      }
      else {
        this.responseCards = null
      }
    })
  },
  methods: {
    async checkBackend() {
      this.checkingBackend = true

      try {
        await Interactions.send(this.chatbotConfig.bot, 'Hey Retail Demo Store');
        this.backendConfigured = true
      }
      catch(err) {
        console.error('Error communicating with chatbot: ' + err)
        this.error = err
        this.backendConfigured = false
      }
      finally {
        this.checkingBackend = false
      }
    }
  },
  computed: {
    chatbotConfig: function () {
      let config = {
        bot: process.env.VUE_APP_BOT_NAME,
        clearComplete: false,
        botTitle: "Retail Demo Store Support",
        conversationModeOn: false,
        voiceEnabled: false,
        textEnabled: true
      }
      return config
    }
  },
}
</script>

<style scoped>
  #chatBot {
    margin-top: 0px;
    max-height: 95vh;
    overflow-y: auto;
  }

  .card-recommend {
    min-width: 250px;
  }
</style>