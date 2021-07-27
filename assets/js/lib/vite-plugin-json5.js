/**
 * Based on
 * https://github.com/vitejs/vite/blob/main/packages/vite/src/node/plugins/json.ts
 *
 * License: MIT.
 */

import * as JSON5 from "json5";
import { dataToEsm } from "@rollup/pluginutils";

//import { SPECIAL_QUERY_RE } from 'vite/src/node/constants'
const SPECIAL_QUERY_RE = /[\?&](?:worker|raw|url)\b/;

// export interface JsonOptions {
//   /**
//    * Generate a named export for every property of the JSON object
//    * @default true
//    */
//   namedExports?: boolean
//   /**
//    * Generate performant output as JSON.parse("stringified").
//    * Enabling this will disable namedExports.
//    * @default false
//    */
//   stringify?: boolean
// }

const jsonExtRE = /\.json5($|\?)(?!commonjs-proxy)/;

export default function json5Plugin(options = {}, isBuild) {
  return {
    name: "vite-plugin-json5",

    transform(code, id) {
      if (!jsonExtRE.test(id)) return null;
      if (SPECIAL_QUERY_RE.test(id)) return null;

      try {
        if (options.stringify) {
          if (isBuild) {
            return {
              // during build, parse then double-stringify to remove all
              // unnecessary whitespaces to reduce bundle size.
              code: `export default JSON.parse(${JSON.stringify(
                JSON.stringify(JSON5.parse(code))
              )})`,
              map: { mappings: "" },
            };
          } else {
            return `export default ${JSON.stringify(JSON5.parse(code))}`;
          }
        }

        const parsed = JSON5.parse(code);
        return {
          code: dataToEsm(parsed, {
            preferConst: true,
            namedExports: options.namedExports,
          }),
          map: { mappings: "" },
        };
      } catch (e) {
        const errorMessageList = /[\d]+/.exec(e.message);
        const position = errorMessageList && parseInt(errorMessageList[0], 10);
        const msg = position
          ? `, invalid JSON syntax found at line ${position}`
          : `.`;
        this.error(`Failed to parse JSON5 file` + msg, e.idx);
      }
    },
  };
}
