<template>
  <Layout :isLoading="isLoading" :previousPageLinkProps="previousPageLinkProps">
    <template #default>
      <div class="container text-left">

        <h1>Your alerts!</h1>
          <div class="num-alerts">
            You have {{numAlerts}} alerts!
          </div>

          <ul class="alerts">
            <div
              v-for="(alert, index) in formattedAlerts"
              :key="index"
              class = "one-alert"
            >
              <h2 class="alert-subject">{{alert.subject}}</h2>
              <div>
                <p v-for="(text, index2) in alert.text"
                      :key="index2"
                      class="alert-text">
                    {{text}}
                </p>
              </div>

            </div>
          </ul>
        </div>

    </template>
  </Layout>
</template>

<script>
import { mapGetters } from 'vuex';
import Layout from "@/components/Layout/Layout";


export default {
  name: 'Alerts',
  components: {
    Layout
  },
  computed: {
    ...mapGetters(['alerts', 'numAlerts']),
    isLoading() {
      return !this.numAlerts
    },
    formattedAlerts() {
      return this.alerts.map(alert => {return {subject: alert.subject,
                                               text: alert.text.split("\n")}})
    },
    previousPageLinkProps() {
      if (!this.lastVisitedPage) return null;
      return { text: 'Continue Shopping', to: this.lastVisitedPage };
    }
  },
};
</script>

<style scoped>

.one-alert {
  border:  1px dotted var(--grey-300);
  border-radius: 2px;
  padding: 1em;
}
.alert-subject {
  font-family: monospace;
}

.alert-text {
  font-family: monospace;
}

.num-alerts {
  padding-bottom: 1em;
}

</style>
