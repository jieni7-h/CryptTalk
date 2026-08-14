import socket
import threading
from crypto_utils import *

# 配置
HOST = '127.0.0.1'  # 同一台机器，如果是不同机器改成服务器 IP
PORT = 12345

des_key = None

def receive_messages(sock):
    """接收消息的线程"""
    global des_key
    try:
        while True:
            data = sock.recv(4096).decode()
            if not data:
                break
            
            parts = data.split('|')
            if len(parts) != 2:
                continue
            
            cipher_b64, digest_b64 = parts
            cipher_data = base64_to_bytes(cipher_b64)
            received_digest = base64_to_bytes(digest_b64)
            
            # DES 解密
            plain_data = des_decrypt(cipher_data, des_key)
            message = plain_data.decode('utf-8')
            
            # 验证 MD5
            computed_digest = md5(plain_data)
            
            if computed_digest == received_digest:
                print(f"\n[服务器] {message} [完整性校验通过]")
            else:
                print(f"\n[服务器] {message} [警告: 消息已被篡改!]")
            print("你: ", end="", flush=True)
    except Exception as e:
        print(f"接收线程结束: {e}")

def main():
    global des_key
    
    print("===== 客户端启动 =====")
    
    # 1. 连接服务器
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    print(f"已连接到服务器 {HOST}:{PORT}")
    
    # 2. 接收 RSA 公钥
    pub_key_b64 = sock.recv(4096).decode()
    public_key = base64_to_public_key(pub_key_b64)
    print("已收到 RSA 公钥")
    
    # 3. 生成 DES 密钥，用 RSA 公钥加密后发送
    des_key = generate_des_key()
    encrypted_des_key = rsa_encrypt(des_key, public_key)
    sock.send(bytes_to_base64(encrypted_des_key).encode())
    print("已发送加密后的 DES 密钥")
    
    # 4. 启动接收线程
    receive_thread = threading.Thread(target=receive_messages, args=(sock,), daemon=True)
    receive_thread.start()
    
    # 5. 发送消息
    print("开始聊天（输入 'exit' 退出）")
    try:
        while True:
            msg = input("你: ")
            if msg.lower() == 'exit':
                break
            
            plain_data = msg.encode('utf-8')
            cipher_data = des_encrypt(plain_data, des_key)
            digest = md5(plain_data)
            
            to_send = bytes_to_base64(cipher_data) + '|' + bytes_to_base64(digest)
            sock.send(to_send.encode())
    except Exception as e:
        print(f"发送错误: {e}")
    finally:
        sock.close()
        print("客户端关闭")

if __name__ == "__main__":
    main()