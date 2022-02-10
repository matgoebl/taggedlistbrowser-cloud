function custom_doc_processor(data) {
 data.emails.forEach(function(val,idx,self) {self[idx]='mailto:' + val;});
 data.hosts.forEach(function(val,idx,self) {self[idx]='https://' + val;});
 return data;
}
