<template>
  <Modal :ariaLabelledBy="DEMO_GUIDE_TITLE_ID" modalHeaderClass="demo-guide-modal-header">
    <template #header>
      <DemoGuideHeader></DemoGuideHeader>
    </template>

    <template #body="{bodyClass}">
      <div :class="['d-flex body', bodyClass]">
        <transition v-if="isMobile" name="pageTransition">
          <DemoGuideMenu v-if="!selectedArticle" class="mobile-menu"></DemoGuideMenu>
          <DemoGuideArticle v-else :articleId="selectedArticle" class="mobile-article"></DemoGuideArticle>
        </transition>

        <div v-else class="desktop-body-container align-self-stretch d-flex align-items-stretch">
          <DemoGuideMenu class="desktop-menu"></DemoGuideMenu>
          <DemoGuideArticle :articleId="selectedArticle" class="desktop-article"></DemoGuideArticle>
        </div>
      </div>
    </template>
  </Modal>
</template>

<script>
import { mapState } from 'vuex';
import { DEMO_GUIDE_TITLE_ID } from './config';
import { Modals } from '../config';
import Modal from '../Modal/Modal';
import DemoGuideHeader from './DemoGuideHeader/DemoGuideHeader';
import DemoGuideMenu from './DemoGuideMenu/DemoGuideMenu';
import DemoGuideArticle from './DemoGuideArticle/DemoGuideArticle';

export default {
  name: 'DemoGuide',
  components: {
    Modal,
    DemoGuideHeader,
    DemoGuideMenu,
    DemoGuideArticle,
  },
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
  },
};
</script>

<style scoped>
.body {
  padding: 0;
}

.mobile-menu,
.mobile-article {
  position: absolute;
  left: 0;
  width: 100%;
  top: 0;
  height: 100%;
  /* use bootstrap modal body padding */
  padding: 16px;
  transition: transform 150ms ease-in-out;
}

.mobile-menu.pageTransition-enter,
.mobile-menu.pageTransition-leave-to {
  transform: translateX(-100%);
}

.mobile-menu.pageTransition-enter-to,
.mobile-menu.pageTransition-leave {
  transform: translateX(0%);
}

.mobile-article.pageTransition-enter,
.mobile-article.pageTransition-leave-to {
  /* breaks at 100% because article focuses on itself on mount */
  transform: translateX(99%);
}

.mobile-article.pageTransition-enter-to,
.mobile-article.pageTransition-leave {
  transform: translateX(0%);
}

.desktop-body-container {
  flex: 1;
}

.desktop-menu {
  width: 300px;
  /* use bootstrap modal border radius */
  border-bottom-left-radius: 0.3rem;
  padding: 16px;
  padding-top: 0;
}

.desktop-article {
  flex: 1;
  /* use bootstrap modal border radius */
  border-bottom-right-radius: 0.3rem;
  padding: 32px;
}

.mobile-article,
.desktop-article {
  overflow-y: auto;
}

/* keep bottom right border intact */
/* need to style scrollbar in order to change border-radius, so we'll imitate Chrome */
.desktop-article::-webkit-scrollbar-track {
  border-bottom-right-radius: 0.3rem;
}

.desktop-article::-webkit-scrollbar {
  background-color: #f5f5f5;
  border-bottom-right-radius: 0.3rem;
}

.desktop-article::-webkit-scrollbar-thumb {
  border-radius: 10px;
  border: 3px solid #f5f5f5;
  background-color: #c7c7c7;
}
</style>
