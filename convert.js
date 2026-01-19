const FOLDER_ID = "";

/**
 * 指定フォルダ内のすべてのPNGファイルをGoogleドキュメントに変換
 * 「サービス」から Drive API を有効化しておくこと。
 */
const convertPngToGoogleDocs = () => {
  if (FOLDER_ID == "") {
    console.log("folder id not specified.");
    return;
  }
  const folder = DriveApp.getFolderById(FOLDER_ID);
  const pngFiles = folder.getFilesByType(MimeType.PNG);

  while (pngFiles.hasNext()) {
    const file = pngFiles.next();
    const fileName = file.getName().replace(/\.png$/i, "");

    // OCRを実行してGoogleドキュメントに変換
    const resource = {
      title: fileName,
      mimeType: MimeType.GOOGLE_DOCS,
      parents: [{ id: FOLDER_ID }],
    };

    const options = {
      ocr: true,
      ocrLanguage: "ja", // 日本語の場合。英語なら'en'
    };

    const docFile = Drive.Files.copy(resource, file.getId(), options);

    console.log(`OCR変換完了: ${fileName} (ID: ${docFile.id})`);
  }
};
