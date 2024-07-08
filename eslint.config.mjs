import path from "node:path";
import { fileURLToPath } from "node:url";
import js from "@eslint/js";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
    baseDirectory: __dirname,
    recommendedConfig: js.configs.recommended,
    allConfig: js.configs.all
});

export default [...compat.extends(
    "plugin:vue/vue3-recommended",
    "plugin:prettier-vue/recommended",
    "prettier",
), {
  rules: {
    "vue/multi-word-component-names": "off",
  },
    settings: {
        "prettier-vue": {
            SFCBlocks: {
                template: true,
                script: true,
                style: true,

                customBlocks: {
                    docs: {
                        lang: "markdown",
                    },

                    config: {
                        lang: "json",
                    },

                    module: {
                        lang: "js",
                    },

                    comments: false,
                },
            },

            usePrettierrc: true,

            fileInfoOptions: {
                ignorePath: ".testignore",
                withNodeModules: false,
            },
        },
    },
}];
