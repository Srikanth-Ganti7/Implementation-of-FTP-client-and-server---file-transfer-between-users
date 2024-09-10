import socket
import threading
import os
from queue import Queue, Empty

input_queue = Queue()
output_queue = Queue()

def send_file(sock, filename, output_q):
    if not os.path.exists(filename):
        output_q.put("System: File does not exist.")
        return
    if os.path.getsize(filename) == 0:
        output_q.put("System: File is empty.")
        return

    try:
        file_size = os.path.getsize(filename)
        sock.sendall(str(file_size).encode())
        with open(filename, 'rb') as file:
            bytes_sent = 0
            while bytes_sent < file_size:
                chunk = file.read(1024)
                if not chunk:
                    break
                sock.sendall(chunk)
                bytes_sent += len(chunk)

            if bytes_sent == file_size:
                output_q.put(f"System: File transfer completed successfully for {filename}.")
            else:
                output_q.put(f"System: File transfer error for {filename}: sent {bytes_sent} out of {file_size} bytes.")
    except Exception as e:
        output_q.put(f"System: An error occurred while sending file {filename}: {e}")

def receive_file(sock, filename, output_q):
    try:
        data = sock.recv(1024).decode()
        expected_size = int(data)
    except ValueError:
        output_q.put("System: Received data is not a valid integer for the file size.")
        return
    except Exception as e:
        output_q.put(f"System: An error occurred while receiving file size: {e}")
        return

    received_data = b''
    new_filename = "new_" + filename

    with open(new_filename, 'wb') as file:
        while len(received_data) < expected_size:
            try:
                chunk = sock.recv(1024)
                if not chunk:
                    break
                received_data += chunk
                file.write(chunk)
            except Exception as e:
                output_q.put(f"System: An error occurred while receiving data: {e}")
                break

    if len(received_data) == expected_size:
        output_q.put(f"System: File {new_filename} received successfully.")
    else:
        output_q.put(f"System: File reception error: received {len(received_data)} out of {expected_size} bytes.")

def input_handler(input_q, user_name):
    while True:
        try:
            inp = input()
            if inp:
                input_q.put(f"{user_name}: {inp}")
        except EOFError:
            break

def output_handler(output_q, user_name):
    while True:
        message = output_q.get()
        if message.startswith("System:"):
            # System messages could be displayed with a different formatting
            print(message)  # Modify this print as needed to change the display of system messages
        else:
            print(message)  # Chat messages are printed normally

def handle_send(sock, input_q, output_q, user_name):
    try:
        while True:
            try:
                message = input_q.get(timeout=1)
                if message.startswith(f"{user_name}: transfer "):
                    filename = message.split(" ", 2)[2]
                    sock.sendall(f"transfer {filename}".encode())
                    send_file(sock, filename, output_q)
                else:
                    sock.sendall(message.encode())
                if message == f"{user_name}: exit":
                    output_q.put(f"{user_name} has left the chat.")
                    break
            except Empty:
                continue
    finally:
        sock.close()

def handle_receive(sock, output_q):
    try:
        while True:
            data = sock.recv(1024)
            if data:
                decoded_data = data.decode()
                if decoded_data.startswith("transfer "):
                    filename = decoded_data.split(" ", 1)[1]
                    receive_file(sock, filename, output_q)
                else:
                    output_q.put(decoded_data)
            else:
                output_q.put("System: Connection closed by the remote host.")
                break
    except UnicodeDecodeError:
        output_q.put("System: Received data could not be decoded properly.")
    except Exception as e:
        output_q.put(f"System: An unexpected error occurred while receiving data: {e}")
    finally:
        sock.close()

def server(my_port, output_q):
    host = '0.0.0.0'
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, my_port))
        s.listen()
        output_q.put(f"System: Server listening on port {my_port}")
        while True:
            try:
                conn, addr = s.accept()
                output_q.put(f"System: Connected by {addr}")
                threading.Thread(target=handle_receive, args=(conn, output_q), daemon=True).start()
            except socket.error as e:
                output_q.put(f"System: Error accepting connections: {e}")

def connect_to_other(input_q, output_q, user_name):
    their_ip = 'localhost'
    their_port = int(input(f"{user_name}, enter the port number of the other user: "))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((their_ip, their_port))
            output_q.put(f"System: Connected to {their_ip} on port {their_port}")
            handle_send(s, input_q, output_q, user_name)
        except socket.error as e:
            output_q.put(f"System: Connection error: {e.strerror}. Please check the IP address and try again.")
        except Exception as e:
            output_q.put(f"System: An unexpected error occurred: {e}")

def main():
    user_name = input("Enter your name: ")
    my_port = int(input(f"{user_name}, enter your listening port: "))
    threading.Thread(target=server, args=(my_port, output_queue), daemon=True).start()

    output_thread = threading.Thread(target=output_handler, args=(output_queue, user_name), daemon=True)
    output_thread.start()

    input_thread = threading.Thread(target=input_handler, args=(input_queue, user_name), daemon=True)
    input_thread.start()

    connect_to_other(input_queue, output_queue, user_name)

if __name__ == "__main__":
    main()
