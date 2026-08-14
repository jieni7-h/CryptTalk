import socket
import threading
import tkinter as tk
import base64
import hashlib
import os
from datetime import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class CryptTalkServer:
    def __init__(self):
        self.server_socket = None
        self.client_socket = None
        self.des_key = None
        self.running = False
        self.root = tk.Tk()
        self.root.title("CryptTalk - 服务器端")
        self.root.geometry("800x600")
        self.root.minsize(600, 450)
        self.root.resizable(True, True)
        self.root.configure(bg='#f5f5f5')
        self.create_widgets()

    # ---------- 自定义美化弹窗 ----------
    def show_custom_dialog(self, title, message, msg_type='info'):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("520x350")
        dialog.resizable(False, False)
        dialog.configure(bg='#ffffff')
        dialog.transient(self.root)
        dialog.grab_set()
        
        if msg_type == 'info':
            icon, color = "ℹ️", "#2196F3"
        elif msg_type == 'success':
            icon, color = "✅", "#4CAF50"
        elif msg_type == 'warning':
            icon, color = "⚠️", "#FF9800"
        elif msg_type == 'error':
            icon, color = "❌", "#F44336"
        else:
            icon, color = "🔒", "#9C27B0"
        
        top_bar = tk.Frame(dialog, bg=color, height=5)
        top_bar.pack(fill=tk.X)
        
        content_frame = tk.Frame(dialog, bg='#ffffff', padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(content_frame, text=icon, font=('Segoe UI', 40), bg='#ffffff').pack(pady=(10, 5))
        tk.Label(content_frame, text=title, font=('微软雅黑', 14, 'bold'), bg='#ffffff', fg=color).pack(pady=(0, 15))
        
        text_frame = tk.Frame(content_frame, bg='#ffffff')
        text_frame.pack(fill=tk.BOTH, expand=True)
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 10), bg='#f9f9f9',
                              relief=tk.FLAT, padx=10, pady=10)
        text_widget.insert('1.0', message)
        text_widget.config(state=tk.DISABLED)
        scrollbar = tk.Scrollbar(text_frame, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        btn_frame = tk.Frame(content_frame, bg='#ffffff')
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        tk.Button(btn_frame, text="确定", command=dialog.destroy,
                  bg=color, fg='white', font=('微软雅黑', 10, 'bold'),
                  relief=tk.FLAT, padx=20, pady=5, cursor='hand2').pack()
        self.root.wait_window(dialog)

    # ---------- GUI 布局 ----------
    def create_widgets(self):
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="CryptTalk 服务器", font=('微软雅黑', 16, 'bold'),
                 bg='#2c3e50', fg='white').pack(pady=12)
        
        control_frame = tk.Frame(self.root, bg='#ecf0f1', height=45)
        control_frame.pack(fill=tk.X)
        control_frame.pack_propagate(False)
        
        self.status_canvas = tk.Canvas(control_frame, width=12, height=12, bg='#ecf0f1', highlightthickness=0)
        self.status_canvas.pack(side=tk.LEFT, padx=(15, 5), pady=16)
        self.status_light = self.status_canvas.create_oval(2, 2, 10, 10, fill='#95a5a6', outline='')
        self.status_label = tk.Label(control_frame, text="未启动", font=('微软雅黑', 10), fg='#7f8c8d', bg='#ecf0f1')
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        tk.Label(control_frame, text="端口:", font=('微软雅黑', 10), bg='#ecf0f1').pack(side=tk.LEFT, padx=(20, 5))
        self.port_entry = tk.Entry(control_frame, width=8, font=('微软雅黑', 10))
        self.port_entry.insert(0, "12345")
        self.port_entry.pack(side=tk.LEFT, padx=5)
        
        self.start_btn = tk.Button(control_frame, text="启动服务器", command=self.start_server,
                                   bg='#27ae60', fg='white', font=('微软雅黑', 10, 'bold'),
                                   relief=tk.FLAT, padx=12, pady=4, cursor='hand2')
        self.start_btn.pack(side=tk.LEFT, padx=10, pady=8)
        self.stop_btn = tk.Button(control_frame, text="停止服务器", command=self.stop_server,
                                  bg='#e74c3c', fg='white', font=('微软雅黑', 10, 'bold'),
                                  relief=tk.FLAT, padx=12, pady=4, cursor='hand2', state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5, pady=8)
        
        main_chat_frame = tk.Frame(self.root, bg='#f5f5f5')
        main_chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(8, 5))
        self.chat_canvas = tk.Canvas(main_chat_frame, bg='#f5f5f5', highlightthickness=0)
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(main_chat_frame, command=self.chat_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_canvas.configure(yscrollcommand=scrollbar.set)
        self.messages_frame = tk.Frame(self.chat_canvas, bg='#f5f5f5')
        self.chat_canvas.create_window((0, 0), window=self.messages_frame, anchor='nw', width=self.chat_canvas.winfo_width())
        self.messages_frame.bind("<Configure>", self.on_frame_configure)
        self.chat_canvas.bind("<Configure>", self.on_canvas_configure)
        
        input_frame = tk.Frame(self.root, bg='#ffffff', relief=tk.RAISED, bd=1)
        input_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.message_entry = tk.Text(input_frame, height=3, font=('微软雅黑', 11),
                                     wrap=tk.WORD, bd=0, padx=10, pady=8)
        self.message_entry.pack(fill=tk.X, padx=10, pady=(10, 5))
        self.message_entry.bind('<Return>', lambda e: self.send_message())
        self.message_entry.bind('<Shift-Return>', lambda e: None)
        btn_frame = tk.Frame(input_frame, bg='#ffffff')
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.send_btn = tk.Button(btn_frame, text="发送", command=self.send_message,
                                  bg='#27ae60', fg='white', font=('微软雅黑', 11, 'bold'),
                                  relief=tk.FLAT, padx=25, pady=8, cursor='hand2')
        self.send_btn.pack(side=tk.RIGHT)
        
        info_frame = tk.Frame(self.root, bg='#ecf0f1', height=25)
        info_frame.pack(fill=tk.X, side=tk.BOTTOM)
        info_frame.pack_propagate(False)
        self.status_bar = tk.Label(info_frame, text="就绪", font=('微软雅黑', 9), fg='#7f8c8d', bg='#ecf0f1')
        self.status_bar.pack(side=tk.LEFT, padx=10, pady=4)
        tk.Label(info_frame, text="🔒 RSA | DES | MD5", font=('微软雅黑', 9), fg='#7f8c8d', bg='#ecf0f1').pack(side=tk.RIGHT, padx=10, pady=4)
        self.root.bind('<Configure>', self.on_window_resize)

    def on_frame_configure(self, event):
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
    def on_canvas_configure(self, event):
        self.chat_canvas.itemconfig(1, width=event.width)
    def on_window_resize(self, event):
        for widget in self.messages_frame.winfo_children():
            if hasattr(widget, 'update_width'):
                widget.update_width()

    def create_bubble(self, message, is_sender=True, is_system=False):
        if is_system:
            frame = tk.Frame(self.messages_frame, bg='#f5f5f5')
            frame.pack(fill=tk.X, pady=4)
            tk.Label(frame, text=message, font=('微软雅黑', 9),
                     bg='#e0e0e0', fg='#666666', padx=12, pady=4).pack(pady=2)
        else:
            frame = tk.Frame(self.messages_frame, bg='#f5f5f5')
            frame.pack(fill=tk.X, pady=6)
            content_frame = tk.Frame(frame, bg='#f5f5f5')
            if is_sender:
                content_frame.pack(side=tk.RIGHT, padx=10)
                time_str = datetime.now().strftime("%H:%M")
                tk.Label(content_frame, text=time_str, font=('微软雅黑', 8), fg='#999999', bg='#f5f5f5').pack(side=tk.RIGHT, padx=(5, 0))
                bubble = tk.Label(content_frame, text=message, font=('微软雅黑', 11), bg='#95ec69', fg='#000000', wraplength=300, justify=tk.LEFT, padx=12, pady=8)
                bubble.pack(side=tk.RIGHT)
                tk.Label(content_frame, text="✓", font=('微软雅黑', 10), fg='#999999', bg='#f5f5f5').pack(side=tk.RIGHT, padx=2)
            else:
                content_frame.pack(side=tk.LEFT, padx=10)
                tk.Label(content_frame, text="📱", font=('微软雅黑', 14), bg='#f5f5f5').pack(side=tk.LEFT, padx=(0, 5))
                bubble = tk.Label(content_frame, text=message, font=('微软雅黑', 11), bg='#ffffff', fg='#000000', wraplength=300, justify=tk.LEFT, padx=12, pady=8)
                bubble.pack(side=tk.LEFT)
                time_str = datetime.now().strftime("%H:%M")
                tk.Label(content_frame, text=time_str, font=('微软雅黑', 8), fg='#999999', bg='#f5f5f5').pack(side=tk.LEFT, padx=(5, 0))
            def update_width():
                max_width = min(400, self.chat_canvas.winfo_width() - 120)
                bubble.configure(wraplength=max_width)
            frame.update_width = update_width
            update_width()
        self.root.after(50, lambda: self.chat_canvas.yview_moveto(1.0))

    def log_message(self, msg, is_sender=True, is_system=False):
        if is_system:
            self.create_bubble(msg, is_sender=False, is_system=True)
        else:
            self.create_bubble(msg, is_sender=is_sender, is_system=False)

    def update_status(self, status, color, is_online=False):
        self.status_label.config(text=status, fg=color)
        self.status_canvas.itemconfig(self.status_light, fill='#2ecc71' if is_online else '#95a5a6')

    # ---------- 加密函数 ----------
    def generate_rsa_keypair(self):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        pem = private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()).decode()
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "RSA私钥.txt")
        with open(desktop_path, "w", encoding="utf-8") as f:
            f.write(pem)
        self.log_message(f"✅ RSA 私钥已保存至: {desktop_path}", is_system=True)
        return private_key, private_key.public_key()

    def rsa_decrypt(self, data, private_key):
        return private_key.decrypt(data, padding.PKCS1v15())
    def des_decrypt(self, data_b64, key):
        data = base64.b64decode(data_b64)
        cipher = Cipher(algorithms.TripleDES(key), modes.ECB(), backend=default_backend())
        decryptor = cipher.decryptor()
        plain_padded = decryptor.update(data) + decryptor.finalize()
        pad_len = plain_padded[-1]
        return plain_padded[:-pad_len].decode('utf-8')
    def des_encrypt(self, data, key):
        cipher = Cipher(algorithms.TripleDES(key), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()
        pad_len = 8 - (len(data) % 8)
        data += bytes([pad_len] * pad_len)
        encrypted = encryptor.update(data) + encryptor.finalize()
        return base64.b64encode(encrypted).decode()
    def md5_hash(self, data):
        return hashlib.md5(data.encode()).hexdigest()

    # ---------- 核心逻辑 ----------
    def start_server(self):
        try:
            port = int(self.port_entry.get())
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(('0.0.0.0', port))
            self.server_socket.listen(1)
            self.running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.update_status("等待连接", '#f39c12', False)
            self.log_message(f"服务器已启动，端口: {port}", is_system=True)
            self.status_bar.config(text=f"监听端口 {port}...")
            threading.Thread(target=self.accept_connection, daemon=True).start()
        except Exception as e:
            self.show_custom_dialog("错误", f"启动服务器失败: {e}", 'error')

    def accept_connection(self):
        try:
            self.client_socket, addr = self.server_socket.accept()
            self.log_message(f"客户端已连接: {addr[0]}:{addr[1]}", is_system=True)
            self.update_status("已连接", '#27ae60', True)
            self.status_bar.config(text=f"已连接客户端: {addr[0]}")
            
            rsa_private, rsa_public = self.generate_rsa_keypair()
            public_key_b64 = base64.b64encode(rsa_public.public_bytes(encoding=serialization.Encoding.DER, format=serialization.PublicFormat.SubjectPublicKeyInfo)).decode()
            self.show_custom_dialog("RSA 公钥 (服务端)", f"生成的 RSA 公钥 (Base64):\n\n{public_key_b64}", 'info')
            self.client_socket.send(public_key_b64.encode())
            
            raw_len = self.client_socket.recv(4)
            if not raw_len:
                raise Exception("未收到DES密钥长度")
            key_len = int.from_bytes(raw_len, 'big')
            encrypted_key_data = b''
            while len(encrypted_key_data) < key_len:
                chunk = self.client_socket.recv(min(4096, key_len - len(encrypted_key_data)))
                if not chunk:
                    break
                encrypted_key_data += chunk
            encrypted_key_b64 = encrypted_key_data.decode()
            encrypted_key = base64.b64decode(encrypted_key_b64)
            self.des_key = self.rsa_decrypt(encrypted_key, rsa_private)
            self.show_custom_dialog("DES 密钥 (服务端)", f"RSA 解密后得到的 DES 密钥 (Hex):\n\n{self.des_key.hex()}", 'success')
            self.log_message("🔒 加密通道已建立，可开始对话", is_system=True)
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            self.log_message(f"连接失败: {e}", is_system=True)
            self.stop_server()

    def receive_messages(self):
        while self.running and self.client_socket:
            try:
                raw_len = self.client_socket.recv(4)
                if not raw_len:
                    break
                msg_len = int.from_bytes(raw_len, 'big')
                data = b''
                while len(data) < msg_len:
                    chunk = self.client_socket.recv(min(4096, msg_len - len(data)))
                    if not chunk:
                        break
                    data += chunk
                if len(data) != msg_len:
                    break
                decoded = data.decode('utf-8')
                parts = decoded.split('|')
                if len(parts) == 2:
                    encrypted_msg, received_md5 = parts
                    self.show_custom_dialog("收到加密消息", f"密文 (Base64):\n{encrypted_msg[:200]}{'...' if len(encrypted_msg)>200 else ''}\n\n附带的 MD5: {received_md5}", 'info')
                    decrypted = self.des_decrypt(encrypted_msg, self.des_key)
                    computed_md5 = self.md5_hash(decrypted)
                    if computed_md5 == received_md5:
                        self.show_custom_dialog("解密成功", f"解密后明文: {decrypted}\n\n重新计算的 MD5: {computed_md5}\n\n✅ 校验通过，消息未被篡改", 'success')
                        self.log_message(decrypted, is_sender=False, is_system=False)
                    else:
                        self.show_custom_dialog("MD5校验失败", f"解密后明文: {decrypted}\n\n重新计算的 MD5: {computed_md5}\n\n❌ 校验失败！消息可能被篡改！", 'warning')
                        self.log_message(f"{decrypted} ⚠ 消息已被篡改！", is_sender=False, is_system=False)
                else:
                    self.log_message(f"格式错误: {decoded[:100]}", is_system=True)
            except Exception as e:
                if self.running:
                    self.log_message(f"接收失败: {e}", is_system=True)
                break
        if self.running:
            self.log_message("客户端已断开", is_system=True)
            self.update_status("已断开", '#e74c3c', False)
            self.status_bar.config(text="连接已断开")

    def send_message(self):
        msg = self.message_entry.get("1.0", tk.END).strip()
        if not msg or not self.client_socket or not self.des_key:
            return
        self.show_custom_dialog("发送消息 (服务端)", f"原始消息: {msg}\n\nMD5 哈希值: {self.md5_hash(msg)}", 'info')
        encrypted = self.des_encrypt(msg.encode(), self.des_key)
        self.show_custom_dialog("DES 加密结果", f"DES 加密后的密文 (Base64):\n{encrypted[:200]}{'...' if len(encrypted)>200 else ''}", 'info')
        payload = f"{encrypted}|{self.md5_hash(msg)}".encode('utf-8')
        header = len(payload).to_bytes(4, 'big')
        try:
            self.client_socket.send(header + payload)
            self.log_message(msg, is_sender=True, is_system=False)
            self.message_entry.delete("1.0", tk.END)
            self.status_bar.config(text=f"已发送: {msg[:50]}")
        except Exception as e:
            self.log_message(f"发送失败: {e}", is_system=True)

    def stop_server(self):
        self.running = False
        if self.client_socket:
            try: self.client_socket.close()
            except: pass
        if self.server_socket:
            try: self.server_socket.close()
            except: pass
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.update_status("已停止", '#e74c3c', False)
        self.log_message("服务器已停止", is_system=True)
        self.status_bar.config(text="服务器已停止")

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    def on_closing(self):
        self.stop_server()
        self.root.destroy()

if __name__ == "__main__":
    app = CryptTalkServer()
    app.run()