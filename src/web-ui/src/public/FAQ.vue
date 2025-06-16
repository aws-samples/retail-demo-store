<template>
  <Layout :isLoading="isLoading" :previousPageLinkProps="previousPageLinkProps">
    <template #default>
        <h2 class="faq-title">Frequently Asked Questions</h2>
        <div class="accordion" id="faqAccordion">
          <div class="card" v-for="(item, index) in faqItems" :key="index">
            <div class="card-header" :id="'heading' + index">
              <h3 class="mb-0">
                <button
                    class="btn btn-link"
                    type="button"
                    data-toggle="collapse"
                    :data-target="'#collapse' + index"
                    :aria-expanded="index === 0"
                    :aria-controls="'collapse' + index">
                  {{ item.question }}
                </button>
              </h3>
            </div>
            <div
                :id="'collapse' + index"
                class="collapse"
                :class="{ 'show': index === 0 }"
                :aria-labelledby="'heading' + index"
                data-parent="#faqAccordion">
              <div class="card-body">
                {{ item.answer }}
              </div>
            </div>
          </div>
        </div>
    </template>
  </Layout>
</template>

<script>

import Layout from '@/components/Layout/Layout.vue';

export default {
  name: 'FAQ',
  components: {Layout},
  data() {
    return {
      faqItems: [
        {
          question: 'How do I create an account?',
          answer: 'You can create an account by clicking the "Sign Up" button in the top right corner and filling out the registration form.'
        },
        {
          question: 'What payment methods do you accept?',
          answer: 'We accept all major credit cards, debit cards, and digital payment methods.'
        },
        {
          question: 'How can I track my order?',
          answer: 'Once your order is shipped, you will receive a tracking number via email. You can use this number to track your package in your account dashboard.'
        },
        {
          question: 'Can I return or replace my order?',
          answer: 'Once your order is delivered, you will have 30 days to return or replace your order.'
        },
        // Add more FAQ items as needed
      ]
    }
  },
  computed: {
    isLoading() {
      return false;
    },
    previousPageLinkProps() {
      return null;
    }
  }
}
</script>

<style scoped>

.faq-title {
  text-align: center;
  margin-bottom: 2rem;
}

.card {
  margin-bottom: 0.5rem;
}

.card-header {
  background-color: #f8f9fa;
}

.btn-link {
  color: #123456;
  text-decoration: none;
  width: 100%;
  text-align: left;
}

.btn-link:hover {
  text-decoration: none;
  color: #0056b3;
}

.card-body {
  padding: 1.25rem;
}
</style>
