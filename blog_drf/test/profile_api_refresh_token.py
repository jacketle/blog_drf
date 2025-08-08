import requests
import time

# 刷新令牌
access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUzNzk2MjEyLCJpYXQiOjE3NTM3OTI2MTIsImp0aSI6IjMxMzUzMGNkMzYyNzRiY2Y4ODdlOWQ0NWU2NTE3MTIzIiwidXNlcl9pZCI6IjIifQ.5ZC-o_BsyirVdRbxOsHEMZ6KfpDlaBBi9TEukmTh_1Y"
refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc1Mzg3OTAxMiwiaWF0IjoxNzUzNzkyNjEyLCJqdGkiOiIyOWE2ZTUzMWMyMzE0MjU1YjExMTVhNDE1NzA4Yjk2MSIsInVzZXJfaWQiOiIyIn0.VRDKgjfIXY_qpqgl2Go1g9nQneNH5aO7gdM_wsOv2jE"


# 刷新接口
def refresh_access_token():
    refresh_url = "http://localhost:8000/api/token/refresh/"
    data = {"refresh": refresh_token}
    response = requests.post(refresh_url, json=data)
    if response.status_code == 200:
        return response.json()["access"]
    else:
        raise Exception("刷新令牌失败")


# 访问接口（带自动刷新）
def access_protected_api():
    url = "http://localhost:8000/api/users/profile/"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 401:
        print("访问令牌已过期，正在刷新...")
        new_access_token = refresh_access_token()
        headers["Authorization"] = f"Bearer {new_access_token}"
        response = requests.get(url, headers=headers)

    return response


# 执行访问
response = access_protected_api()
print("最终响应:", response.status_code, response.json())