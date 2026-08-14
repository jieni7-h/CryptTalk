import hashlib

# 计算 "hello" 的 MD5 摘要
md5_value = hashlib.md5(b"hello").hexdigest()

print(f"明文: hello")
print(f"MD5 摘要: {md5_value}")
print(f"摘要长度: {len(md5_value)} 字节")