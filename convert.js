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
 * 指定フォルダ内のすべてのPNGファイルをGoogleドキュメントに変換
 */
const convertPngToGoogleDocs = () => {
  const folderId = getFolderId();
  const folder = DriveApp.getFolderById(folderId);
  const pngFiles = folder.getFilesByType(MimeType.PNG);

  while (pngFiles.hasNext()) {
    const file = pngFiles.next();
    const fileName = file.getName().replace(/\.png$/i, "");

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
  }
};
