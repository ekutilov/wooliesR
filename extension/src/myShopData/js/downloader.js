var   upload_url = 'https://myshopdash.appspot.com/upload/',
      dash_url = 'https://myshopdash.appspot.com/dashapp/',
      privacy_url = '##',
      filename = "woolies_ereceipts.json"

// interface injections

const popup_css = `
#popup-downloader-container {
  display: none;
  background: rgba(0, 0, 0, 0.6);
  position: fixed;
  top: 0; bottom: 0; left: 0; right: 0;
  opacity:0; transition: opacity 1s;
  z-index: 99999998;
  color: #606c76;
}

#popup-downloader-container .popup-downloader {
  width: 700px; height: 450px;
  border: 1px solid;
  background: white;
  position: fixed;
  left: calc(50% - 350px); top: calc(50% - 225px);
  z-index: 99999999;
  color: #606c76;
  font-family: 'Helvetica Neue', 'Roboto',  'Helvetica', 'Arial', sans-serif;
  font-size: 12pt;
  font-weight: 300;
  letter-spacing: 0.2pt;
  line-height: 1.2;
}

#popup-downloader-container .popup-downloader #xicon {
  font-size: 20pt;
  cursor: pointer;
  position: absolute;
  right: 10px; top: 5px;
}

#popup-downloader-container .container {
  margin: 0 0;
  max-width: 700px;
  padding: 0px 20px;
  position: relative;
  width: 100%;
  top: 50%; transform: translateY(-50%);
}

#popup-downloader-container .container .row {
  display: flex;
  flex-wrap: nowrap;
  flex-direction: row;
  padding: 0px;
  width: 100%;
}

#popup-downloader-container .container .row.card {
  padding:10px; margin: 10px 0;
  border: 1px solid; border-color: #BBB; border-radius: 5px;
}

#popup-downloader-container .row .column {
  display: block; flex: 1 1 auto;
  max-width: 100%; margin: 0 5px;
}

#popup-downloader-container .row:after {
  content: "";
  display: table;
  clear: both;
}

#popup-downloader-container button {
  border: 1px solid #9b4dca; border-radius: 5px;
  background-color: #9b4dca; color: #fff;
  cursor: pointer;
  display: inline-block;
  font-size: 12pt; font-weight: 700;
  height: 40px;
  letter-spacing: 1pt; line-height: 12pt;
  text-align: center; text-decoration: none; white-space: nowrap;
  margin: 5px; padding: 5px 10px;
}

#popup-downloader-container button:hover {
    background-color: #606c76; border-color: #606c76; color: #fff;
    outline: 0;
  }

.center { text-align: center; }

#popup-downloader-container p {
    font-size: 12pt; font-weight: 300;
    margin: 3pt 0;
    line-height:1.2;
    font-family: 'Helvetica Neue', 'Roboto', 'Helvetica', 'Arial', sans-serif;
  }

a {
  font-size: 12pt !important;
  font-weight: 300;
  color: #9b4dca;
  text-decoration: none;
}

a:focus, a:hover {
  color: #606c76;
}

#popup-downloader-container p.small {
  font-size: 10pt;
}

#popup-downloader-container h1,
#popup-downloader-container h3 {
    font-family: 'Helvetica Neue', 'Roboto', 'Helvetica', 'Arial', sans-serif;
    font-weight: 300; letter-spacing: -0.5pt;
    margin-bottom: 12pt; margin-top: 18pt;
    color: #ff6600;
    text-align: center;
    line-height: 1.2;
  }

#popup-downloader-container h1 { font-size: 36pt; }

#popup-downloader-container h3 { font-size: 24pt; }

#popup-downloader-container h3.danger { color: #FF0000; }

@keyframes spinner { to {transform: rotate(360deg);} }

#popup-downloader-container .spinner:before {
    content: '';
    box-sizing: border-box;
    position: absolute;
    top: 50%; left: 50%;
    width: 30px; height: 30px;
    margin-top: -15px; margin-left: -15px;
    border-radius: 50%; border-top: 2px solid #fd7e14; border-right: 2px solid transparent;
    animation: spinner .6s linear infinite;
  }

#popup-downloader-container .check {
    display: block;
    transform: rotate(45deg);
    height: 40px; width: 20px;
    border-bottom: 11px solid #78b13f; border-right: 11px solid #78b13f;
    position: relative; left: 50%;
  }
`,
popup_html_step1 = `
    <div class="popup-downloader">
    <span id='xicon'>&times;</span>
      <div class='container'>
        <div class='row'>
          <div class='column'>
            <h3>Downloading in progress</h3>
          </div>
        </div>
        <div class='row'>
          <div class='column center'>
            <p>We are retrieving your data from Woolworths Servers.
            It might take some time.</p>
          </div>
        </div>
        <div class='row'>
          <div class='column center'>
            <div style='position: relative; width: 100%; height: 30px; margin:15px 0;'>
              <div class='spinner' >
              </div>
            </div>
          </div>
        </div>
        <div class='row'>
          <div class='column center'>
            <p>
              <span id='dl-status-1'>
                Launching the download...
              </span>
            </p>
            <p>
              <span id='dl-status-2'>
                &nbsp;
              </span>
            </p>
            <p>
              <span id='dl-status-3'>
                &nbsp;
              </span>
            </p>
          </div>
        </div>
        <div class='row'>
          <div class='column center'>
            <button id='reloadButton'>Cancel</button>
          </div>
        </div>
      </div>
    </div>
`,
popup_html_step2 = `
  <div class="popup-downloader">
  <span id='xicon'>&times;</span>
    <div class='container'>
      <div class='row'>
        <div class='column'>
          <h3>Download complete</h3>
        </div>
      </div>
      <div class='row'>
        <div class='column'>
          <div class='check'></div>
        </div>
      </div>
      <div class='row'>
        <div class='column center'>
          <p>Now you can download your data or review it in the viewer</p>
        </div>
      </div>
      <div class='row card'>
        <div class='column '>
          <p>Download data as a raw json file onto your local drive.
          This file will contain all downloaded data, but
          it will need to be decoded before viewing.</p>
        </div>
        <div class='column '>
          <button id='msdDownloadButton'>Download json</button>
        </div>
      </div>
      <div class='row card'>
        <div  class='column'>
          <p>
            You can open the downloaded
            data in a special viewer on myshopdash.appspot.com. Your data will be
            decoded and visualised, and you will be able to download decoded data
            from the site as Excel files.
          </p>
          <p class='small'>
            You will be redirected to external website.
            Your data will be transferred and temporarily stored there:
            see <a href='` + privacy_url + `'>Privace policy</a>
          </p>
        </div>
        <div class='column'>
          <button id='msdViewerButton'>Open in viewer</button>
        </div>
      </div>
    </div>
  </div>
`,
popup_html_upload = `
  <div class="popup-downloader">
  <span id='xicon'>&times;</span>
    <div class='container'>
      <div class='row'>
        <div class='column'>
          <h3>
            Uploading data
          </h3>
        </div>
      </div>
      <div class='row'>
        <div class='column'>
          <div style='position: relative; width: 100%; height: 30px; margin:15px 0;'>
            <div class='spinner' >
            </div>
    		  </div>
        </div>
      </div>
      <div class='row'>
        <div class='column center'>
          <button id='reloadButton'>Cancel</button>
        </div>
      </div>
    </div>
  </div>
`,
popup_html_upload_complete = `
<div class="popup-downloader">
<span id='xicon'>&times;</span>
  <div class='container'>
    <div class='row'>
      <div class='column'>
        <h3>
          Upload complete
        </h3>
      </div>
    </div>
    <div class='row'>
      <div class='column center'>
            <p>&nbsp;</p>
            <p>You will be redirected to my Shopping Dashboard now,
            click the link if it does not happen automatically</p>
            <p><a href='https://myshopdash.appspot.com/dashapp'>myShopDash</a></p>
      </div>
    </div>
  </div>
</div>`,
popup_html_upload_error = `
<div class="popup-downloader">
<span id='xicon'>&times;</span>
  <div class='container'>
    <div class='row'>
      <div class='column'>
        <h3 class='danger'>
          Upload error
        </h3>
      </div>
    </div>
    <div class='row'>
      <div class='column center'>
            <p>&nbsp;</p>
            <p>An error occured during uploading.</p>
            <p>(Response code: <span class='error-code'></span>)</p>
            <p>You can try again. If the fault persists, please contact me
            on github or email.</p>
      </div>
    </div>
    <div class='row'>
      <div class='column center'>
        <button id='reloadButton'>Try again</button>
      </div>
    </div>
  </div>
</div>`,
popup_html_download_error = `
<div class="popup-downloader">
<span id='xicon'>&times;</span>
  <div class='container'>
    <div class='row'>
      <div class='column'>
        <h3 class='danger'>
          Download error
        </h3>
      </div>
    </div>
    <div class='row'>
      <div class='column center'>
            <p>&nbsp;</p>
            <p>An error occured during downloading your data.</p>
            <p>(Response code: <span class='error-code'></span>)</p>
            <p>You can try again: reload page, try to log
            out and log in, update the extension. </p>
            <p>If the fault persists, please contact me
            on github or email.</p>
      </div>
    </div>
    <div class='row'>
      <div class='column center'>
        <button id='reloadButton'>Reload page</button>
      </div>
    </div>
  </div>
</div>`

