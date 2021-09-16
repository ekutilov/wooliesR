downloadButton.addEventListener("click",
  async () => {
    let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    await chrome.scripting.executeScript(
    {
      target: {tabId: tab.id},
      files: ['/js/jquery.min.js']
    },
    () => {
      chrome.scripting.executeScript(
      {
        target: {tabId: tab.id},
        files: ['/js/downloader.js']
      },
      () => window.close()
      )
    }
    )
  }
)
