import socket
import tkinter as tk
from threading import Thread
from queue import Queue

class Client:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.root = tk.Tk()
        self.root.title("Client")
        self.root.geometry("300x500")

        self.log_text = tk.Text(self.root)
        self.log_text.pack(expand=True, fill=tk.BOTH)

        self.message_entry = tk.Entry(self.root)
        self.message_entry.pack(expand=True, fill=tk.X)

        self.send_button = tk.Button(self.root, text="Envoyer", command=self.send_message)
        self.send_button.pack()

        self.queue = Queue()
        
        self.connect_to_server()

        self.receive_thread = Thread(target=self.receive_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        #IMPORTANT : mise a jour de l'affichage
        self.root.after(100, self.log_messages)

        self.root.mainloop()

    def log_messages(self):
        while not self.queue.empty():
            message = self.queue.get()
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
            self.queue.task_done()
        self.root.after(100, self.log_messages)

    def connect_to_server(self):
        try:
            self.client_socket.connect(('127.0.0.1', 12345))
            self.log_message("Connecté au serveur.")
        except Exception as e:
            self.log_message(f"Impossible de se connecter au serveur: {e}")

    def log_message(self, message):
        self.queue.put(message)

    def send_message(self):
        message = self.message_entry.get()
        try:
            self.client_socket.sendall(message.encode())
            self.log_message(f"Vous: {message}")
            self.message_entry.delete(0, tk.END)
        except Exception as e:
            self.log_message(f"Erreur lors de l'envoi du message: {e}")

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                if message:
                    self.log_message(f"interlocuteur: {message}")
            except Exception as e:
                self.log_message(f"Erreur lors de la réception du message: {e}")
                break

if __name__ == "__main__":
    client = Client()
