from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import math

app = FastAPI()

# --- 1. 模拟数据库 (坐标建议从高德拾取器获取后替换) ---
# 格式: {"id": {"name": 名称, "location": [经度, 纬度], "audio": 语音地址}}
CAMPUS_DATA = {
    "CB": {"name": "中心楼", "loc": [120.737, 31.273], "audio": "cb.mp3"},
    "SA": {"name": "理学院A", "loc": [120.738, 31.272], "audio": "sa.mp3"},
    "FB": {"name": "基础楼", "loc": [120.736, 31.275], "audio": "fb.mp3"},
    "GYM": {"name": "体育馆", "loc": [120.741, 31.268], "audio": "gym.mp3"}
}

class NavRequest(BaseModel):
    user_lon: float
    user_lat: float
    unvisited_ids: List[str]

# --- 2. 核心算法：简单距离计算 ---
def get_dist(p1, p2):
    # 简化版欧几里得距离，用于校园内点位排序足够了
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

# --- 3. 路由接口 ---
@app.get("/buildings")
async def get_buildings():
    return CAMPUS_DATA

@app.post("/plan")
async def plan_route(req: NavRequest):
    """AI 路径规划：贪心算法返回游览顺序"""
    curr_loc = [req.user_lon, req.user_lat]
    remaining = req.unvisited_ids.copy()
    route = []

    while remaining:
        # 寻找距离当前位置最近的点
        nearest_id = min(remaining, key=lambda x: get_dist(curr_loc, CAMPUS_DATA[x]["loc"]))
        route.append({
            "id": nearest_id,
            "name": CAMPUS_DATA[nearest_id]["name"],
            "loc": CAMPUS_DATA[nearest_id]["loc"]
        })
        # 更新当前位置为该建筑，继续找下一个最近的点
        curr_loc = CAMPUS_DATA[nearest_id]["loc"]
        remaining.remove(nearest_id)
    
    return {"planned_sequence": route}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)