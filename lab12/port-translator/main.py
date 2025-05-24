import socket
import threading
import json
import time
import os
import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime


class PortForwarder:
    def __init__(self, root):
        self.root = root
        self.root.title("Port Forwarder")

        self.rules = {}
        self.active_connections = {}
        self.config_file = "config.json"
        self.running = False

        self.setup_ui()
        self.load_config()
        self.start_monitoring_config()

    def setup_ui(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.control_frame = ttk.LabelFrame(self.main_frame, text="Control")
        self.control_frame.pack(fill=tk.X, pady=5)

        self.start_btn = ttk.Button(self.control_frame, text="Start", command=self.start_forwarding)
        self.start_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.stop_btn = ttk.Button(self.control_frame, text="Stop", command=self.stop_forwarding, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.reload_btn = ttk.Button(self.control_frame, text="Reload Config", command=self.reload_config)
        self.reload_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.rules_frame = ttk.LabelFrame(self.main_frame, text="Active Rules")
        self.rules_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.rules_tree = ttk.Treeview(self.rules_frame, columns=("listen", "forward", "connections"), show="headings")
        self.rules_tree.heading("listen", text="Listen Port")
        self.rules_tree.heading("forward", text="Forward To")
        self.rules_tree.heading("connections", text="Active Connections")
        self.rules_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.log_frame = ttk.LabelFrame(self.main_frame, text="Log")
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_area = scrolledtext.ScrolledText(self.log_frame, width=80, height=10)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)

    def load_config(self):
        try:
            with open(self.config_file, "r") as f:
                new_rules = json.load(f)

            for rule in new_rules:
                listen_port = rule["listen"]
                forward_to = f"{rule['forward_ip']}:{rule['forward_port']}"

                if listen_port not in self.rules:
                    self.rules[listen_port] = {
                        "forward_ip": rule["forward_ip"],
                        "forward_port": rule["forward_port"],
                        "socket": None,
                        "thread": None,
                    }
                    self.rules_tree.insert("", tk.END, values=(listen_port, forward_to, 0))

            self.log_message("Configuration loaded successfully")
            self.update_rules_tree()
        except Exception as e:
            self.log_message(f"Error loading config: {str(e)}")

    def reload_config(self):
        if self.running:
            self.log_message("Reloading configuration...")
            self.load_config()
            self.restart_listeners()
        else:
            self.load_config()

    def update_rules_tree(self):
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)

        for listen_port, rule in self.rules.items():
            forward_to = f"{rule['forward_ip']}:{rule['forward_port']}"
            conn_count = len(self.active_connections.get(listen_port, {}))
            self.rules_tree.insert("", tk.END, values=(listen_port, forward_to, conn_count))

    def start_monitoring_config(self):
        self.last_mtime = os.path.getmtime(self.config_file)
        threading.Thread(target=self.monitor_config_changes, daemon=True).start()

    def monitor_config_changes(self):
        while True:
            try:
                current_mtime = os.path.getmtime(self.config_file)
                if current_mtime != self.last_mtime:
                    self.last_mtime = current_mtime
                    self.root.after(0, self.reload_config)
                time.sleep(1)
            except:
                time.sleep(1)

    def start_forwarding(self):
        if self.running:
            return

        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.log_message("Starting port forwarding...")

        self.restart_listeners()

    def stop_forwarding(self):
        if not self.running:
            return

        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.log_message("Stopping port forwarding...")

        for listen_port, rule in self.rules.items():
            if rule["socket"]:
                try:
                    rule["socket"].close()
                except:
                    pass
                rule["socket"] = None

            if rule["thread"] and rule["thread"].is_alive():
                rule["thread"].join()
                rule["thread"] = None

        self.log_message("Port forwarding stopped")

    def restart_listeners(self):
        if not self.running:
            return

        for listen_port, rule in self.rules.items():
            if rule["socket"]:
                try:
                    rule["socket"].close()
                except:
                    pass
                rule["socket"] = None

            if rule["thread"] and rule["thread"].is_alive():
                rule["thread"].join()
                rule["thread"] = None

            thread = threading.Thread(target=self.start_listener, args=(listen_port,), daemon=True)
            rule["thread"] = thread
            thread.start()

    def start_listener(self, listen_port):
        try:
            if listen_port not in self.rules:
                return

            rule = self.rules[listen_port]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("0.0.0.0", int(listen_port)))
            sock.listen(5)
            rule["socket"] = sock

            self.log_message(f"Listening on port {listen_port}")

            while self.running:
                try:
                    client_sock, client_addr = sock.accept()
                    self.log_message(f"New connection from {client_addr} to port {listen_port}")

                    if listen_port not in self.active_connections:
                        self.active_connections[listen_port] = {}

                    conn_id = f"{client_addr[0]}:{client_addr[1]}"
                    self.active_connections[listen_port][conn_id] = {"client_sock": client_sock, "thread": None}

                    self.update_rules_tree()

                    thread = threading.Thread(
                        target=self.handle_client, args=(listen_port, conn_id, client_sock, client_addr), daemon=True
                    )
                    self.active_connections[listen_port][conn_id]["thread"] = thread
                    thread.start()

                except OSError:
                    break
                except Exception as e:
                    self.log_message(f"Error accepting connection: {str(e)}")
                    break

            sock.close()
        except Exception as e:
            self.log_message(f"Listener error on port {listen_port}: {str(e)}")

    def handle_client(self, listen_port, conn_id, client_sock, client_addr):
        try:
            if listen_port not in self.rules:
                return

            rule = self.rules[listen_port]
            forward_ip = rule["forward_ip"]
            forward_port = rule["forward_port"]

            server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_sock.connect((forward_ip, int(forward_port)))

            self.log_message(f"Forwarding {client_addr} to {forward_ip}:{forward_port}")

            client_to_server = threading.Thread(
                target=self.forward_data,
                args=(client_sock, server_sock, f"{client_addr} -> {forward_ip}:{forward_port}"),
                daemon=True,
            )

            server_to_client = threading.Thread(
                target=self.forward_data,
                args=(server_sock, client_sock, f"{forward_ip}:{forward_port} -> {client_addr}"),
                daemon=True,
            )

            client_to_server.start()
            server_to_client.start()

            client_to_server.join()
            server_to_client.join()

        except Exception as e:
            self.log_message(f"Error handling client {client_addr}: {str(e)}")
        finally:
            try:
                client_sock.close()
            except:
                pass

            try:
                server_sock.close()
            except:
                pass

            if listen_port in self.active_connections and conn_id in self.active_connections[listen_port]:
                del self.active_connections[listen_port][conn_id]
                self.update_rules_tree()

    def forward_data(self, src, dst, description):
        try:
            while self.running:
                data = src.recv(4096)
                if not data:
                    break
                dst.sendall(data)
        except:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = PortForwarder(root)
    root.mainloop()
