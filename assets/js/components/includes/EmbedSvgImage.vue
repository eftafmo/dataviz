<template>
  <image :href="uri"></image>
</template>

<script>
/**
 * Fetch an image from the URL, and convert it to a base64 URI.
 * Loading images this way ensures that they still work while
 * the chart is downloaded.
 */
export default {
  name: "EmbedSvgImage",
  props: {
    fetchUrl: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      uri: null,
    };
  },
  watch: {
    fetchUrl() {
      this.loadURI();
    },
  },
  mounted() {
    this.loadURI();
  },
  methods: {
    async loadURI() {
      const response = await fetch(this.fetchUrl);
      const blob = await response.blob();

      this.uri = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.addEventListener("load", () => resolve(reader.result));
        reader.addEventListener("error", reject);
        reader.readAsDataURL(blob);
      });
    },
  },
};
</script>

<style scoped></style>