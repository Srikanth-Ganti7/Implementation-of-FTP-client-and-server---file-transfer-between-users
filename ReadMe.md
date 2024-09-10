
# CNT 5106 - Computer Networks - Project 3

## Implementation of FTP client and server with multiple threads

In this project, the application will manage two primary threads: a main thread that handles incoming connections and reads messages, and a writing thread that sends messages and files to a specified port. The program's functionality includes establishing connections, exchanging messages, and transferring files between users.



## Authors

**Name**: Balasai Srikanth Ganti

**UFID** : 5251-6075

**Name**: Nikhil Sai Siddam Shetty

**UFID** : 2086-1319


## Running the First User

To run the First user, execute the following command in cmd prompt:
- `python Server.py `

- Enter the name of the first user: `<name>`
- Enter the listening port of the first user: `<First port>`

## Running the Second User

To run the second user, execute the following command in cmd promt :
- `python Server.py`

- Enter the name of the Second user: `<name>`
- Enter the listening port of the Second user: `<First port>`

### Commands

After the ports have been assigned:

- Enter the port of the second user in the first user 
- Enter the port of the first user in the second user


The First user listens for client connections and handles each client session in a separate thread. It supports the following commands:

- `transfer <filename>`: Transfers a file from one user to another.
- `exit` : This is used to exit both the users


### Notes
- The server creates a new file with a new prefix for Transfer files to avoid overwriting existing files.
- Both the server and client use a chunk size of 1024 bytes for file transfer.






