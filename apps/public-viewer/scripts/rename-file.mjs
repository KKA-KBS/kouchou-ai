import { constants } from "node:fs";
import { access, copyFile, readFile, rename, unlink, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

// サーバー起動ではクッキーを読むため force-dynamic。静的書き出しは force-static でないと build できない。
const dynamicPages = ["app/page.tsx", "app/[slug]/page.tsx", "app/faq/page.tsx"];
const forceDynamic = 'export const dynamic = "force-dynamic";';
const forceStatic = 'export const dynamic = "force-static";';

let ignoreFiles = [];

if (process.env.NEXT_PUBLIC_OUTPUT_MODE === "export") {
  // static build 時にビルド対象から除外するファイル
  ignoreFiles = ["app/[slug]/opengraph-image.tsx", "app/[slug]/opengraph-image.png"];
} else {
  // 通常のビルド時にビルド対象から除外するファイル
  ignoreFiles = ["app/[slug]/opengraph-image.png/route.ts"];
}

/**
 * Rename a file with fallback to copy+delete for cross-device operations
 * @param {string} oldPath - Source file path
 * @param {string} newPath - Destination file path
 */
async function renameWithFallback(oldPath, newPath) {
  try {
    await rename(oldPath, newPath);
  } catch (error) {
    // EXDEV error occurs when trying to rename across different filesystems/mount points
    // Fall back to copy+delete approach
    if (error.code === "EXDEV") {
      await copyFile(oldPath, newPath);
      await unlink(oldPath);
    } else {
      throw error;
    }
  }
}

async function setPageDynamic(next) {
  if (process.env.NEXT_PUBLIC_OUTPUT_MODE !== "export") return;
  const from = next === "force-static" ? forceDynamic : forceStatic;
  const to = next === "force-static" ? forceStatic : forceDynamic;
  for (const file of dynamicPages) {
    const filePath = resolve(file);
    const text = await readFile(filePath, "utf8");
    if (!text.includes(from)) continue;
    await writeFile(filePath, text.replace(from, to));
  }
}

export async function renameFiles() {
  await setPageDynamic("force-static");
  for (const file of ignoreFiles) {
    const filePath = resolve(file);
    const renamedPath = resolve(file.replace(/([^/]+)$/, "_$1"));

    try {
      await access(filePath, constants.F_OK);
      await renameWithFallback(filePath, renamedPath);
      console.log(`Renamed: ${file} → _${file.split("/").pop()}`);
    } catch (error) {
      console.warn(`Skipping rename for ${file}: ${error.message}`);
    }
  }
}

export async function restoreFiles() {
  await setPageDynamic("force-dynamic");
  for (const file of ignoreFiles) {
    const filePath = resolve(file);
    const renamedPath = resolve(file.replace(/([^/]+)$/, "_$1"));

    try {
      await access(renamedPath, constants.F_OK);
      await renameWithFallback(renamedPath, filePath);
      console.log(`Restored: _${file.split("/").pop()} → ${file}`);
    } catch (error) {
      console.warn(`Skipping restore for ${file}: ${error.message}`);
    }
  }
}

// ビルドを包むスクリプト（with-renamed-files.mjs）から関数として読み込めるよう、
// 直接実行されたときだけ CLI として動く
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const action = process.argv[2];

  if (action !== "rename" && action !== "restore") {
    console.error("Invalid action:", action);
    process.exit(1);
  }

  if (action === "rename") {
    await renameFiles();
    process.exit(0);
  }

  if (action === "restore") {
    await restoreFiles();
    process.exit(0);
  }
}
