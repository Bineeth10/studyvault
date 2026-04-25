import bcrypt
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['studyvault']
users = db['users']

hashed = bcrypt.hashpw(b'bineeth@123B', bcrypt.gensalt()).decode('utf-8')
res = users.update_many(
    {'email': {'$in': ['joseph@gmail.com', 'A001@studyvault.com']}},
    {'$set': {'password': hashed, 'is_active': True, 'is_deleted': False}}
)
print("Updated count:", res.modified_count)