function popup_interface(html) {
  var dpopupContainer = document.getElementById('popup-downloader-container')
  dpopupContainer.innerHTML = html
  dpopupContainer.style.display = 'block'
  dpopupContainer.style.opacity = 1
  document.getElementById("xicon").addEventListener('click',
      () => {
        document.body.removeChild(document.getElementById("popup-downloader-container"));
        window.location.reload()
      })
  if (document.getElementById("reloadButton")) {
      document.getElementById("reloadButton").addEventListener('click',
          () => {
            document.body.removeChild(document.getElementById("popup-downloader-container"));
            window.location.reload()
          })
  }
  return dpopupContainer
}

function getClientId() {
  var temp_scripts = document.getElementsByTagName("script")
  var searchText = "var defaultClientId ="
  var rexp = RegExp("var defaultClientId = \'(.{32})\'")
  var found;

  for (var i = 0; i < temp_scripts.length; i++) {
    if (temp_scripts[i].text.includes(searchText)) {
      client_id = rexp.exec(temp_scripts[i].text)[1];
      break;
    }
  }
  return client_id
}

async function downloader() {

  const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
        delay_time = 50,
        transactions_list_url = "https://api.woolworthsrewards.com.au/wx/v1/rewards/member/ereceipts/transactions/list",
        details_list_url = "https://api.woolworthsrewards.com.au/wx/v1/rewards/member/ereceipts/transactions/details"

  var dpopupContainer = popup_interface(popup_html_step1),
      status_line_1 = document.getElementById('dl-status-1'),
      status_line_2 = document.getElementById('dl-status-2'),
      status_line_3 = document.getElementById('dl-status-3');

  // downloader itself starts here

  const access_token = JSON.parse(sessionStorage.authStatusData).access_token,
        client_id = getClientId()

  var file = [],
      i = 1,
      download_success = true

  status_line_1.innerHTML = 'Downloading...'

  do {
    response = $.ajax({
      url: transactions_list_url + "?page=" + i,
      beforeSend: (xhr) => {
                            xhr.setRequestHeader('client_id' , client_id);
                            xhr.setRequestHeader('authorization', "Bearer " + access_token);
                           },
      method : 'GET',
      contentType : 'json',
      async : false})

      if (response.status != 200) {download_success = false; downloadErrorCode = response.status; break}

      file = file.concat(response.responseJSON.data);
      i++;

      status_line_2.innerHTML = 'Downloading list of transactions: page ' + i + '...'
      await delay(delay_time);

    } while (response.responseJSON.data.length > 0);

  status_line_2.innerHTML = 'List of transactions: done'

  receiptsList = file.map(x => x.receiptKey)
  d_len = receiptsList.length

  for (let j = 0; j < d_len; j++) { //d_len instead of 10 (debuggin)
    if (receiptsList[j]!==''){
      response = $.ajax({
          url: details_list_url,
          beforeSend: (xhr) => {
            xhr.setRequestHeader('client_id' , client_id);
            xhr.setRequestHeader('authorization' , "Bearer " + access_token);
            xhr.setRequestHeader('content-type', 'application/json;charset=UTF-8');
          },
          method : 'POST',
          contentType : 'json',
          async : false,
          data : '{"receiptKey" : "' + receiptsList[j] + '" }'
      })

      if (response.status != 200) {
        download_success = false;
        downloadErrorCode = response.status;
        break;
      }

      file[j].ereceipt = response.responseJSON.data
    }
    status_line_3.innerHTML ='Downloading eReceipts: ' + (j+1) + ' out of ' + d_len;
    await delay(delay_time);
  }

  status_line_3.innerHTML = 'eReceipts: done'

  if (download_success) return JSON.stringify(file)
}

