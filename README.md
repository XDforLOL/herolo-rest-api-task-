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
    token=has_token
}

<url>/api/read_message/
    Reads 1 meassge of logged user

<url>/api/delete_message/<msg_id>

<url>/api/all_msg_by_usrid/<usr_id>
    optinal param {
    read=<bool>
    }
