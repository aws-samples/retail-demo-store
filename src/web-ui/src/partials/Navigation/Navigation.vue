<template>
  <nav class="navigation fixed-top pt-2 p-lg-1">
    <div class="nav-contents container d-lg-flex align-items-center">
      <HomeLink class="logo"></HomeLink>
      <ShopDropdown class="shop mx-lg-2"></ShopDropdown>
      <Search class="search mx-lg-4 d-lg-inline-flex collapse multi-collapse"></Search>
      <UserDropdown class="user-dropdown d-lg-block collapse multi-collapse"></UserDropdown>
      <NavSeparator class="d-none d-lg-block mx-2"></NavSeparator>
      <ScanLink class="scan"></ScanLink>
      <NavSeparator class="sep-1 mx-2"></NavSeparator>
      <SupportLink class="support"></SupportLink>
      <NavSeparator class="sep-2 mx-2"></NavSeparator>
      <CartLink class="cart"></CartLink>
    </div>
    <div class="collapse-area d-lg-none">
      <button class="btn collapse-button collapsed w-100" data-toggle="collapse" data-target=".multi-collapse"/>
    </div>
  </nav>
</template>

<script>
import HomeLink from './HomeLink/HomeLink';
import ShopDropdown from './ShopDropdown/ShopDropdown';
import Search from './Search/Search';
import SupportLink from './SupportLink/SupportLink';
import NavSeparator from './NavSeparator/NavSeparator';
import CartLink from './CartLink/CartLink';
import UserDropdown from './UserDropdown/UserDropdown';
import ScanLink from "@/partials/Navigation/ScanLink/ScanLink";

export default {
  name: 'Navigation',
  components: {
    ScanLink,
    HomeLink,
    ShopDropdown,
    Search,
    SupportLink,
    NavSeparator,
    CartLink,
    UserDropdown,
  },
};
</script>

<style scoped>
.navigation {
  background: var(--white);
  border-bottom: 1px solid var(--grey-500);
  box-shadow: 6px 2px 6px var(--grey-200);
}

.logo {
  grid-area: Logo;
  width: 80px;
}

.shop {
  grid-area: Shop;
}

.search {
  grid-area: Search;
  justify-self: end;
}

.user-dropdown {
  grid-area: UserDropdown;
  justify-self: start;
  /* max-width: 250px; */
}

.support {
  grid-area: Support;
}

.scan {
  grid-area: Scan;
}

.sep-1 {
  grid-area: Sep1;
  justify-self: end;
}

.sep-2 {
  grid-area: Sep2;
  justify-self: end;
}

.cart {
  grid-area: Cart;
  justify-self: end;
}

.collapse-area {
  line-height: 1 !important;
}

.collapse-button {
  background-color: var(--grey-300);
  border-radius: 0;
  height: 10px;
  line-height: 10px;
  font-size: 12px;
}

.collapse-button:hover {
  background-color: var(--grey-400);
}

.collapse-button:focus {
  box-shadow: none;
}

button.btn.collapsed:before {
  content: ' ̌' ;
  font-size: 22px;
}
button.btn:before {
  content: '^' ;
  font-size: 12px;
}

.nav-contents {
  display: grid;
  grid-template-columns: repeat(2, auto) auto 1fr auto repeat(5, auto);
  grid-template-rows: repeat(2, auto);
  grid-row-gap: 10px;
  /* let second row components take more space if they need to */
  grid-template-areas:
    'Shop Logo . . . Scan Sep1 Support Sep2 Cart'
    'UserDropdown UserDropdown UserDropdown UserDropdown . Search Search Search Search Search';
}

@media (min-width: 992px) {
  .logo {
    width: 120px;
  }

  .search {
    flex: 1;
  }
}
</style>
