var file = []; var file2 = []; var i = 0; 
console.log('Downloading list of transactions...');

do {
response = $.ajax({ url: "https://api.woolworthsrewards.com.au/wx/v1/rewards/member/ereceipts/transactions/list?page=" + ++i, 
  beforeSend: function(xhr){xhr.setRequestHeader('client_id' , defaultClientId);
                            xhr.setRequestHeader('authorization', "Bearer " + JSON.parse(sessionStorage.authStatusData).access_token);},
  method : 'GET', contentType : 'json', async : false}).responseJSON;
file = file.concat(response.data);
console.log('Page ' + i + '..');
} while (response.data.length > 0);

receiptsList = file.map(function(x) { return x.receiptKey ; });
console.log('Downloading eReceipts');
for (let j = 0; j < receiptsList.length; j++) {
if (receiptsList[j]!==''){
response2 = $.ajax({ url: "https://api.woolworthsrewards.com.au/wx/v1/rewards/member/ereceipts/transactions/details", 
  beforeSend: function(xhr){xhr.setRequestHeader('client_id' , defaultClientId);
                            xhr.setRequestHeader('authorization' , "Bearer " + JSON.parse(sessionStorage.authStatusData).access_token);
                            xhr.setRequestHeader('content-type', 'application/json;charset=UTF-8');},
  method : 'POST',
  contentType : 'json',
  async : false,
  data : '{"receiptKey" : "' + receiptsList[j] + '" }'
}).responseJSON;
response2.data.receiptDetails.key = receiptsList[j];
file2 = file2.concat(response2.data);
}
console.log(j + '.. ');
do {;} while (Date.now() % 100 > 20);
}
document.head.innerHTML = '';
document.body.innerHTML = '<br><br>This is your list of transactions (in json): <br>(copy-paste and save to a plain text file)<br><textarea id="List" rows="30" cols="100">' + JSON.stringify(file) + '</textarea><br><br><br>This is your eReceipts (in json): <br>(copy-paste and save into another plain text file for further use)<br><textarea id="eReceipts" rows="30" cols="100">' + JSON.stringify(file2) + '</textarea>';



