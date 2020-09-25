<template>
        <!-- Demo guide level3-->
    <div class="modal" v-if="showGuideDetails">
      <nav class="navbar modal-dialog-centered no-padding no-margin h-100" v-if="showUseCases">
        <div class="row h-100 w-100">
          <div class="col-sm-8 col-md-8 col-lg-8 offset-sm-2 offset-md-2 offset-lg-2 demo-guide-level-3-text">
            <ul class="col-sm-12 col-md-12 col-lg-12">
              <p class="nav-item">
                Demo Guide/ Use cases enabled in this demo/ <b>{{sectionName}}</b>
                <i class="fas fa-times fa-lg float-right" v-on:click="toggleLevel3Click()"></i>
              </p>                     
            </ul>
            <div class="row h-100">
              <div class="col-sm-3 col-md-3 col-lg-3">
                <div class="line-height-1 small" v-for="service in services" v-bind:key=service.name> 
                   <LexIcon v-if="service.name=='Amazon Lex'"></LexIcon>
                   <PersonalizeIcon v-if="service.name=='Amazon Personalize'"></PersonalizeIcon>
                   <PinpointIcon v-if="service.name=='Amazon Pinpoint'"></PinpointIcon>
                  <b>{{service.name}}</b>
                  <ul id="sublist" class="no-padding no-margin">
                    <li v-for="subsection in service.subsections" v-bind:key=subsection.name @click="updateSectionProps(subsection.name, service.name)" class="p-2" :class="{'activeSection': displaySection === subsection.name}">
                       {{subsection.name}}
                    </li> 
                  </ul>
                  <hr>
                </div>
              </div>
              <DemoGuideServiceDetails v-bind:sectionToDisplay="displaySection"/>
            </div>
          </div>
        </div>
      </nav>
      <!-- Personalize topics-->
      <nav class="navbar modal-dialog-centered no-padding no-margin h-100" v-if="showPersonalizeTopics">
        <div class="row h-100 w-100" >
          <div class="col-sm-8 col-md-8 col-lg-8 offset-sm-2 offset-md-2 offset-lg-2 demo-guide-level-3-text">
            <ul class="col-sm-12 col-md-12 col-lg-12">
              <p class="nav-item">
                Demo Guide/ <b>Amazon Personalize Popular Topics</b>
                <i class="fas fa-times fa-lg float-right" v-on:click="toggleLevel3Click()"></i>
              </p>                     
            </ul>
            <div class="row h-100">
              <div class="col-sm-3 col-md-3 col-lg-3 line-height-1">
                <div v-for="personalizeTopic in personalizePopularTopics" v-bind:key=personalizeTopic.name> 
                   <PersonalizeIcon></PersonalizeIcon>
                  <b>{{personalizeTopic.name}}</b>
                  <hr class="mt-2 mb-2">
                  <ul id="sublist" class="no-padding">
                    <li v-for="topic in personalizeTopic.topics" v-bind:key=topic.name @click="updatePersonalizeTopicSelection(topic.name)" :class="{'activeSection': personalizeTopicToDisplay === topic.name}" >
                       <span class="line-height-1 small">{{topic.name}}</span>
                       <hr class="bg-white mt-2 mb-2">
                    </li> 
                  </ul>
                  <hr>
                </div>
              </div>
              <DemoGuideServiceDetails v-bind:sectionToDisplay="personalizeTopicToDisplay"/>
            </div>
          </div>
        </div>
      </nav>    
    </div>
</template>
<script>

import DemoGuideServiceDetails from '../DemoGuideServiceDetails';
import LexIcon from '../../../images/icon_lex_orange.vue';
import PersonalizeIcon from '../../../images/icon_personalize_orange.vue';
import PinpointIcon from '../../../images/icon_Pinpoint_orange.vue';
import ServiceUseCases from '../staticData/useCases.json';
import PersonalizePopularTopics from '../staticData/personalizePopularTopics.json';

export default {
  name: 'DemoGuideLevel3',
  components: {
  DemoGuideServiceDetails,
   LexIcon,
   PersonalizeIcon,
   PinpointIcon
  },
  props: {
      showGuideDetails: Boolean,
      showGuide: Boolean,
      showUseCases: Boolean,
      showPersonalizeTopics: Boolean,
  },
  data () {
    return {  
      errors: [],
      sectionName: 'Amazon Personalize',
      displaySection: 'User Personalization',
      personalizeTopicToDisplay: 'Is Amazon Personalize the right solution for my business?',
      services: ServiceUseCases,
      personalizePopularTopics: PersonalizePopularTopics,
    }
  },
  methods: {
    toggleLevel3Click: function() {
      this.$emit('toggleUseCases');
    },
    updateSectionProps: function(subSectionName, serviceName) {
      this.displaySection = subSectionName;
      this.sectionName = serviceName;
    },
    updatePersonalizeTopicSelection: function(topicName){
      this.personalizeTopicToDisplay = topicName;
      console.log(this.personalizeTopicToDisplay);
    }
  },
}
</script>

<style scoped>
.demo-guide {
  padding-top: 7rem;
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
   font-size: large;
   padding: 1em;
}
.demo-guide-level-3-text {
   background-color: #232f3e;
   font-size: medium;
   flex-shrink: 0;
   color: white;
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
.activeSection {
    background-color: #e88b01;
}
.no-padding {
   padding: 0;
}
.no-margin {
  margin: 0 ;
}
.line-height-1 {
  line-height: 1;
}
</style>