function download_file(filename, text) {
      const element = document.createElement('a');
      element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
      element.setAttribute('download', filename);

      element.style.display = 'none';
      document.body.appendChild(element);

      element.click();

      document.body.removeChild(element);
}

function upload_file(url, text) {
  popup_interface(popup_html_upload)

  var element = document.createElement('form');
  element.setAttribute('action', url);
  element.setAttribute('method', 'post');
  element.setAttribute('id', 'jsonform')
  element.innerHTML = '<textarea id="jsondata" name="content">' + text + '</textarea>'
  element.style.display = 'none'
  document.body.appendChild(element);
  element.submit()
  document.body.removeChild(element);
}

function completeHandler(event) {
  console.log('Server response text: ' + event.target.responseText)

  if (event.target.status == 200) {
    popup_interface(popup_html_upload_complete)
    window.location.replace(dash_url);
  } else errorHandler(event)
}

function errorHandler(event) {
  popup_interface(popup_html_upload_error)

  var error_report ='';
  if (event.message) error_report = error_report + 'Msg: ' + event.message + '; '
  if (event.target.status) error_report = error_report + 'Code: ' + event.target.status
  document.getElementsByClassName('error-code')[0].innerHTML = error_report

  console.log('Event message: '+ event.message)
  console.log('Event status: '+ event.target.status)
  console.log('Server response text: ' + event.target.responseText)
}

function abortHandler(event) {
  window.location.reload()
}

async function main() {
  var downloadErrorCode;

  // setting up the interface elements:
  // css
  const popup_downloader_css = document.createElement('style');
  popup_downloader_css.innerHTML = popup_css;
  document.head.appendChild(popup_downloader_css);

  // pop-up initialisation
  var dpopupContainer = document.createElement('div');
  dpopupContainer.setAttribute('id', "popup-downloader-container")
  document.body.appendChild(dpopupContainer);

  // start download logic
  var wwData = await downloader()

  if (typeof wwData !== 'undefined') {
    popup_interface(popup_html_step2)
    document.getElementById("msdDownloadButton").addEventListener('click', () => download_file(filename, wwData))
    document.getElementById("msdViewerButton").addEventListener('click', () => upload_file(upload_url, wwData))
  } else {
    popup_interface(popup_html_download_error)
    const err_code = document.getElementById('error-code');
    err_code.innerHTML = downloadErrorCode;
  }
}

main()
