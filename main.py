import json
import requests
from datetime import datetime 
import logging
import os
import sys

# 1. 读取主配置
with open("config.json", "r") as f:
    config = json.load(f)

ACCESS_TOKEN = config["Access_token"]
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# 2. 读取任务设置并初始化日志 (将原 list 改名为 t_setting)
with open("tasks_setting.json", "r") as f:
    t_setting = json.load(f)

logging.basicConfig(
    filename=t_setting["log_location"], 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# 3. 获取参数任务中的数据
task_config = {}
try:
    # 引号修正：外部双引，内部单引
    url_r = f"https://api.ticktick.com/open/v1/project/{config['config_task']['PROJECT']}/task/{config['config_task']['ID']}"
    response_get = requests.get(url_r, headers=headers)
    response_get.raise_for_status()

    task_data = response_get.json()
    task_content = task_data.get("content", "")
    print(f"Task Content: {task_content}")
    
    lines = task_content.split('\n')
    for line in lines:
        if "=" in line:
            key, value = line.split("=", 1)
            task_config[key.strip()] = value.strip()
except requests.exceptions.RequestException as e:
    task_config = {"roomweek": "False", "workstatus": "True"}
    logging.error(f"fail to access config_task[{config['config_task']['ID']}]")

if task_config.get("workstatus") == "False":
    logging.info("resting")
    sys.exit()

def task_clear(task_id, project_id, token):
    # 此处原有的 list = json.load(f) 已删除，因为函数内未使用该变量
    print(f"task_clear start for: {task_id}")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    today_str = datetime.now().strftime("%Y-%m-%d")
    payload = {
        "id": task_id,
        "projectId": project_id,
        "content": today_str
    }

    url = f"https://api.ticktick.com/open/v1/task/{task_id}"
    task_title = "no name"
    
    # 执行更新请求
    response = requests.post(url, json=payload, headers=headers)
    
    # 获取标题以美化日志
    try:
        url_info = f"https://api.ticktick.com/open/v1/project/{project_id}/task/{task_id}"
        resp_info = requests.get(url_info, headers=headers)
        resp_info.raise_for_status()
        task_title = resp_info.json().get("title", "no name")
    except Exception:
        logging.error(f"fail to obtain title of task[{task_id}]")
    
    if response.status_code == 200:
        logging.info(f"from {config['NAME']}[{task_title}]: task[{task_id}] task_clear finished")
    else:
        logging.error(f"from {config['NAME']}[{task_title}]: task[{task_id}] task_clear error, code: {response.status_code}")

def clean_list(task_id, project_id, token, task_name):
    print(f"clean_list start for: {task_id}")
    
    with open("tasks_setting.json", "r") as f:
        local_t_setting = json.load(f)

    with open("clean_list.json", "r") as f:
        clean_settings = json.load(f)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # --- 【关键修复：将变量定义提前，确保 else 分支也能访问】 ---
    last_idx = clean_settings.get("last_group", 0)
    name_list = clean_settings.get("name_list", [])
    time_str = datetime.now().strftime("%m-%d")
    url_c = "https://api.ticktick.com/open/v1/task"
    url_u = f"https://api.ticktick.com/open/v1/task/{task_id}"

    is_accessible = True
    try:
        url_r = f"https://api.ticktick.com/open/v1/project/{project_id}/task/{task_id}"
        res = requests.get(url_r, headers=headers)
        res.raise_for_status()
        t_data = res.json()
        task_status = t_data.get("status")
        task_title = t_data.get("title")
    except Exception:
        is_accessible = False
        task_title, task_status = "no name", 0
        logging.error(f"fail to access task[{task_id}]")

    if is_accessible:
        if task_status == 2: # 已完成，需要创建明天的
            logging.info(f"from {config['NAME']}[{task_title}]: last mission done, creating new one")
            
            if task_config.get("roomweek") == "False":
                curr_idx = (last_idx + 1) if (last_idx + 1) <= len(name_list) else (last_idx + 1 - 7)
                content_str = name_list[curr_idx-1]
            else:
                idx0 = (last_idx + 1) if (last_idx + 1) <= len(name_list) else (last_idx + 1 - 7)
                idx1 = (idx0 + 1) if (idx0 + 1) <= len(name_list) else (idx0 + 1 - 7)
                content_str = f"教室：{name_list[idx0-1]}\nRoom:{name_list[idx1-1]}"
                curr_idx = idx1

            payload = {
                "title": f"{time_str}值日",
                "content": content_str,
                "projectId": project_id,
                "priority": 3
            }

            try:
                post_res = requests.post(url_c, json=payload, headers=headers)
                post_res.raise_for_status()
                new_data = post_res.json()
                
                local_t_setting["tasks_list"][task_name]["ID"] = new_data.get("id")
                local_t_setting["tasks_list"][task_name]["PROJECT"] = new_data.get("projectId")
                with open("tasks_setting.json", "w") as f:
                    json.dump(local_t_setting, f, indent=4)
                
                clean_settings["last_group"] = curr_idx
                with open("clean_list.json", "w") as f:
                    json.dump(clean_settings, f, indent=4)
                # 引号兼容性修正
                logging.info(f"create new task[{new_data.get('id')}][{new_data.get('title')}] successfully")
            except Exception as e:
                logging.error(f"fail to create task: {str(e)}")
        else:
            # 未完成则只更新标题
            update_payload = {"title": f"{time_str}值日"}
            requests.post(url_u, json=update_payload, headers=headers)
            logging.info(f"from {config['NAME']}: task[{task_id}][{task_title}] title updated")
    
    else: # 找不到原任务，触发新建逻辑
        # 这里现在可以正常访问 last_idx 和 name_list 了
        logging.error(f"Task {task_id} not found, logic for creating new task triggered")
        if task_config.get("roomweek") == "False":
            curr_idx = (last_idx + 1) if (last_idx + 1) <= len(name_list) else (last_idx + 1 - 7)
            content_str = name_list[curr_idx-1]
        else:
            idx0 = (last_idx + 1) if (last_idx + 1) <= len(name_list) else (last_idx + 1 - 7)
            idx1 = (idx0 + 1) if (idx0 + 1) <= len(name_list) else (idx0 + 1 - 7)
            content_str = f"教室：{name_list[idx0-1]}\nRoom:{name_list[idx1-1]}"
            curr_idx = idx1

        payload = {
            "title": f"{time_str}值日",
            "content": content_str,
            "projectId": project_id,
            "priority": 3
        }

        try:
            post_res = requests.post(url_c, json=payload, headers=headers)
            post_res.raise_for_status()
            new_data = post_res.json()
            
            local_t_setting["tasks_list"][task_name]["ID"] = new_data.get("id")
            local_t_setting["tasks_list"][task_name]["PROJECT"] = new_data.get("projectId")
            with open("tasks_setting.json", "w") as f:
                json.dump(local_t_setting, f, indent=4)
            
            clean_settings["last_group"] = curr_idx
            with open("clean_list.json", "w") as f:
                json.dump(clean_settings, f, indent=4)
            logging.info(f"create new task[{new_data.get('id')}][{new_data.get('title')}] successfully")
        except Exception as e:
            logging.error(f"fail to create task: {str(e)}")
# --- 主执行流程 ---

# 重新读取最新的配置执行任务 (list -> main_setting)
with open("tasks_setting.json", "r") as f:
    main_setting = json.load(f)

for t_name in main_setting.get("clear_tasks_list", []):
    task_info = main_setting["tasks_list"][t_name]
    if task_info["ID"] != " ":
        task_clear(task_info["ID"], task_info["PROJECT"], ACCESS_TOKEN)

for t_name in main_setting.get("clean_tasks_list", []):
    task_info = main_setting["tasks_list"][t_name]
    if task_info["ID"] != " ":
        clean_list(task_info["ID"], task_info["PROJECT"], ACCESS_TOKEN, t_name)

# 4. 日志大小检测 (list -> final_setting)
with open("tasks_setting.json", "r") as f:
    final_setting = json.load(f)

log_path = final_setting.get("log_location")
if log_path and os.path.exists(log_path):
    if os.path.getsize(log_path) >= 5242880: # 5MB
        now_date = datetime.now().strftime("%Y-%m-%d")
        # 修正原代码拼写错误 log_loacton -> log_location
        final_setting["log_location"] = f"log/ticktick_task_{now_date}.log"
        with open("tasks_setting.json", "w") as f:
            json.dump(final_setting, f, indent=4)