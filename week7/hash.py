import hashlib

# 雜湊：正推很快，反推很難。
# 可以輕易地從 A 推論出 B ;
# 但是很難從 B 推論回來 ;
# 而且 A 與 B 的關聯性無法被得知。

# result = x ^ 3
m = hashlib.sha256()
m.update("Nobody inspects".encode("utf-8"))
key = m.hexdigest()
print(key)

# 相同的 A 可以取得 相同的 B
# 用這個關鍵特性 製造key

# 可以單純用email 來製造key，但是只用email會有安全性問題，因為email是公開的資訊，容易被猜測或取得。
# 所以我們可以加入一個獨一無二的identifier，來增加key的安全
# 所以說要如何符合需求呢？？只要能夠辨認出使用者的唯一性就可以了，像是使用者的id、手機號碼、email等等，只要能夠辨認出使用者的唯一性就可以了。

# JWT就是這個東西的再包裝