import socket
import threading

serverClients = list()  # Список клиентов


def send_mess(message, cl_socket=None):
    # Отправляем сообщение всем, кроме автора
    for clientSocket, name in serverClients:
        if clientSocket != cl_socket:
            try:
                clientSocket.send(message.encode('utf-8'))
            except Exception as e:
                print("Server Exception: ", e)
                remove_client(clientSocket)  # Удаляем клиента


def remove_client(client_socket):
    for i, (sock, name) in enumerate(serverClients):
        if sock == client_socket:
            serverClients.pop(i)
            try:
                sock.close()
            except Exception as e:
                print("Server Exception: ", e)
                pass

            print(f"Client {name} removed")
            send_mess(f'Client {name} gone')
            break


def meet_client(cl_socket, address):
    try:
        name = cl_socket.recv(1024).decode('utf-8')  # Получаем имя клиента для приветствия
        print(f"Client {name} added from address: {address}")

        serverClients.append((cl_socket, name))  # Запоминаем клиента
        send_mess(f'Client {name} added in chat.',
                  cl_socket)  # Отправляем всем сообщение о подключении клиента

        # Читаем сообщения
        while True:
            try:

                message = cl_socket.recv(1024).decode('utf-8')

                if not message:
                    break

                ready_message = f'{name}: {message}'
                send_mess(ready_message, cl_socket)

            except Exception as e:
                print("Server Exception: ", e)
                break

    except Exception as e:
        print("Server Exception: ", e)
        cl_socket.sendto(("Can't add you in chat. Exception: " + str(e)).encode('utf-8'))


serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Создаем сокет localhost 9090
serverSocket.bind(('', 9090))
serverSocket.listen(5)
serverSocket.settimeout(180)
print("Server is ready for work")

try:
    while True:
        clSocket, addr = serverSocket.accept()  # Принимаем подключение
        clientThread = threading.Thread(target=meet_client, args=(clSocket, addr),
                                        daemon=True)  # Создаем поток для подключенного клиента
        clientThread.start()

except Exception as e:
    print("Server Exception: ", e)

finally:
    for clSocket, name in serverClients:
        try:
            clSocket.close()
        except:
            pass
    serverSocket.close()
    print("Server stopped")
