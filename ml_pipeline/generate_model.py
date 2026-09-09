import os
import pickle
import random
from sklearn.ensemble import RandomForestRegressor

random.seed(2026)
X = []
y = []

for _ in range(1000):
    acc = random.uniform(40.0, 100.0)
    rt = random.uniform(1200.0, 8000.0)
    comp = random.uniform(50.0, 100.0)
    cons = random.uniform(50.0, 100.0)
    mem = max(0.0, min(100.0, acc + random.uniform(-10.0, 10.0)))
    
    speed_score = max(0.0, min(100.0, 100.0 * (8000.0 - rt) / (8000.0 - 1500.0)))
    cps = acc * 0.30 + speed_score * 0.20 + comp * 0.20 + cons * 0.15 + mem * 0.15
    
    X.append([acc, rt, comp, cons, mem])
    y.append(cps)

rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
rf.fit(X, y)

os.makedirs("ml_pipeline/models", exist_ok=True)
model_path = "ml_pipeline/models/cps_random_forest.pkl"
with open(model_path, "wb") as f:
    pickle.dump(rf, f)

print(f"Model generated successfully: {model_path}, size: {os.path.getsize(model_path)} bytes")
