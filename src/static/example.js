function custom_doc_processor(data) {
 baseurl = window.location.protocol + "//" + window.location.host + $("#home").attr('href');

 data.emails.forEach(function(val,idx,self) {self[idx]='mailto:' + val + "|" + val;});
 data.hosts.forEach(function(val,idx,self) {self[idx]='https://' + val + "|" + val;});
 try {
   data.user = baseurl + '?output=table&query=%2A&filter=internal%3Auser%3D' + data.user + "|" + data.user;
 } catch {}

 return data;
}
