from flask import Flask, render_template, request, jsonify
from config import Config
import requests
from datetime import datetime, timedelta
import json
import logging
import time
import traceback

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# 飞书API相关配置
FEISHU_HOST = "https://open.feishu.cn/open-apis"
TOKEN_URL = f"{FEISHU_HOST}/auth/v3/tenant_access_token/internal"
BITABLE_URL = f"{FEISHU_HOST}/bitable/v1"
WIKI_URL = f"{FEISHU_HOST}/wiki/v2"

# 晚间问候表格配置
GREETING_TABLE_ID = app.config['GREETING_TABLE_ID']

# 获取飞书访问令牌
def get_tenant_access_token():
    logger.info("开始获取飞书访问令牌")
    start_time = time.time()
    try:
        payload = {
            "app_id": app.config['FEISHU_APP_ID'],
            "app_secret": app.config['FEISHU_APP_SECRET']
        }
        logger.debug(f"请求参数: app_id={app.config['FEISHU_APP_ID']}")
        response = requests.post(TOKEN_URL, json=payload)
        response.raise_for_status()
        token = response.json()["tenant_access_token"]
        logger.info(f"成功获取访问令牌，耗时: {time.time() - start_time:.2f}秒")
        return token
    except Exception as e:
        logger.error(f"获取访问令牌失败: {str(e)}\n{traceback.format_exc()}")
        raise

# 获取实际的BASE_ID
def get_base_id():
    logger.info("开始获取BASE_ID")
    start_time = time.time()
    base_id = app.config['BASE_ID']
    logger.debug(f"配置的BASE_ID: {base_id}")

    if not base_id or base_id.lower() == 'wiki':
        logger.info('BASE_ID为空或设置为"wiki"，尝试从API获取...')
        try:
            token = get_tenant_access_token()
            if not token:
                logger.error('获取访问令牌失败')
                return None

            url = f"{WIKI_URL}/spaces/get_node"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            params = {
                "token": app.config['WIKI_BASE'],
                "obj_type": "wiki"
            }
            logger.debug(f"API请求参数: {params}")

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            logger.debug(f"API响应: {data}")

            if data.get('code') == 0 and data.get('data', {}).get('node', {}).get('obj_token'):
                base_id = data['data']['node']['obj_token']
                logger.info(f"成功从API获取BASE_ID: {base_id}，耗时: {time.time() - start_time:.2f}秒")
                return base_id
            logger.error(f"API响应中未找到有效的BASE_ID: {data}")
            return None
        except Exception as e:
            logger.error(f"获取BASE_ID时发生错误: {str(e)}\n{traceback.format_exc()}")
            return None

    logger.info(f"使用配置的BASE_ID: {base_id}，耗时: {time.time() - start_time:.2f}秒")
    return base_id

# 获取情绪记录列表
def get_emotion_records():
    logger.info("开始获取情绪记录列表")
    start_time = time.time()
    try:
        token = get_tenant_access_token()
        base_id = get_base_id()
        if not base_id:
            raise Exception("无法获取有效的BASE_ID")

        headers = {"Authorization": f"Bearer {token}"}
        url = f"{BITABLE_URL}/apps/{base_id}/tables/{app.config['TABLE_ID']}/records"
        logger.debug(f"请求URL: {url}")

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        records = response.json()["data"]["items"]
        logger.info(f"成功获取{len(records)}条记录，耗时: {time.time() - start_time:.2f}秒")
        return records
    except Exception as e:
        logger.error(f"获取情绪记录失败: {str(e)}\n{traceback.format_exc()}")
        raise

# 添加新的情绪记录
def add_emotion_record(event):
    logger.info(f"开始添加新的情绪记录: {event}")
    start_time = time.time()
    try:
        token = get_tenant_access_token()
        base_id = get_base_id()
        if not base_id:
            raise Exception("无法获取有效的BASE_ID")

        headers = {"Authorization": f"Bearer {token}"}
        url = f"{BITABLE_URL}/apps/{base_id}/tables/{app.config['TABLE_ID']}/records"
        fields = {
            "日期": int(datetime.now().timestamp())*1000,
            "事件": event
        }
        payload = {"fields": fields}
        logger.debug(f"请求参数: {payload}")

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        logger.debug(f"响应结果: {result}")
        logger.info(f"成功添加情绪记录，耗时: {time.time() - start_time:.2f}秒")
        return result
    except Exception as e:
        logger.error(f"添加情绪记录失败: {str(e)}\n{traceback.format_exc()}")
        raise

@app.route('/')
def index():
    logger.info("访问首页")
    return render_template('index.html')

