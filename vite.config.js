import * as path from "path";

import vue from "@vitejs/plugin-vue";
import json5 from "./assets/js/lib/vite-plugin-json5.js";
import checkSprites from "./assets/js/lib/vite-plugin-check-sprites";

// see https://vitejs.dev/config/

export default ({ mode }) => {
  return {
    // XXX Abort build if sprites are larger than the inline limit.
    // XXX Otherwise, sprites cannot be used in downloadable charts.
    // XXX Any larger images should go into the `img` folder instead.
    assetsInlineLimit: 8192,
    plugins: [vue(), json5(), checkSprites("assets/sprites/**/*", 8192)],
    resolve: {
      alias: {
        "@js": path.resolve(__dirname, "assets/js"),
        "@css": path.resolve(__dirname, "assets/css"),
      },
      extensions: [".js", ".vue"],
    },

    build: {
      // publish the manifest, django uses it in templates
      manifest: true,
      // the build directory
      outDir: path.resolve(__dirname, "../build"),
      minify: mode === "production",
      emptyOutDir: true,
      brotliSize: false,

      rollupOptions: {
        input: ["assets/entry.js", "assets/site.js"],
      },
    },
  };
};
