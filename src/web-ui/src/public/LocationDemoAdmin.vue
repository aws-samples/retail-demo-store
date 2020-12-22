<template>
 <Layout>
   <div class="content">
     <location-demo-navigation/>
     <div class="container">
       <div class="row">
         <div class=col>
           <h4>Reset Personalize</h4>
           <hr/>
           <button type="button" class="btn btn-primary" data-toggle="modal" data-target="#resetCampaigns">
             Reset Personalize Campaigns
           </button>
           <div class="modal fade" id="resetCampaigns" tabindex="-1" role="dialog" aria-labelledby="resetCampaignsModalLabel"
                aria-hidden="true">
             <div class="modal-dialog" role="document">
               <div class="modal-content">
                 <div class="modal-header">
                   <h5 class="modal-title" id="resetCampaignsModalLabel">Confirm</h5>
                   <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                     <span aria-hidden="true">&times;</span>
                   </button>
                 </div>
                 <div class="modal-body text-left">
                   Resetting Personalize campaigns will remove all Personalize resources & interactions and retrain
                   campaigns from scratch.
                   <br><br>
                   This process takes approximately 3 hours and no campaigns will be available during this time.
                 </div>
                 <div class="modal-footer">
                   <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
                   <button type="button" class="btn btn-primary" v-on:click="resetCampaigns">Confirm Reset</button>
                 </div>
               </div>
             </div>
           </div>
         </div>
       </div>
     </div>
   </div>
 </Layout>
</template>

<script>
import Layout from "@/components/Layout/Layout";
import LocationDemoNavigation from "@/public/LocationDemoNavigation";
import {RepositoryFactory} from "@/repositories/RepositoryFactory";

const RecommendationsRepository = RepositoryFactory.get('recommendations')

export default {
name: "LocationDemoAdmin",
  components: {
    Layout,
    LocationDemoNavigation
  },
  methods: {
   async resetCampaigns() {
     await RecommendationsRepository.resetRealtimeRecommendations();
   }
  }
}
</script>

<style scoped>

</style>