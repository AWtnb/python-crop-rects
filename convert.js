/**
 * このスクリプトが置かれているフォルダのIDを取得
 */
const getFolderId = () => {
  const sid = ScriptApp.getScriptId();
  const file = DriveApp.getFileById(sid);
  const folder = file.getParents().next();
  return folder.getId();
};

/**
 * 処理完了メールを送信
 * @param {Array} results - 処理結果の配列
 * @param {string} folderName - 処理対象フォルダ名
 */
const sendCompletionEmail = (results, folderName) => {
  const props = PropertiesService.getScriptProperties();
  const recipient = props.getProperty("NOTIFICATION_EMAIL");

  if (!recipient) {
    console.warn(
      "メール送信先が設定されていません（スクリプトプロパティ: NOTIFICATION_EMAIL）",
    );
    return;
  }

  const successCount = results.filter((r) => r.success).length;
  const failureCount = results.filter((r) => !r.success).length;

  const subject = `[GAS] PNG→Googleドキュメント変換完了 (${successCount}/${results.length}件成功)`;

  let body = `PNG画像のOCR変換処理が完了しました。\n\n`;
  body += `対象フォルダ: ${folderName}\n`;
  body += `成功: ${successCount}件\n`;
  body += `失敗: ${failureCount}件\n`;
  body += `合計: ${results.length}件\n\n`;

  if (0 < failureCount) {
    body += `--- 失敗したファイル ---\n`;
    results
      .filter((r) => !r.success)
      .forEach((r) => {
        body += `- ${r.fileName}\n`;
        body += `  エラー: ${r.error}\n`;
        if (1 < r.retryCount) {
          body += `  リトライ回数: ${r.retryCount}回\n`;
        }
      });
  }

  MailApp.sendEmail(recipient, subject, body);
  console.log(`完了通知メールを送信: ${recipient}`);
};

/**
 * OCR変換処理をリトライ付きで実行
 * @param {GoogleAppsScript.Drive.File} file - 変換対象ファイル
 * @param {string} fileName - ファイル名（拡張子なし）
 * @param {string} folderId - 出力先フォルダID
 * @param {number} maxRetries - 最大リトライ回数
 * @returns {Object} 処理結果
 */
const convertWithRetry = (file, fileName, folderId, maxRetries = 3) => {
  let lastError = null;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const resource = {
        title: fileName,
        mimeType: MimeType.GOOGLE_DOCS,
        parents: [{ id: folderId }],
      };

      const options = {
        ocr: true,
        ocrLanguage: "ja",
      };

      const docFile = Drive.Files.copy(resource, file.getId(), options);

      if (1 < attempt) {
        console.log(
          `OCR変換完了: ${fileName} (${attempt}回目の試行で成功, ID: ${docFile.id})`,
        );
      } else {
        console.log(`OCR変換完了: ${fileName} (ID: ${docFile.id})`);
      }

      return {
        success: true,
        fileName,
        docId: docFile.id,
        retryCount: attempt,
      };
    } catch (error) {
      lastError = error;
      console.warn(
        `OCR変換失敗 (試行 ${attempt}/${maxRetries}): ${fileName} - ${error.message}`,
      );

      if (attempt < maxRetries) {
        // リトライ前の待機時間を試行回数に応じて延長（指数バックオフ）
        const waitTime = 5000 * attempt;
        console.log(`${waitTime / 1000}秒待機してリトライします...`);
        Utilities.sleep(waitTime);
      }
    }
  }

  // すべてのリトライが失敗した場合
  console.error(
    `OCR変換失敗（${maxRetries}回リトライ後）: ${fileName} - ${lastError.message}`,
  );
  return {
    success: false,
    fileName,
    error: lastError.message,
    retryCount: maxRetries,
  };
};

/**
 * 指定フォルダ内のすべてのPNGファイルをGoogleドキュメントに変換
 */
const convertPngToGoogleDocs = () => {
  const folderId = getFolderId();
  const folder = DriveApp.getFolderById(folderId);
  const pngFiles = folder.getFilesByType(MimeType.PNG);

  const results = [];
  let processedCount = 0;

  while (pngFiles.hasNext()) {
    const file = pngFiles.next();
    const fileName = file.getName().replace(/\.png$/i, "");

    const result = convertWithRetry(file, fileName, folderId, 3);
    results.push(result);

    if (result.success) {
      processedCount++;

      // 1ファイル処理ごとに1秒待機
      Utilities.sleep(1000);

      // 10ファイルごとにやや長めの待機
      if (processedCount % 10 === 0) {
        console.log(`${processedCount}件処理完了。5秒待機中...`);
        Utilities.sleep(5000);
      }
    }
  }

  sendCompletionEmail(results, folder.getName());
};
