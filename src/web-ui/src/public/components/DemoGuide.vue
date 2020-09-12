<template>
  <div class="demo-guide col-sm-12 col-md-3 col-lg-3 mb-4">

    <!-- Demo guide-->
    <div class="container" v-if="!showLevel">
      <nav class="navbar demo-guide-content fixed-bottom">
         <ul class="navbar-nav mx-auto d-none d-md-block demo-guide-level-1-text" v-on:click="showDemoGuideLevel2()">
          <li class="nav-item" style="font-weight:bold;font-size:x-large">
            DEMO GUIDE<i class="fas fa-caret-up fa-lg" style="padding-left:2em;"></i>
          </li>        
          <li class="nav-item" style="color:#e88b01">
            Learn more about this demo
          </li>                  
        </ul>                                    
      </nav>  
    </div>
        <!-- Demo guide level2-->
    <div class="modal" v-if="showguide">
      <nav class="navbar fixed-bottom" style="padding:0">
         <ul class="navbar-nav mx-auto d-none d-md-block demo-guide-level-2" v-on:click="showDemoGuideLevel2()">
            <li class="nav-item demo-guide-level-1-text" style="font-weight:bold;font-size:x-large">
              <i class="fas fa-chevron-down fa-lg" style="padding-left:2em;"></i>
              DEMO GUIDE <a style="color:#e88b01" >Learn more about this demo</a>
              <i class="fas fa-chevron-down fa-lg" style="padding-left:2em;"></i>
            </li>                     
        </ul>
          <ul class="navbar-nav mx-auto d-none d-md-block demo-guide-level-2" v-on:click="showDemoGuideLevel3()">
            <li class="nav-item demo-guide-level-2-text row" >
              <div class="demo-guide-use-cases col-sm-12 col-md-3 col-lg-3" v-on:click="showDemoGuideUseCases()">
                <p style="margin:1rem;font-weight:bold;font-size:x-large">
                USE CASES ENABLED IN THIS DEMO
                </p>
              <p>Click here to dive deep into the ways Amazon Personalize and other ML Services are used in this demo</p>
              </div>
              <div class="demo-guide-use-cases col-sm-12 col-md-3 col-lg-3" v-on:click="showDemoGuidePersonalizeTopics()">
                <p style="margin:1rem;font-weight:bold;font-size:x-large">
                AMAZON PERSONALIZE USEFUL TOPICS
                </p>
              <p>Dive deeper into some popular topics related to Amazon Personalize</p>
              </div>
              <div class="demo-guide-use-cases col-sm-12 col-md-3 col-lg-3">
                <p style="margin:1rem;font-weight:bold;font-size:x-large">
                ABOUT THIS DEMO
                </p>
              <p>Provide feedback or learn more about the workshops available</p>
              </div>
            </li>    
          </ul>                                    
      </nav>  
    </div>
    <DemoGuideLevel3 :showUseCases="showUseCases" :showPersonalizeTopics="showPersonalizeTopics" :showguidedetails="showguidedetails" @toggleUseCases="hideDemoGuideLevel3()"></DemoGuideLevel3>
  </div>
</template>

<script>

import DemoGuideLevel3 from './DemoGuideLevel3.vue';

export default {
  name: 'DemoGuide',
  components: {
    DemoGuideLevel3
  },
  props: {
  },
  data () {
    return {  
      errors: [],
      showguide: false,
      showguidedetails: false,
      sectionName: 'Amazon Personalize',
      displaySection: 'User Personalization',
      showPersonalizeTopics: false,
      showUseCases: false,
      services: [{
        name: 'Amazon Personalize',
        subsections: [
          {name : 'User Personalization'},
          {name : 'Similar items'},
          {name : 'Personalized ranking'},
          {name : 'Real time events'}
          ]
        },
        {
          name: 'Amazon Pinpoint',
          subsections: [
            {name : 'Welcome Email'},
            {name : 'Abandoned cart email'},
            {name : 'Text alerts(SMS)'}
          ]
        },
        {
          name: 'Amazon Lex',
          subsections: [
            {name : 'Chatbot conversational interfaces'},
          ]
        }
      ]
    }
  },
  computed: {
    showLevel: function() {
      return this.showguide || this.showguidedetails;
    }
  },
  methods: {
    showDemoGuideLevel2: function() {
      this.showguide = !this.showguide;
      this.showUseCases = false;
      this.showPersonalizeTopics = false;
    },
    showDemoGuideLevel3: function() {
      this.showguide = !this.showguide;
      this.showguidedetails = !this.showguidedetails;
    },
    hideDemoGuideLevel3: function() {
      this.showguide = !this.showguide;
      this.showguidedetails = !this.showguidedetails;
      this.showUseCases = false;
      this.showPersonalizeTopics = false;
    },
    showDemoGuideUseCases: function() {
      this.showUseCases = true;
    },
    showDemoGuidePersonalizeTopics: function() {
      this.showPersonalizeTopics = true;
    },
  },
}
</script>

<style scoped>
.demo-guide {
  padding-top: 7rem;
  font-weight: normal;
  font-style: normal;
  @font-face {
  font-family: 'Amazon Ember';
  src: local('../staticData/fonts/amazon-ember_rg.woff2'),url('../staticData/fonts/amazon-ember_rg.woff2'),
  url('../staticData/fonts/amazon-ember_rg.woff');
  }
}
.demo-guide-content {
   background-color: #f8f9fa6b;
   flex-shrink: 0;
   padding: unset;
}
.demo-guide-level-1-text {
   background-color: #152939;
   flex-shrink: 0;
   color: white;
   justify-content: center;
   display: block;
   font-size: large;
   padding: 1em;
   border-top-left-radius: 10px;
   border-top-right-radius: 10px;
}
.demo-guide-level-2-text {
   background-color: #232f3e;
   flex-shrink: 0;
   color: white;
   justify-content: center;
   font-size: medium;
   padding: 1em;
}
.demo-guide-level-3-text {
   background-color: #232f3e;
   flex-shrink: 0;
   color: white;
   font-size: small;
   padding: 1em;
   width: 100%;
}
.demo-guide-level-2{
  text-align: center;
  width: 100%;
  margin: 0;
  padding: 0;
}

.demo-guide-use-cases{
  border:solid;
  border-width: thin;
  width: 27em;
  display: inline-block;
  margin: 1em;
}
.modal {
  width: 100%;
  height: 100%;
  background: #4a4b4cbd;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: block;
  overflow-y: scroll;
}
.sidebar {
  background-color: #31465f;
  overflow-x: hidden;
  box-sizing: border-box;
}
#sublist {
  list-style: none;
  margin: 0;
  padding: 0;
}
.about-service {
  background-color: white;
  color: black;
}
.icon {
  width: 1em;
  height: 1em;
  fill: currentColor;
}
</style>
