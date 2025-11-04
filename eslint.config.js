import prettierSkipFormatting from "@vue/eslint-config-prettier/skip-formatting";
import pluginPrettier from "eslint-config-prettier";
import pluginCypress from "eslint-plugin-cypress/flat";
import mocha from "eslint-plugin-mocha";
import pluginVue from "eslint-plugin-vue";
import globals from "globals";
import { defineConfig } from "eslint/config";

export default defineConfig([
  {
    files: ["**/*.{ts,mts,tsx,js,mjs,cjs}"],
    name: "app/files-to-lint",
  },
  {
    ignores: ["**/dist/**", "**/dist-ssr/**", "**/coverage/**", "**/node_modules/**", "**/.fs/**", "**/.venv/**"],
    name: "app/files-to-ignore",
  },
  pluginVue.configs["flat/recommended"],
  {
    files: ["cypress/e2e/**/*.{cy,spec}.{js,ts,jsx,tsx}", "cypress/support/**/*.{js,ts,jsx,tsx}"],
    plugins: {
      mocha,
    },
    rules: {
      "mocha/no-exclusive-tests": "error", // disallow `.only`
    },
  },
  {
    ...pluginCypress.configs.recommended,
    files: ["cypress/e2e/**/*.{cy,spec}.{js,ts,jsx,tsx}", "cypress/support/**/*.{js,ts,jsx,tsx}"],
    rules: {
      // expect() expression will be marked as errors otherwise.
      "@typescript-eslint/no-unused-expressions": ["off"],
      // Can't enforce camelCase since it conflicts with some python stuff
      camelcase: ["error", { properties: "never" }],
      "no-unused-expressions": ["off"],
    },
  },
  {
    languageOptions: {
      ecmaVersion: "latest",
      globals: {
        ...globals.browser,
        ...globals.node, // SSR, Electron, config files
        browser: "readonly", // BEX related
        Capacitor: "readonly",
        chrome: "readonly", // BEX related
        cordova: "readonly",
        ga: "readonly", // Google Analytics
        process: "readonly", // process.env.*
      },

      sourceType: "module",
    },

    // add your custom rules here
    rules: {
      "vue/multi-word-component-names": "off",
    },
  },
  prettierSkipFormatting,
  pluginPrettier,
]);
