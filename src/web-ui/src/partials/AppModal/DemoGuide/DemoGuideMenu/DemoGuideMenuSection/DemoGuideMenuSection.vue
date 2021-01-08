<template>
  <section class="section py-1 px-2">
    <button
      :id="headingId"
      class="heading-button py-2 d-flex justify-content-between align-items-start text-left"
      :aria-expanded="!!shouldInitiallyBeExpanded"
      data-toggle="collapse"
      :data-target="`#${collapseId}`"
      :aria-controls="collapseId"
    >
      {{ heading }}
      <i class="chevron fa fa-chevron-up ml-2"></i>
    </button>

    <ul
      :id="collapseId"
      :class="{ 'articles collapse m-0 pl-4': true, show: shouldInitiallyBeExpanded }"
      :aria-labelledBy="headingId"
      :data-parent="`#${menuAccordionId}`"
    >
      <li v-for="(article, i) in section.articles" :key="article" class="article mb-2">
        <a
          href="#"
          @click="() => selectArticle(article)"
          :class="{ 'article-button text-left': true, 'article-button--selected': article === selectedArticle }"
          >{{ articleTitles[i] }}</a
        >
      </li>
    </ul>
  </section>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { sectionHeadings, articleTitles, getSectionIdFromArticleId } from '../../config';

export default {
  name: 'DemoGuideMenuSection',
  props: {
    section: { type: Object, required: true },
    menuAccordionId: { type: String, required: true },
  },
  computed: {
    ...mapState({
      selectedArticle: (state) => state.modal.openModal?.selectedArticle,
    }),
    shouldInitiallyBeExpanded() {
      return this.selectedArticle && this.section.id === getSectionIdFromArticleId(this.selectedArticle);
    },
    headingId() {
      return `demo-guide-section-heading-${this.section.id}`;
    },
    collapseId() {
      return `demo-guide-section-${this.section.id}`;
    },
    heading() {
      return sectionHeadings[this.section.id].toUpperCase();
    },
    articleTitles() {
      return this.section.articles.map((articleId) => articleTitles[articleId]);
    },
  },
  methods: { ...mapActions(['selectArticle']) },
};
</script>

<style scoped>
.section {
  border: 1px solid var(--grey-600);
}

.heading-button {
  width: 100%;
  border: none;
  background: inherit;
  font-size: 1rem;
  color: inherit;
  transition: color 150ms ease-in-out;
}

.heading-button:focus {
  outline: none;
}

.heading-button:hover,
.heading-button:focus {
  color: var(--amazon-orange);
}

.chevron {
  transform: rotate(180deg);
  transition: transform 150ms ease-in-out;
  font-size: 1.15rem;
}

.heading-button[aria-expanded='true'] .chevron {
  transform: rotate(0deg);
}

.articles {
  list-style-type: none;
}

.article:last-of-type {
  margin-bottom: 0;
}

.article-button {
  color: inherit;
  transition: color 150ms ease-in-out;
}

.article-button:hover {
  text-decoration: none;
}

.article-button:focus {
  outline: none;
}

.article-button:hover,
.article-button:focus,
.article-button--selected {
  color: var(--amazon-orange);
}
</style>
