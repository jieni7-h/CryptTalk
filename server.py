import socket
import threading
from crypto_utils import *

# 配置
HOST = '127.0.0.1'
PORT = 12345

des_key = None  # 协商后的 DES 密钥

def receive_messages(conn):
    """接收消息的线程"""
    global des_key
    try:
        while True:
            # 接收消息（格式: 密文Base64|摘要Base64）
            data = conn.recv(4096).decode()
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
                print(f"\n[客户端] {message} [完整性校验通过]")
            else:
                print(f"\n[客户端] {message} [警告: 消息已被篡改!]")
            print("你: ", end="", flush=True)
    except Exception as e:
        print(f"接收线程结束: {e}")

def main():
    global des_key
    
    print("===== 服务器启动 =====")
    
    # 1. 生成 RSA 密钥对
    private_key, public_key = generate_rsa_keypair()
    print("RSA 密钥对生成完成")
    
    # 2. 监听端口
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"等待客户端连接... ({HOST}:{PORT})")
    
    conn, addr = server_socket.accept()
    print(f"客户端已连接: {addr}")
    
    # 3. 发送 RSA 公钥
    pub_key_b64 = public_key_to_base64(public_key)
    conn.send(pub_key_b64.encode())
    print("已发送 RSA 公钥")
    
    # 4. 接收加密的 DES 密钥
    encrypted_des_key_b64 = conn.recv(4096).decode()
    encrypted_des_key = base64_to_bytes(encrypted_des_key_b64)
    des_key_bytes = rsa_decrypt(encrypted_des_key, private_key)
    des_key = des_key_bytes  # DES 密钥是 8 字节
    print("已获取并解密 DES 密钥")
    
    # 5. 启动接收线程
    receive_thread = threading.Thread(target=receive_messages, args=(conn,), daemon=True)
    receive_thread.start()
    
    # 6. 主线程发送消息
    print("开始聊天（输入 'exit' 退出）")
    try:
        while True:
            msg = input("你: ")
            if msg.lower() == 'exit':
                break
            
            # 加密消息
            plain_data = msg.encode('utf-8')
            cipher_data = des_encrypt(plain_data, des_key)
            digest = md5(plain_data)
            
            # 发送格式: 密文Base64|摘要Base64
            to_send = bytes_to_base64(cipher_data) + '|' + bytes_to_base64(digest)
            conn.send(to_send.encode())
    except Exception as e:
        print(f"发送错误: {e}")
    finally:
        conn.close()
        server_socket.close()
        print("服务器关闭")

if __name__ == "__main__":
    main()