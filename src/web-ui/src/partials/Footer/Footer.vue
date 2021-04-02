<template>
  <footer>
    <div class="justify-content-center d-flex align-items-center">
      <div class="rds">Retail Demo Store</div>
      <div class="separator mx-2" aria-hidden></div>
      <PoweredByAWS class="img"></PoweredByAWS>
    </div>

    <TermsAndConditions></TermsAndConditions>
  </footer>
</template>

<script>
import PoweredByAWS from '@/components/PoweredByAWS/PoweredByAWS';
import TermsAndConditions from '@/partials/TermsAndConditions/TermsAndConditions';

export default {
  name: 'Footer',
  components: { PoweredByAWS, TermsAndConditions },
};
</script>

<style scoped>
.rds {
  font-weight: bold;
}

.separator {
  height: 30px;
  width: 2px;
  background: var(--grey-600);
}

.img {
  /* fine-tuning to match other copy in footer */
  margin-top: 10px;
  height: 30px;
}

@media (min-width: 576px) {
  .rds {
    font-size: 1.4rem;
  }

  .separator {
    height: 40px;
  }

  .img {
    margin-top: 14px;
    height: 40px;
  }
}
</style>
