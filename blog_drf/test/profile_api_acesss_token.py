import requests

# 已获取的访问令牌
access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUzNzk2MjEyLCJpYXQiOjE3NTM3OTI2MTIsImp0aSI6IjMxMzUzMGNkMzYyNzRiY2Y4ODdlOWQ0NWU2NTE3MTIzIiwidXNlcl9pZCI6IjIifQ.5ZC-o_BsyirVdRbxOsHEMZ6KfpDlaBBi9TEukmTh_1Y"

# 目标接口
url = "http://localhost:8000/api/users/profile/"

# 设置请求头
headers = {
    "Authorization": f"Bearer {access_token}"
}

# 发送请求
response = requests.get(url, headers=headers)

# 处理响应
if response.status_code == 200:
    print("访问成功:", response.json())
else:
    print("访问失败:", response.status_code, response.text)