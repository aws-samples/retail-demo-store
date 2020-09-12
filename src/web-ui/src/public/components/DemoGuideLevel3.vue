<template>
        <!-- Demo guide level3-->
    <div class="modal" v-if="showguidedetails">
      <nav class="navbar modal-dialog-centered" style="padding:0;margin:0;height:100%" v-if="showUseCases">
        <div class="row" style="width: 100%;height:100%">
          <div class="col-sm-8 col-md-8 col-lg-8 offset-sm-2 offset-md-2 offset-lg-2 demo-guide-level-3-text">
            <ul class="col-sm-12 col-md-12 col-lg-12">
              <p class="nav-item">
                Demo Guide/ Use cases enabled in this demo/ <b>{{sectionName}}</b>
                <i class="fas fa-times fa-lg" style="float:right;" v-on:click="toggleLevel3Click()"></i>
              </p>                     
            </ul>
            <div class="row" style="height: 100%;">
              <div class="col-sm-3 col-md-3 col-lg-3">
                <div id="service" v-for="service in services" v-bind:key=service.name> 
                   <LexIcon v-if="service.name=='Amazon Lex'"></LexIcon>
                   <PersonalizeIcon v-if="service.name=='Amazon Personalize'"></PersonalizeIcon>
                   <PinpointIcon v-if="service.name=='Amazon Pinpoint'"></PinpointIcon>
                  <b>{{service.name}}</b>
                  <ul id="sublist">
                    <li v-for="subsection in service.subsections" v-bind:key=subsection.name @click="updateSectionProps(subsection.name, service.name)" :class="{'activeSection': displaySection === subsection.name}" style="padding:8px;">
                       {{subsection.name}}
                    </li> 
                  </ul>
                  <hr>
                </div>
              </div>
              <DemoGuideServiceDetails v-bind:displaysection="displaySection"/>
            </div>
          </div>
        </div>
      </nav>
      <!-- Personalize topics-->
      <nav class="navbar modal-dialog-centered" style="padding:0;margin:0;height:100%" v-if="showPersonalizeTopics">
        <div class="row" style="width: 100%;height:100%">
          <div class="col-sm-8 col-md-8 col-lg-8 offset-sm-2 offset-md-2 offset-lg-2 demo-guide-level-3-text">
            <ul class="col-sm-12 col-md-12 col-lg-12">
              <p class="nav-item">
                Demo Guide/ <b>Amazon Personalize Popular Topics</b>
                <i class="fas fa-times fa-lg" style="float:right;" v-on:click="toggleLevel3Click()"></i>
              </p>                     
            </ul>
            <div class="row" style="height: 100%;">
              <div class="col-sm-3 col-md-3 col-lg-3" style="line-height:1">
                <div v-for="personalizeTopic in personalizePopularTopics" v-bind:key=personalizeTopic.name> 
                   <PersonalizeIcon></PersonalizeIcon>
                  <b>{{personalizeTopic.name}}</b>
                  <hr style="margin-top:0.5rem; margin-bottom:0.5rem,background:#f1faff">
                  <ul id="sublist">
                    <li v-for="topic in personalizeTopic.topics" v-bind:key=topic.name @click="updatePersonalizeTopicSelection(topic.name)" :class="{'activeSection': personalizeTopicToDisplay === topic.name && topic.name!== 'Use Case for Personalization'}" >
                       <span style="line-height:1;font-size:small">{{topic.name}}</span>
                       <ul id="sublist" v-if="topic.name === 'Use Case for Personalization'">
                          &nbsp; &emsp;<li v-for="subtopic in personalizeTopic.subtopics" v-bind:key=subtopic.name @click.stop="updatePersonalizeTopicSelection(subtopic.name)" :class="{'activeSection': personalizeTopicToDisplay === subtopic.name}" style="padding:8px;font-size:small">
                            {{subtopic.name}}
                          </li>
                       </ul>
                       <hr style="margin-top:0.5rem; margin-bottom:0.5rem">
                    </li> 
                  </ul>
                  <hr>
                </div>
              </div>
              <DemoGuideServiceDetails v-bind:displaysection="personalizeTopicToDisplay"/>
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
      showguidedetails: Boolean,
      showguide: Boolean,
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
  margin: 0;
  padding: 0;
}
#service {
  font-size: small;
  line-height: 1;
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
</style>
