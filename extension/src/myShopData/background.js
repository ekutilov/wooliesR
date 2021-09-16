chrome.runtime.onInstalled.addListener(() => {
    chrome.action.setPopup({"popup": "def_popup.html"});
})

chrome.webNavigation.onCommitted.addListener(
  (tab) => {
    chrome.scripting.executeScript(
    {
      target: { tabId: tab.tabId },
      func: () => {
                  return JSON.parse(sessionStorage.authStatusData)
                  }
      },
     (result) => {
        if (result[0].result.reason == "AUTHENTICATED") {
            chrome.action.setPopup({ popup: "download_popup.html", tabId: tab.tabId });
            chrome.action.setBadgeBackgroundColor({color: "#F00", tabId: tab.tabId});
            chrome.action.setBadgeText({text: " ▼ ", tabId: tab.tabId})
        } else {
            chrome.action.setPopup({ popup: "def_popup.html", tabId: tab.tabId});
            chrome.action.setBadgeText({text: "", tabId: tab.tabId})
        }
      }
    )
  },
  { url: [{urlContains: 'woolworthsrewards.com.au/index.html'}] }
)