# 获取晚间问候
def get_greeting():
    logger.info("开始获取晚间问候")
    start_time = time.time()
    try:
        token = get_tenant_access_token()
        base_id = get_base_id()
        if not base_id:
            raise Exception("无法获取有效的BASE_ID")

        headers = {"Authorization": f"Bearer {token}"}
        url = f"{BITABLE_URL}/apps/{base_id}/tables/{GREETING_TABLE_ID}/records"
        logger.debug(f"请求URL: {url}")

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        records = response.json()["data"]["items"]
        logger.debug(f"响应结果: {records}")
        
        if records:
            # 按照提醒日字段逆序排序
            records.sort(key=lambda x: x["fields"].get("提醒日", 0), reverse=True)
            
            # 获取当前日期的零点时间戳（毫秒）
            current_date = datetime.now()
            current_hour = current_date.hour
            current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
            current_timestamp = int(current_date.timestamp() * 1000)
            next_day = current_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            next_day_timestamp = int(next_day.timestamp() * 1000)
            
            # 如果是早晨，需要获取前一天的记录
            if current_hour < 12:
                # 计算前一天的时间范围
                prev_day = (current_date - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                prev_day_timestamp = int(prev_day.timestamp() * 1000)
                # 查找前一天的记录
                today_record = next(
                    (record for record in records 
                     if prev_day_timestamp <= record["fields"].get("提醒日", 0) <= current_timestamp),
                    None
                )
            else:
                # 晚间问候使用当天的记录
                today_record = next(
                    (record for record in records 
                     if current_timestamp <= record["fields"].get("提醒日", 0) <= next_day_timestamp),
                    None
                )
            
            # 根据当前时间选择问候字段
            greeting_field = "早晨问候.文本化结果" if current_hour < 12 else "晚间问候.文本化结果"
            
            if today_record:
                # 使用当天的记录
                greeting_data = today_record["fields"].get(greeting_field, [])
            else:
                # 使用最新的记录
                greeting_data = records[0]["fields"].get(greeting_field, [])
            
            if greeting_data and isinstance(greeting_data, list) and len(greeting_data) > 0:
                latest_greeting = greeting_data[0].get("text", "❤️")
            else:
                latest_greeting = "❤️"
        else:
            latest_greeting = "❤️"
            
        logger.info(f"成功获取问候语，耗时: {time.time() - start_time:.2f}秒")
        return latest_greeting
    except Exception as e:
        logger.error(f"获取问候语失败: {str(e)}\n{traceback.format_exc()}")
        return "愿你心怀暖阳，充满希望"

# 获取情绪颜色数据
def get_emotion_color():
    logger.info("开始获取情绪颜色数据")
    start_time = time.time()
    try:
        token = get_tenant_access_token()
        base_id = get_base_id()
        if not base_id:
            raise Exception("无法获取有效的BASE_ID")

        headers = {"Authorization": f"Bearer {token}"}
        url = f"{BITABLE_URL}/apps/{base_id}/tables/{GREETING_TABLE_ID}/records"
        logger.debug(f"请求URL: {url}")

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        records = response.json()["data"]["items"]
        
        # 情绪颜色映射
        emotion_colors = {
            "快乐": "#FFD93D",  # 明亮的黄色
            "平静": "#4CACBC",  # 温和的蓝绿色
            "疲倦": "#95A5A6",  # 淡灰色
            "焦虑": "#E67E22",  # 橙色
            "低落": "#34495E",  # 深蓝色
            "愤怒": "#E74C3C"   # 红色
        }

        # 获取每天的情绪颜色
        daily_emotions = {}
        for record in records:
            emotion = record["fields"].get("情绪颜色")
            date = record["fields"].get("提醒日")
            if emotion and date:
                daily_emotions[date] = emotion_colors.get(emotion, "")

        logger.info(f"成功获取情绪颜色数据，耗时: {time.time() - start_time:.2f}秒")
        return daily_emotions
    except Exception as e:
        logger.error(f"获取情绪颜色数据失败: {str(e)}\n{traceback.format_exc()}")
        return {}

@app.route('/api/records', methods=['GET'])
def get_records():
    logger.info("接收获取记录请求")
    try:
        records = get_emotion_records()
        greeting = get_greeting()
        emotion_colors = get_emotion_color()
        return jsonify({"success": True, "data": records, "greeting": greeting, "emotion_colors": emotion_colors})
    except Exception as e:
        error_msg = f"获取记录失败: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        return jsonify({"success": False, "error": error_msg}), 500

@app.route('/api/records', methods=['POST'])
def create_record():
    logger.info("接收创建记录请求")
    try:
        data = request.get_json()
        logger.debug(f"请求数据: {data}")
        result = add_emotion_record(data.get('event'))
        return jsonify({"success": True, "data": result})
    except Exception as e:
        error_msg = f"创建记录失败: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        return jsonify({"success": False, "error": error_msg}), 500

@app.route('/calendar')
def calendar():
    logger.info("访问日历页面")
    return render_template('calendar.html')

if __name__ == '__main__':
    logger.info("启动应用服务器...")
    app.run(host='0.0.0.0', port=5000)