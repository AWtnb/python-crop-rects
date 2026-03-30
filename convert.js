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
      });
  }

  MailApp.sendEmail(recipient, subject, body);
  console.log(`完了通知メールを送信: ${recipient}`);
};

/**
 * 指定フォルダ内のすべてのPNGファイルをGoogleドキュメントに変換
 */
const convertPngToGoogleDocs = () => {
  const folderId = getFolderId();
  const folder = DriveApp.getFolderById(folderId);
  const pngFiles = folder.getFilesByType(MimeType.PNG);

  const results = [];

  while (pngFiles.hasNext()) {
    const file = pngFiles.next();
    const fileName = file.getName().replace(/\.png$/i, "");

    try {
      // OCRを実行してGoogleドキュメントに変換
      const resource = {
        title: fileName,
        mimeType: MimeType.GOOGLE_DOCS,
        parents: [{ id: folderId }],
      };

      const options = {
        ocr: true,
        ocrLanguage: "ja", // 日本語の場合。英語なら'en'
      };

      const docFile = Drive.Files.copy(resource, file.getId(), options);

      console.log(`OCR変換完了: ${fileName} (ID: ${docFile.id})`);
      results.push({ success: true, fileName, docId: docFile.id });
    } catch (error) {
      console.error(`OCR変換失敗: ${fileName} - ${error.message}`);
      results.push({ success: false, fileName, error: error.message });
    }
  }

  sendCompletionEmail(results, folder.getName());
};
