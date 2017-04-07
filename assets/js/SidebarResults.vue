<template>
  <div id="sidebar-results" class="sidebar sidebar-results"
       v-on:click="expand">

    <div class="sidebar-header">
      {{ message }}
      <span v-bind:id="message">Asta totusi se randeaza</span>
      <tag :dismissable="true">it</tag> <tag>works</tag>
    </div>

    <div class="sidebar-tabs">
      <nav class="sidebar-tab-menu">
        <a class="sidebar-tab-menu-item active">
          Results
          <span class="counter">14</span>
        </a>
        <a class="sidebar-tab-menu-item">
          Programmes
          <span class="counter">156</span>
        </a>
      </nav>

    </div>
  </div>
</template>

<style>

</style>

<script>
  import Vue from 'vue';

  export default Vue.extend({
    data() {
      return {
        message: "Am triumfat"
      };
    },
    methods: {
      expand() {
        console.log("i think i just expanded something");
      },
    },
  });
</script>
