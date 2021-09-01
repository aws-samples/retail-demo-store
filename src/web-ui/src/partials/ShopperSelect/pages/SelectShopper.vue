<template>
  <div>
    <h1 class="heading">Select Shopper</h1>
    <p>
      Select a shopper to see how the personalized product recommendations change based on the shopper’s browsing
      history and interests.
    </p>

    <div class="form-container p-4">
      <div class="mb-4">Use the controls below to select a shopper from the Retail Demo Store user dataset.</div>

      <form @submit.prevent="onSubmit" class="form">
        <div class="form-group d-flex align-items-center">
          <label for="age-range" class="label mr-3 mb-0">1</label>
          <select class="form-control" id="age-range" placeholder="Select age range" v-model="ageRange">
            <option value="">Select age range</option>
            <option value="18-24">18-24 years</option>
            <option value="25-34">25-34 years</option>
            <option value="35-44">35-44 years</option>
            <option value="45-54">45-54 years</option>
            <option value="54-70">54-70 years</option>
            <option value="70-and-above">Above 70 years</option>
          </select>
        </div>

        <div class="form-group d-flex flex-column">
          <div class="d-flex align-items-center">
            <label for="primary-interest" class="label mr-3 mb-0">2</label>
            <select class="form-control" id="primary-interest" v-model="primaryInterest">
              <option value="">Select primary interest</option>

              <template v-if="categories">
                <option v-for="(category, i) in categories" :key="category.id" :value="category.name">{{
                  formattedCategories[i]
                }}</option>
              </template>
            </select>
          </div>

          <a
            href="#"
            type="button"
            class="learn-more"
            data-toggle="tooltip"
            data-placement="bottom"
            data-html="true"
            title="<div class='mb-2'>This demo will enable to choose the primary interest which is highest weighted when producing personalized product recommendations. The second and third category are automatically selected for you and have lower impact on the product recommendations each shopper receives.</div><div><a href='https://github.com/aws-samples/retail-demo-store' target='_blank' rel='noopener noreferrer'>For more info, visit to the GitHub repository.</a></div>"
            ref="learnMore"
          >
            Learn more
          </a>
        </div>

        <div class="text-center">
          <button class="submit btn btn-primary btn-lg" type="submit" :disabled="!(ageRange && primaryInterest)">
            Submit
          </button>
        </div>

        <div v-if="shopperNotFound" class="alert alert-warning mt-4" role="alert">
          A shopper with the selected attributes was not found. Please try a different combination.
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { RepositoryFactory } from '@/repositories/RepositoryFactory';
import { mapGetters, mapState } from 'vuex';

const UsersRepository = RepositoryFactory.get('users');

export default {
  name: 'SelectShopper',
  data() {
    return {
      ageRange: '',
      primaryInterest: '',
      shopperNotFound: false,
    };
  },
  mounted() {
    // eslint-disable-next-line no-undef
    $(this.$refs.learnMore).tooltip();
  },
  beforeDestroy() {
    // eslint-disable-next-line no-undef
    $(this.$refs.learnMore).tooltip('dispose');
  },
  computed: {
    ...mapState({ categories: (state) => state.categories.categories }),
    ...mapGetters(['formattedCategories']),
  },
  methods: {
    async onSubmit() {
      const { primaryInterest, ageRange } = this;

      const { data } = await UsersRepository.getUnclaimedUser({ primaryInterest, ageRange });

      if (!data) {
        this.shopperNotFound = true;
      } else {
        this.$emit('shopperSelected', {
          selection: { primaryInterest, ageRange },
          assignedShopper: data[0],
        });
      }
    },
    resetShopperNotFound() {
      if (this.shopperNotFound) this.shopperNotFound = false;
    },
  },
  watch: {
    primaryInterest() {
      this.resetShopperNotFound();
    },
    ageRange() {
      this.resetShopperNotFound();
    },
  },
};
</script>

<style scoped>
.heading {
  font-size: 1.75rem;
}

.form-container {
  border: 1px solid var(--grey-400);
  border-radius: 4px;
}

.form {
  margin: auto;
  max-width: 350px;
}

.label {
  font-size: 2.5rem;
  color: var(--grey-600);
  width: 25px;
}

.learn-more {
  font-style: italic;
  font-size: 0.9rem;
  color: var(--blue-600);
  align-self: flex-end;
}

.submit {
  width: 200px;
  background: var(--blue-500);
  border-color: var(--blue-500);
}

.submit:hover:not([disabled]),
.submit:focus:not([disabled]) {
  background: var(--blue-600);
  border-color: var(--blue-600);
}
</style>
