#### Query specific user
curl -s 'localhost:8080/user/?first=Sheldon&last=Cooper' | jq
#### Query all users
curl -s localhost:8080/all_users | jq
#### Load the user dynamo database
curl -XPOST -s localhost:8080/load_db
