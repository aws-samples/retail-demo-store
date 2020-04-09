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
          <div class="col-lg-12">
            <amplify-chatbot v-bind:chatbotConfig="chatbotConfig" class="chatBot"></amplify-chatbot>
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
      error: null
    }
  },
  created () {
    this.checkBackend()
  },
  methods: {
    async checkBackend() {
      this.checkingBackend = true

      try {
        await Interactions.send(this.chatbotConfig.bot, 'Hey TGS');
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
        bot: "RetailDemoStore",
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