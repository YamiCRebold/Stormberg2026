function doGet() {
  return HtmlService.createHtmlOutputFromFile('Index')
    .setTitle('Tablero Stormberg + Granite')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.DEFAULT);
}
