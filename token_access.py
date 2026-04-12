import requests
import json
# === 配置你的信息 ===
with open("config.json",'r') as f:
    config=json.load(f)
CLIENT_ID = config["CLIENT_ID"]
CLIENT_SECRET = config["CLIENT_SECRET"]
REDIRECT_URI = config["REDIRECT_URI"]  # 必须与后台配置一致
SCOPE =  config["SCOPE"] # 权限范围

def get_ticktick_token():
    # 第一步：构建授权链接
    auth_url = (
        f"https://ticktick.com/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={SCOPE}"
    )
    
    print("1. 请在浏览器中打开以下链接进行授权：")
    print(f"\n{auth_url}\n")
    
    # 第二步：获取用户授权后的回调 URL
    callback_url = input("2. 授权成功后，请将浏览器地址栏完整的 URL 粘贴到这里：\n").strip()
    
    # 从 URL 中提取 code 参数
    try:
        if 'code=' not in callback_url:
            print("错误：URL 中未包含 code 参数。")
            return
        auth_code = callback_url.split('code=')[1].split('&')[0]
    except Exception as e:
        print(f"解析 URL 失败: {e}")
        return

    # 第三步：用 code 换取 Access Token
    token_url = "https://ticktick.com/oauth/token"
    
    # 注意：TickTick 要求 client_id/secret 放在 Basic Auth 中或 Post Body
    # 下面是使用 Post Body 的标准做法
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'scope': SCOPE,
        'redirect_uri': REDIRECT_URI
    }
    
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get('access_token')
        print("\n[成功] 你的 Access Token 是：")
        print(access_token)
        with open('config.json','r') as f:
            temp=json.load(f)
        if temp["Access_token"]!=" ":
            print("已经有token了")
            rw=str(input("是否仍然修改[Y/N]"))
            if rw=="Y" or rw=="y":
                temp["Access_token"]=access_token
                with open("config.json","w") as f:
                    json.dump(temp,f,indent=4)
                    print("修改成功")
            elif rw=="N" or rw=="n":
                print("已取消")
            else:
                print("输入不合法")
        else:
            temp["Access_token"]=access_token
            with open("config.json","w") as f:
                json.dump(temp,f,indent=4)
                print("修改成功")
        return access_token
    else:
        print(f"\n[失败] 无法获取 Token: {response.text}")
        return None

if __name__ == "__main__":
    get_ticktick_token()