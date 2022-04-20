<template id="js-fenix-template">
  <div class="fenix-branding">
    <div class="fenix-logo">
      <a v-bind:href="currentURL" target="_blank">
        <img src="/fenixcommerce.png" alt="Fenixcommerce" title="Fenixcommerce" height="" />
      </a>
    </div>
    <div class="fenix-text">
      Powered by <a v-bind:href="currentURL" target="_blank">Fenixcommerce</a>
    </div>
  </div>
</template>
<script>
export default {
  name: 'FenixBranding',
  data() {
    return {
      currentURL: 'https://fenixcommerce.com?track='+window.location.href
    };
  }
};
</script>

<style scoped>
.fenix-branding{
  font-size: 0.7rem;
  margin-top: 4px;
  margin-bottom: 4px;
}

.fenix-branding a,
.fenix-branding a:hover, 
.fenix-branding a:focus{
  color: #0073bb;
  text-decoration: none;
}

.fenix-branding .fenix-logo{
  display: inline-block;
  margin-right: 5px;
}

.fenix-branding .fenix-logo img{
  width: 18px;
}

.fenix-branding .fenix-text{
  display: inline-block;
}
</style>