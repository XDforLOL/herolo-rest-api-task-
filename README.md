"# herolo-rest-api-task-"
Has basic Authentication
Username: <username>
Password: <password>

* Write a message

<url>/api/send_message
Parameters {
    subject=<Message_Subject>
    body=<Message_Body>
    recipient=<User_id>
}

<url>/api/read_message/'

<url>/api/delete_message/<int:msg_id>'

<url>/api/all_msg_by_usrid/<int:usr_id>'
