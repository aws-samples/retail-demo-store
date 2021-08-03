<template>
  <ModalHeader :class="{ 'header align-items-center': true, 'header--mobile': isMobile }">
    <button
      v-if="isMobile && selectedArticle"
      aria-label="close article"
      @click="closeArticle"
      class="back-button mr-2 px-2"
    >
      <i class="fa fa-chevron-left"></i>
    </button>

    <h1 :id="DEMO_GUIDE_TITLE_ID" class="modal-title">
      DEMO GUIDE
    </h1>

    <span v-if="!isMobile">
      <span class="mx-2">/</span>{{ selectedSectionTitle }}<span class="mx-2">/</span>{{ selectedArticleTitle }}
    </span>
  </ModalHeader>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import ModalHeader from '../../Modal/ModalHeader/ModalHeader';
import { DEMO_GUIDE_TITLE_ID, getSectionIdFromArticleId, sectionHeadings, articleTitles } from '../config';
import { Modals } from '../../config';

export default {
  name: 'DemoGuideHeader',
  components: { ModalHeader },
  data() {
    return { DEMO_GUIDE_TITLE_ID };
  },
  computed: {
    ...mapState({
      selectedArticle: (state) => {
        if (state.modal.openModal?.name !== Modals.DemoGuide) throw new Error('Demo guide not open!');

        return state.modal.openModal.selectedArticle;
      },
      isMobile: (state) => state.modal.isMobile,
    }),
    selectedSectionTitle() {
      return this.selectedArticle ? sectionHeadings[getSectionIdFromArticleId(this.selectedArticle)] : null;
    },
    selectedArticleTitle() {
      return this.selectedArticle ? articleTitles[this.selectedArticle] : null;
    },
  },
  methods: {
    ...mapActions(['closeArticle']),
  },
};
</script>

<style scoped>
.header--mobile {
  border-radius: 0;
}


.header {
  /* fix height to avoid elements jumping up and down based on back button presence */
  height: 60px;
  background: var(--aws-deep-squid-ink);
  color: var(--white);
}

.back-button {
  border: 1px solid var(--white);
  background: inherit;
  color: inherit;
  transition: color 150ms ease-in-out, border-color 150ms ease-in-out;
}

.back-button:focus {
  outline: none;
}

.back-button:hover,
.back-button:focus {
  color: var(--amazon-orange);
  border-color: var(--amazon-orange);
}

.modal-title {
  font-size: 1rem;
}
</style>
