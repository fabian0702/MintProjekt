token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkZXZpY2UiOjIsImRldmljZV9sb2NhdGlvbiI6Im1lZGlvIn0.hRWD3GrE1sOiOBLVqxkE3bSEDQfTX6M77Vsr9O5Bj6c'
serverUrl='192.168.97.124:5000/api/submit_result/'
result=$({ echo -e 'power on\nscan on\n'; sleep 10; echo -e 'scan off\nexit'; } | bluetoothctl | grep NEW | sort | uniq | wc -l)
echo 'found '$result' devices'
curl --header "Content-Type: application/json" --request POST --data '{"token":"'$token'","result":"'$result'"}' $serverUrl
echo 'send result:'$result' with token:'$token' to '$serverUrl
