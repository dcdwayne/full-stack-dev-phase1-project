# -- Task 1 --
locations = {
    "悟空": {"x": 0, "y": 0, "group": 0},      # 0 代表左下側陣營
    "辛巴": {"x": -3, "y": 3, "group": 0},
    "貝吉塔": {"x": -4, "y": -1, "group": 0},
    "特南克斯": {"x": 1, "y": -2, "group": 0},
    "丁滿": {"x": -1, "y": 4, "group": 1},     # 1 代表右上側陣營
    "弗利沙": {"x": 4, "y": -1, "group": 1}
}

def func1(name):
    # 防呆處理
    if name not in locations:
        print("角色不存在")
        return
    
    # 以帶入角色為基準，去算其他角色的距離
    target_group = locations[name]["group"]
    distances = {}

    for other_name, other_info in locations.items():
        if other_name == name:
            continue

        # 判定是否同陣營
        if other_info["group"] == target_group:
            distance = abs((other_info["x"] - locations[name]["x"])) + abs((other_info["y"] - locations[name]["y"]))

        elif other_info["group"] != target_group:
            distance = abs((other_info["x"] - locations[name]["x"])) + abs((other_info["y"] - locations[name]["y"])) + 2

        distances[other_name] = distance

    closest_characters = [char for char, dist in distances.items() if dist == min(distances.values())]
    farthest_characters = [char for char, dist in distances.items() if dist == max(distances.values())]

    # 使用 "、".join() 把串列轉成乾淨的字串
    farthest_str = "、".join(farthest_characters)
    closest_str = "、".join(closest_characters)

    print(f"與 {name} 距離最遠的角色是 {farthest_str}; 距離最近的角色是 {closest_str}")


# -- Task 2 --
services = [
    {"name": "S1", "r": 4.5, "c": 1000},
    {"name": "S2", "r": 3, "c": 1200},
    {"name": "S3", "r": 3.8, "c": 800}
]

def func2(ss, start, end, criteria):
    # 加入技師的班表
    for service in ss:
        if "schedule" not in service:
            service["schedule"] = []

    if ">=" in criteria:
        op = ">="
    elif "<=" in criteria:
        op = "<="
    elif "=" in criteria:
        op = "="
    else:
        print("條件格式錯誤")
        return
    
    # 利用拆解出來的運算子，將字串切成「欄位」與「數值」
    field, target_val_str = criteria.split(op)
    
    # 針對數值進行轉型 (如果是 name 維持字串，否則轉浮點數)
    target_val = target_val_str if field == "name" else float(target_val_str)

    best_service = None
    min_diff = float('inf')

    for service in ss:
        # 檢查時間衝突
        is_conflict = False
        for old_start, old_end in service["schedule"]:
            if start < old_end and old_start < end:
                is_conflict = True
                break
        
        if is_conflict:
            continue
        
        # 檢查條件是否匹配
        sv_val = service[field]  # 動態取得該技師對應欄位的值 (可能是 c, r 或 name)
        is_match = False
        
        if op == ">=" and sv_val >= target_val:
            is_match = True
        elif op == "<=" and sv_val <= target_val:
            is_match = True
        elif op == "=" and str(sv_val) == str(target_val):
            is_match = True

        if is_match:
            # 如果是比對 name，差值視為 0；否則計算絕對差值
            diff = 0 if field == "name" else abs(sv_val - target_val)
            
            if diff < min_diff:
                min_diff = diff
                best_service = service

    if best_service is not None:
        best_service["schedule"].append((start, end))
        print(best_service["name"])
    else:
        print("Sorry")


# -- Task 3 --
def func3(index):
    initial_num = 25
    sequence = [-2, -3, 1, 2]
    number_sequence = []

    # 根據輸入的 index 動態決定跑幾圈，保證絕對不會超出索引
    for i in range(index + 1):
        number_sequence.append(initial_num)
        initial_num += sequence[i % 4] # 用 % 4 自動循環

    print(number_sequence[index])


# -- Task 4 --
def func4(sp, stat, n):
    available_seats = []
    for i in range(len(stat)):
        if stat[i] == "0":
            available_seats.append(sp[i])
        elif stat[i] == "1":
            available_seats.append(0)

    most_fitted_car = None
    min_diff = float('inf')

    for i in range(len(available_seats)):
        diff = abs(available_seats[i] - n)
        if diff < min_diff:
            min_diff = diff
            most_fitted_car = i

    print(most_fitted_car)


if __name__ == "__main__":
    print("-- Task 1 --")
    func1("辛巴")
    func1("悟空")
    func1("弗利沙")
    func1("特南克斯")
    
    print("\n-- Task 2 --")
    func2(services, 15, 17, "c>=800")
    func2(services, 11, 13, "r<=4")
    func2(services, 10, 12, "name=S3")
    func2(services, 15, 18, "r>=4.5")
    func2(services, 16, 18, "r>=4")
    func2(services, 13, 17, "name=S1")
    func2(services, 8, 9, "c<=1500")

    print("\n-- Task 3 --")
    func3(1)
    func3(5)
    func3(10)
    func3(30)

    print("\n-- Task 4 --")
    func4([3, 1, 5, 4, 3, 2], "101000", 2)
    func4([1, 0, 5, 1, 3], "10100", 4)
    func4([4, 6, 5, 8], "1000", 4)
