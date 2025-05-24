import socket
import threading
import random
from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext


class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speed Test Client")

        self.conn_frame = ttk.LabelFrame(root, text="Connection Settings")
        self.conn_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        self.host_label = ttk.Label(self.conn_frame, text="Server Host:")
        self.host_label.grid(row=0, column=0, padx=5, pady=5)

        self.host_entry = ttk.Entry(self.conn_frame)
        self.host_entry.grid(row=0, column=1, padx=5, pady=5)
        self.host_entry.insert(0, "localhost")

        self.tcp_port_label = ttk.Label(self.conn_frame, text="TCP Port:")
        self.tcp_port_label.grid(row=0, column=2, padx=5, pady=5)

        self.tcp_port_entry = ttk.Entry(self.conn_frame, width=8)
        self.tcp_port_entry.grid(row=0, column=3, padx=5, pady=5)
        self.tcp_port_entry.insert(0, "5555")

        self.udp_port_label = ttk.Label(self.conn_frame, text="UDP Port:")
        self.udp_port_label.grid(row=0, column=4, padx=5, pady=5)

        self.udp_port_entry = ttk.Entry(self.conn_frame, width=8)
        self.udp_port_entry.grid(row=0, column=5, padx=5, pady=5)
        self.udp_port_entry.insert(0, "5556")

        self.test_frame = ttk.LabelFrame(root, text="Test Settings")
        self.test_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.protocol_label = ttk.Label(self.test_frame, text="Protocol:")
        self.protocol_label.grid(row=0, column=0, padx=5, pady=5)

        self.protocol_var = tk.StringVar()
        self.protocol_combobox = ttk.Combobox(
            self.test_frame, textvariable=self.protocol_var, values=["TCP", "UDP"], state="readonly"
        )
        self.protocol_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.protocol_combobox.current(0)

        self.packet_size_label = ttk.Label(self.test_frame, text="Packet Size (bytes):")
        self.packet_size_label.grid(row=0, column=2, padx=5, pady=5)

        self.packet_size_entry = ttk.Entry(self.test_frame, width=8)
        self.packet_size_entry.grid(row=0, column=3, padx=5, pady=5)
        self.packet_size_entry.insert(0, "1024")

        self.duration_label = ttk.Label(self.test_frame, text="Duration (sec):")
        self.duration_label.grid(row=0, column=4, padx=5, pady=5)

        self.duration_entry = ttk.Entry(self.test_frame, width=8)
        self.duration_entry.grid(row=0, column=5, padx=5, pady=5)
        self.duration_entry.insert(0, "10")

        self.control_frame = ttk.Frame(root)
        self.control_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.start_btn = ttk.Button(self.control_frame, text="Start Test", command=self.start_test)
        self.start_btn.grid(row=0, column=0, padx=5, pady=5)

        self.stop_btn = ttk.Button(self.control_frame, text="Stop Test", command=self.stop_test, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=5, pady=5)

        self.log_frame = ttk.LabelFrame(root, text="Log")
        self.log_frame.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")

        self.log_area = scrolledtext.ScrolledText(self.log_frame, width=80, height=15)
        self.log_area.grid(row=0, column=0, padx=5, pady=5)

        self.test_running = False
        self.test_thread = None

        root.grid_rowconfigure(3, weight=1)
        root.grid_columnconfigure(0, weight=1)

    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)

    def start_test(self):
        if self.test_running:
            return

        try:
            host = self.host_entry.get()
            protocol = self.protocol_var.get()
            packet_size = int(self.packet_size_entry.get())
            duration = int(self.duration_entry.get())

            if protocol == "TCP":
                port = int(self.tcp_port_entry.get())
            else:
                port = int(self.udp_port_entry.get())

            if packet_size <= 0:
                raise ValueError("Packet size must be positive")
            if duration <= 0:
                raise ValueError("Duration must be positive")

            self.test_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)

            self.test_thread = threading.Thread(
                target=self.run_test, args=(host, port, protocol, packet_size, duration), daemon=True
            )
            self.test_thread.start()

            self.log_message(f"Started {protocol} test to {host}:{port} with {packet_size}B packets for {duration}s")

        except ValueError as e:
            self.log_message(f"Invalid input: {str(e)}")
        except Exception as e:
            self.log_message(f"Failed to start test: {str(e)}")

    def stop_test(self):
        if not self.test_running:
            return

        self.test_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.log_message("Test stopped by user")

    def run_test(self, host, port, protocol, packet_size, duration):
        try:
            if protocol == "TCP":
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((host, port))
                self.log_message("TCP connection established")

                end_time = datetime.now().timestamp() + duration
                packet_num = 0

                while self.test_running and datetime.now().timestamp() < end_time:
                    try:
                        send_time = datetime.now().timestamp()
                        time_str = f"{send_time:<32}".encode()
                        data = time_str + bytes([random.randint(0, 255) for _ in range(packet_size - len(time_str))])

                        sock.send(len(data).to_bytes(4, byteorder="big"))
                        sock.send(data)

                        packet_num += 1

                    except Exception as e:
                        self.log_message(f"TCP send error: {str(e)}")
                        break

                sock.close()
                self.log_message("TCP connection closed")

            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.log_message("UDP socket created")

                end_time = datetime.now().timestamp() + duration
                packet_num = 0

                while self.test_running and datetime.now().timestamp() < end_time:
                    try:
                        send_time = datetime.now().timestamp()
                        time_str = f"{send_time:<32}".encode()
                        data = (
                            packet_num.to_bytes(4, byteorder="big")
                            + time_str
                            + bytes([random.randint(0, 255) for _ in range(packet_size - 36)])
                        )

                        sock.sendto(data, (host, port))
                        packet_num += 1

                    except Exception as e:
                        self.log_message(f"UDP send error: {str(e)}")
                        break

                sock.close()
                self.log_message("UDP socket closed")

            self.test_running = False
            self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))

        except Exception as e:
            self.log_message(f"Test error: {str(e)}")
            self.test_running = False
            self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()
