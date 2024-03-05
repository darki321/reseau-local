import socket
import threading
import tkinter as tk
from queue import Queue
import traceback

class Server:
    def __init__(self):
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', 12345))
        self.server_socket.listen(5)

        self.root = tk.Tk()
        self.root.title("Serveur")
        self.root.geometry("300x200")

        self.log_text = tk.Text(self.root)
        self.log_text.pack(expand=True, fill=tk.BOTH)

        self.queue = Queue()
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        self.log_messages()

    def handle_client(self, client_socket, address):
        self.queue.put(f"Nouvelle connexion de {address}")
        try:
            while True:
                message = client_socket.recv(1024).decode()
                if message:
                    self.queue.put(f"Message reçu de {address}: {message}")
                    self.broadcast(message, client_socket)
                else:
                    self.queue.put(f"Connexion fermée par {address}")
                    break
        except Exception as e:
            self.queue.put(f"Erreur {address}: {e}")
            traceback.print_exc()
        finally:
            self.remove_client(client_socket)


    def log_messages(self):
        while not self.queue.empty():
            message = self.queue.get()
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
            self.queue.task_done()
        self.root.after(100, self.log_messages)

    def handle_client(self, client_socket, address):
        self.queue.put(f"Nouvelle connexion de {address}")
        try:
            while True:
                message = client_socket.recv(1024).decode()
                if message:
                    self.queue.put(f"Message reçu de {address}: {message}")
                    self.broadcast(message, client_socket)
                else:
                    self.queue.put(f"Connexion fermée par {address}")
                    break
        except Exception as e:
            self.queue.put(f"Erreur de {address}: {e}")
        finally:
            self.remove_client(client_socket)

    def broadcast(self, message, sender_socket):
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.sendall(message.encode())
                except Exception as e:
                    self.queue.put(f"Erreur du message à {client.getpeername()}: {e}")
                    self.remove_client(client)

    def remove_client(self, client_socket):
        if client_socket in self.clients:
            self.clients.remove(client_socket)
            client_socket.close()

    def receive_messages(self):
        while True:
            client_socket, address = self.server_socket.accept()
            self.clients.append(client_socket)
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
            client_thread.daemon = True
            client_thread.start()

if __name__ == "__main__":
    server = Server()
    server.root.mainloop()
