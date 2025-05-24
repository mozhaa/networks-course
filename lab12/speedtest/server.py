import socket
import threading
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext, ttk
from common import format_size, format_speed


class ServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speed Test Server")

        self.tcp_frame = ttk.LabelFrame(root, text="TCP Server")
        self.tcp_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        self.tcp_port_label = ttk.Label(self.tcp_frame, text="TCP Port:")
        self.tcp_port_label.grid(row=0, column=0, padx=5, pady=5)

        self.tcp_port_entry = ttk.Entry(self.tcp_frame)
        self.tcp_port_entry.grid(row=0, column=1, padx=5, pady=5)
        self.tcp_port_entry.insert(0, "5555")

        self.tcp_start_btn = ttk.Button(self.tcp_frame, text="Start", command=self.start_tcp_server)
        self.tcp_start_btn.grid(row=0, column=2, padx=5, pady=5)

        self.tcp_status_label = ttk.Label(self.tcp_frame, text="Status: Stopped")
        self.tcp_status_label.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        self.udp_frame = ttk.LabelFrame(root, text="UDP Server")
        self.udp_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        self.udp_port_label = ttk.Label(self.udp_frame, text="UDP Port:")
        self.udp_port_label.grid(row=0, column=0, padx=5, pady=5)

        self.udp_port_entry = ttk.Entry(self.udp_frame)
        self.udp_port_entry.grid(row=0, column=1, padx=5, pady=5)
        self.udp_port_entry.insert(0, "5556")

        self.udp_start_btn = ttk.Button(self.udp_frame, text="Start", command=self.start_udp_server)
        self.udp_start_btn.grid(row=0, column=2, padx=5, pady=5)

        self.udp_status_label = ttk.Label(self.udp_frame, text="Status: Stopped")
        self.udp_status_label.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        self.log_frame = ttk.LabelFrame(root, text="Log")
        self.log_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        self.log_area = scrolledtext.ScrolledText(self.log_frame, width=60, height=15)
        self.log_area.grid(row=0, column=0, padx=5, pady=5)

        self.stats_frame = ttk.LabelFrame(root, text="Statistics")
        self.stats_frame.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")

        self.tcp_stats_label = ttk.Label(self.stats_frame, text="TCP: 0 packets, 0 B, 0 B/s")
        self.tcp_stats_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.udp_stats_label = ttk.Label(self.stats_frame, text="UDP: 0 packets, 0 B, 0 B/s, 0% loss")
        self.udp_stats_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.tcp_server_running = False
        self.udp_server_running = False
        self.tcp_stats = {"total_bytes": 0, "start_time": None, "packets": 0}
        self.udp_stats = {"total_bytes": 0, "start_time": None, "packets": 0, "expected_packets": 0}

        root.grid_rowconfigure(2, weight=1)
        root.grid_columnconfigure(0, weight=1)

    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)

    def start_tcp_server(self):
        if self.tcp_server_running:
            return

        port = int(self.tcp_port_entry.get())

        try:
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.bind(("0.0.0.0", port))
            self.tcp_socket.listen(1)

            self.tcp_server_running = True
            self.tcp_status_label.config(text=f"Status: Running on port {port}")
            self.tcp_start_btn.config(text="Stop", command=self.stop_tcp_server)

            self.tcp_stats = {"total_bytes": 0, "start_time": None, "packets": 0}
            self.update_stats()

            threading.Thread(target=self.tcp_server_thread, daemon=True).start()
            self.log_message(f"TCP server started on port {port}")
        except Exception as e:
            self.log_message(f"Failed to start TCP server: {str(e)}")

    def stop_tcp_server(self):
        if not self.tcp_server_running:
            return

        self.tcp_server_running = False
        try:
            self.tcp_socket.close()
        except:
            pass

        self.tcp_status_label.config(text="Status: Stopped")
        self.tcp_start_btn.config(text="Start", command=self.start_tcp_server)
        self.log_message("TCP server stopped")

    def tcp_server_thread(self):
        while self.tcp_server_running:
            try:
                conn, addr = self.tcp_socket.accept()
                self.log_message(f"TCP connection established with {addr}")

                if self.tcp_stats["start_time"] is None:
                    self.tcp_stats["start_time"] = datetime.now()

                while self.tcp_server_running:
                    try:
                        packet_len_data = conn.recv(4)
                        if not packet_len_data:
                            break

                        packet_len = int.from_bytes(packet_len_data, byteorder="big")

                        data = conn.recv(packet_len)
                        if not data:
                            break

                        send_time = datetime.fromtimestamp(float(data[:32].decode().strip()))
                        delay = (datetime.now() - send_time).total_seconds() * 1000

                        self.tcp_stats["total_bytes"] += len(data)
                        self.tcp_stats["packets"] += 1

                        self.log_message(f"TCP packet received from {addr}, delay: {delay:.2f} ms")

                    except ConnectionResetError:
                        break
                    except Exception as e:
                        self.log_message(f"TCP error: {str(e)}")
                        break

                conn.close()
                self.log_message(f"TCP connection with {addr} closed")

            except OSError:
                break
            except Exception as e:
                self.log_message(f"TCP server error: {str(e)}")
                break

    def start_udp_server(self):
        if self.udp_server_running:
            return

        port = int(self.udp_port_entry.get())

        try:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.bind(("0.0.0.0", port))

            self.udp_server_running = True
            self.udp_status_label.config(text=f"Status: Running on port {port}")
            self.udp_start_btn.config(text="Stop", command=self.stop_udp_server)

            self.udp_stats = {"total_bytes": 0, "start_time": None, "packets": 0, "expected_packets": 0}
            self.update_stats()

            threading.Thread(target=self.udp_server_thread, daemon=True).start()
            self.log_message(f"UDP server started on port {port}")
        except Exception as e:
            self.log_message(f"Failed to start UDP server: {str(e)}")

    def stop_udp_server(self):
        if not self.udp_server_running:
            return

        self.udp_server_running = False
        try:
            self.udp_socket.close()
        except:
            pass

        self.udp_status_label.config(text="Status: Stopped")
        self.udp_start_btn.config(text="Start", command=self.start_udp_server)
        self.log_message("UDP server stopped")

    def udp_server_thread(self):
        while self.udp_server_running:
            try:
                data, addr = self.udp_socket.recvfrom(65507)

                if self.udp_stats["start_time"] is None:
                    self.udp_stats["start_time"] = datetime.now()

                if len(data) >= 36:
                    packet_num = int.from_bytes(data[:4], byteorder="big")
                    send_time = datetime.fromtimestamp(float(data[4:36].decode().strip()))
                    delay = (datetime.now() - send_time).total_seconds() * 1000

                    self.udp_stats["expected_packets"] = max(self.udp_stats["expected_packets"], packet_num + 1)
                    self.udp_stats["total_bytes"] += len(data)
                    self.udp_stats["packets"] += 1

                    self.log_message(f"UDP packet #{packet_num} received from {addr}, delay: {delay:.2f} ms")

            except OSError:
                break
            except Exception as e:
                self.log_message(f"UDP server error: {str(e)}")
                break

    def format_stats(self, packets, total_bytes, speed):
        return f"{packets} packets ({format_size(total_bytes)}), Speed: {format_speed(speed)}"

    def update_stats(self):
        if self.tcp_stats["start_time"]:
            elapsed = (datetime.now() - self.tcp_stats["start_time"]).total_seconds()
            if elapsed > 0:
                speed = self.tcp_stats["total_bytes"] / elapsed
                self.tcp_stats_label.config(
                    text="TCP: " + self.format_stats(self.tcp_stats["packets"], self.tcp_stats["total_bytes"], speed)
                )

        if self.udp_stats["start_time"]:
            elapsed = (datetime.now() - self.udp_stats["start_time"]).total_seconds()
            if elapsed > 0:
                speed = self.udp_stats["total_bytes"] / elapsed
                loss_percent = 0
                if self.udp_stats["expected_packets"] > 0:
                    loss_percent = 1 - self.udp_stats["packets"] / self.udp_stats["expected_packets"]
                self.udp_stats_label.config(
                    text="UDP: "
                    + self.format_stats(self.udp_stats["packets"], self.udp_stats["total_bytes"], speed)
                    + f", {loss_percent:.2%} loss"
                )

        if self.tcp_server_running or self.udp_server_running:
            self.root.after(1000, self.update_stats)


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerApp(root)
    root.mainloop()
