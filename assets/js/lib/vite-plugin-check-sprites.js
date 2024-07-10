import * as fs from "fs";
import { glob } from "glob";

export default function checkSprites(pathGlob, maxSize) {
  return {
    name: "check-sprites",
    buildStart() {
      glob(pathGlob, (er, files) => {
        files.forEach((file) => {
          const stat = fs.statSync(file);
          if (stat.isFile() && stat.size >= maxSize) {
            this.error(
              `Sprite size too large, ${stat.size} >= ${maxSize} bytes: ${file}`,
            );
          }
        });
      });
    },
  };
}
