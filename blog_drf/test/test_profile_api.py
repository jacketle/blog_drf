import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

# 用户登录信息
login_data = {
    "username": "jacketle",
    "password": "zjl123456"
}

# 1. 获取JWT令牌
print("正在获取JWT令牌...")
token_response = requests.post(f"{BASE_URL}/api/users/token/", json=login_data)

if token_response.status_code == 200:
    tokens = token_response.json()
    access_token = tokens["access"]
    refresh_token = tokens["refresh"]
    print(f"访问令牌: {access_token}")
    print(f"刷新令牌: {refresh_token}")

    # 2. 使用访问令牌访问profile接口
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    print("\n正在访问profile接口...")
    profile_response = requests.get(f"{BASE_URL}/api/users/profile/", headers=headers)

    if profile_response.status_code == 200:
        profile_data = profile_response.json()
        print("用户资料获取成功:")
        print(json.dumps(profile_data, indent=2, ensure_ascii=False))
    else:
        print(f"访问profile接口失败，状态码: {profile_response.status_code}")
        print(profile_response.text)

        # 3. 自动刷新令牌并重试
        if profile_response.status_code == 401 or profile_response.status_code == 403:
            print("\n访问令牌已过期，正在刷新令牌...")
            refresh_response = requests.post(
                f"{BASE_URL}/api/token/refresh/",
                json={"refresh": refresh_token}
            )

            if refresh_response.status_code == 200:
                new_tokens = refresh_response.json()
                access_token = new_tokens["access"]
                print(f"新访问令牌: {access_token}")

                # 使用新访问令牌重新访问接口
                headers = {"Authorization": f"Bearer {access_token}"}
                profile_response = requests.get(
                    f"{BASE_URL}/api/users/profile/",
                    headers=headers
                )

                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    print("用户资料获取成功:")
                    print(json.dumps(profile_data, indent=2, ensure_ascii=False))
                else:
                    print(f"刷新后访问失败，状态码: {profile_response.status_code}")
                    print(profile_response.text)
            else:
                print("刷新令牌失败")
                print(refresh_response.text)
else:
    print(f"获取令牌失败，状态码: {token_response.status_code}")
    print(token_response.text)