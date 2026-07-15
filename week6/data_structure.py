# 115/07/13 本週主要在講資料結構

# 資料結構：要怎樣儲存資料

# 方法一、放到 陣列 / 列表
# [5, 8, 6, 7, 2, 3, 5]

# 方法二、二元搜尋樹的方式放資料：維護節點右邊資料一定比跟節點大，左邊的資料一定比跟節點小

'''
              5 

   2                       8

         3          6

                         7

'''

# 驗證效能方式：
# 隨機新增 1000000 萬筆資料到結構中
# 搜尋其中一個資料是否存在

import random 
import time 

print("====================陣列====================")

start = time.time()
data = []
for i in range(10000000):
    data.append(random.randint(1, 100000000))
print("陣列新增資料花費時間：", time.time() - start)

def search(value):
    return value in data

start = time.time()
print(search(50000))
print("陣列搜尋資料花費時間：", time.time() - start)

print("====================二元搜尋樹====================") 

class BST():
    def __init__(self):
        self.root = None
    def add(self, value):
        if self.root == None:
            self.root = {"left": None, "right": None, "value": value}
        else:
            node = self.root
            while True:
                if value > node["value"]:
                    if node["right"] == None:
                        node["right"] = {"left": None, "right": None, "value": value}
                        break
                    else:
                        node = node["right"]
                else:
                    if node["left"] == None:
                        node["left"] = {"left": None, "right": None, "value": value}
                        break
                    else:
                        node = node["left"]
    def search(self, value):
        if self.root == None:
            return False
        node = self.root
        while node != None:
            if value == node["value"]:
                return True
            elif value > node["value"]:
                node = node["right"]
            else:
                node = node["left"]
        return False   



start = time.time()
bst = BST()
for i in range(10000000):
    bst.add(random.randint(1, 100000000))
print("二元搜尋樹新增資料花費時間：", time.time() - start)

def search(value):
    return value in data
start = time.time()
print(bst.search(50000))
print("二元搜尋樹搜尋資料花費時間：", time.time() - start)

"""
通常『讀取』資料比起寫入與新增，為使用的大宗 所以增加讀取效能重要。
二元搜尋樹，就是把資料建立為一個結構（樹狀結構），基本上就是做索引的概念！
代價就是建立樹狀結構比較花時間，但可以加速搜尋速度。
但，要是樹很不平衡 那基本上搜尋效能，比較沒有差別 
"""

"""
細品一下～
原本100筆資料，最多需要找100次，建立索引後，2的七次方 只要找7次。
"""