token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkZXZpY2UiOjEsImRldmljZV9sb2NhdGlvbiI6Im1lbnNhIn0.XNGDn43OxLV4MxMlZV3KkssHmDG-jUxTqi7UYXQ-07s'
serverUrl='192.168.97.124:8000/api/submit_result/'
result=$({ echo -e 'scan on'; sleep 10; echo -e 'devices\nquit'; } | bluetoothctl | grep -E '^Device' | sort | uniq | parallel 'echo {} | sha256sum'| egrep -wo '[a-f0-9]+' | echo "$(paste -sd, - | sed 's/,/","/g')")
curl -s --header "Content-Type: application/json" --request POST --data '{"token":"'$token'","results":["'$result'"]}' $serverUrl > /dev/null
printf "$(date) - send result:$deviceCount with token:$token to $serverUrl\n"