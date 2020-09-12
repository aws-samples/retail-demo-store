<template>
  <div class="demo-guide col-sm-12 col-md-9 col-lg-9 mb-4 about-service" style="padding:0">
        <div v-for="subsection in subsections" v-bind:key=subsection.name style="padding:1em;" :style="{display: displaysection === subsection.name ? 'block' : 'none' }">
            <span>
                <h3>{{subsection.title}}</h3>
                <p>{{subsection.recipe}}</p>
                <hr style="color:white">
                <ol>
                  <li v-for="items in subsection.orderedlist" v-bind:key="items.name">
                    <span v-html="items.item"></span>
                  </li>
                </ol>
                <span v-html="subsection.text"></span>
                <hr style="color:white">
                <em>{{subsection.italicText}}</em>
            </span>
        </div>
  </div>
</template>

<script>

import TopicDetails from './staticData/topicDetails.json';
export default {
  name: 'DemoGuideServiceDetails',
  props: {
      displaysection: String
  },
  data () {
    return {  
      errors: [],
      subsections: TopicDetails
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
   flex-shrink: 0;
   color: white;
   font-size: large;
   padding: 1em;
   width: 100%;
}
.demo-guide-level-2{
  text-align: center;
  width: 100%;
  margin: 0;
  padding: 0;
}
.demo-guide-level-3{
  text-align: center;
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
.active {
    display: block;
}
</style>
