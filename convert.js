const FOLDER_ID = "";

/**
 * 指定フォルダ内のすべてのPNGファイルをGoogleドキュメントに変換
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

    // Googleドキュメントを作成
    const doc = DocumentApp.create(fileName);
    const body = doc.getBody();

    // 画像を挿入
    const blob = file.getBlob();
    body.appendImage(blob);

    // 作成したドキュメントを同じフォルダに移動
    const docFile = DriveApp.getFileById(doc.getId());
    folder.addFile(docFile);
    DriveApp.getRootFolder().removeFile(docFile);

    Logger.log(`変換完了: ${fileName}`);
  }
};
