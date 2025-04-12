from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest
import pandas as pd
from core.models import InventoryItem

def train_demand_forecast(items):
    # Simulate historical data (in a real app, you'd have timestamps)
    df = pd.DataFrame(list(items.values('name', 'quantity')))
    if df.empty:
        return None
    
    # Group by item to predict future quantity
    df_grouped = df.groupby('name').agg({'quantity': 'mean'}).reset_index()
    X = [[i] for i in range(len(df_grouped))]  # Simple feature (index)
    y = df_grouped['quantity'].values
    
    model = LinearRegression()
    model.fit(X, y)
    return model, df_grouped['name'].tolist()

def predict_demand(model, names):
    if model is None:
        return {}
    predictions = model.predict([[i] for i in range(len(names))])
    return dict(zip(names, predictions))

def detect_anomalies(items):
    df = pd.DataFrame(list(items.values('quantity', 'price')))
    if df.empty:
        return []
    
    model = IsolationForest(contamination=0.1, random_state=42)
    df['anomaly'] = model.fit_predict(df)
    anomalies = df[df['anomaly'] == -1].index.tolist()
    return [items[i] for i in anomalies]