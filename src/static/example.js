function custom_doc_processor(data) {
 data.emails.forEach(function(val,idx,self) {self[idx]='mailto:' + val + "|" + val;});
 data.hosts.forEach(function(val,idx,self) {self[idx]='https://' + val + "|" + val;});
 return data;
}
