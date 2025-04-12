from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg
from django.db.models import Count, Sum
import json
import pandas as pd
import plotly.express as px
import csv
from datetime import datetime, timedelta
from .models import InventoryItem, Location, Supplier
from sklearn.linear_model import LinearRegression
import numpy as np

# Placeholder anomaly detection
def detect_anomalies(items):
    return [item for item in items if item.quantity > 100]

# Dashboard Views
@login_required
def dashboard_view(request):
    suppliers = Supplier.objects.filter(user=request.user).distinct()
    locations = Location.objects.filter(user=request.user).distinct()
    location_filter = request.GET.get('location', '')
    return render(request, 'dashboard.html', {
        'suppliers': suppliers,
        'locations': locations,
        'location_filter': location_filter
    })

@login_required
def get_dashboard_data_api(request):
    location_filter = request.GET.get('location', '')
    items = InventoryItem.objects.filter(user=request.user)
    if location_filter:
        items = items.filter(location__name=location_filter)
    
    total_items = items.count()
    total_value = items.aggregate(Sum('price'))['price__sum'] or 0
    stock_data = items.values('name').annotate(total=Sum('quantity')).order_by('-total')
    location_data = items.values('location__name').annotate(total=Sum('quantity'))
    supplier_data = items.values('supplier__name').annotate(total=Sum('quantity'))
    
    stock_chart = px.bar(stock_data, x='name', y='total', title='Stock Levels')
    location_chart = px.pie(location_data, names='location__name', values='total', title='Stock by Location')
    supplier_chart = px.bar(supplier_data, x='supplier__name', y='total', title='Supplier Performance')
    
    # Item list for table
    item_list = [
        {
            'id': item.id,
            'name': item.name,
            'quantity': item.quantity,
            'price': float(item.price),
            'supplier': item.supplier.name if item.supplier else 'N/A',
            'location': item.location.name if item.location else 'N/A'
        } for item in items
    ]
    
    return JsonResponse({
        'total_items': total_items,
        'total_value': total_value,
        'stock_chart_data': stock_chart.to_json(),
        'location_chart_data': location_chart.to_json(),
        'supplier_chart_data': supplier_chart.to_json(),
        'items': item_list
    })

@login_required
def add_item_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        location, _ = Location.objects.get_or_create(
            name=data['location'],
            defaults={'user': request.user}
        )
        supplier, _ = Supplier.objects.get_or_create(
            name=data['supplier'],
            defaults={'user': request.user}
        )
        item = InventoryItem(
            user=request.user,
            name=data['name'],
            quantity=data['quantity'],
            price=data['price'],
            supplier=supplier,
            location=location
        )
        item.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

# Locations Views
@login_required
def locations_view(request):
    locations = Location.objects.filter(user=request.user).annotate(
        item_count=Count('inventoryitem'),
        total_stock=Sum('inventoryitem__quantity')
    )
    for location in locations:
        items = InventoryItem.objects.filter(location=location)
        location.items_list = [{'name': item.name, 'quantity': item.quantity} for item in items]
    return render(request, 'locations.html', {'locations': locations})

@login_required
def add_location_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        if not name:
            return JsonResponse({'status': 'error', 'message': 'Location name is required'}, status=400)
        location, created = Location.objects.get_or_create(
            name=name,
            defaults={'user': request.user}
        )
        if not created:
            return JsonResponse({'status': 'error', 'message': 'Location already exists'}, status=400)
        return JsonResponse({'status': 'success', 'location': {'id': location.id, 'name': location.name}})

@login_required
def edit_location(request, location_id):
    location = Location.objects.get(id=location_id, user=request.user)
    if request.method == 'POST':
        data = json.loads(request.body)
        location.name = data['name']
        location.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def delete_location(request, location_id):
    location = Location.objects.get(id=location_id, user=request.user)
    if request.method == 'POST':
        location.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

# Suppliers Views
@login_required
def suppliers_view(request):
    suppliers = Supplier.objects.filter(user=request.user).annotate(
        item_count=Count('inventoryitem'),
        total_stock=Sum('inventoryitem__quantity')
    )
    return render(request, 'suppliers.html', {'suppliers': suppliers})

@login_required
def add_supplier_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        if not name:
            return JsonResponse({'status': 'error', 'message': 'Supplier name is required'}, status=400)
        supplier, created = Supplier.objects.get_or_create(
            name=name,
            defaults={'user': request.user}
        )
        if not created:
            return JsonResponse({'status': 'error', 'message': 'Supplier already exists'}, status=400)
        return JsonResponse({'status': 'success', 'supplier': {'id': supplier.id, 'name': supplier.name}})

@login_required
def edit_supplier(request, supplier_id):
    supplier = Supplier.objects.get(id=supplier_id, user=request.user)
    if request.method == 'POST':
        data = json.loads(request.body)
        supplier.name = data['name']
        supplier.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def delete_supplier(request, supplier_id):
    supplier = Supplier.objects.get(id=supplier_id, user=request.user)
    if request.method == 'POST':
        supplier.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

# Insights View (simplified for now)
@login_required
def insights_view(request):
    items = InventoryItem.objects.filter(user=request.user)
    
    # Demand Forecast: Quantity over time
    df = pd.DataFrame(list(items.values('name', 'quantity', 'created_at')))
    if not df.empty:
        df['created_at'] = pd.to_datetime(df['created_at'])
        df = df.groupby(['name', pd.Grouper(key='created_at', freq='M')])['quantity'].sum().reset_index()
        forecast_fig = px.line(df, x='created_at', y='quantity', color='name', title='Demand Forecast')
    else:
        mock_dates = pd.date_range(start='2025-01-01', periods=3, freq='M')
        mock_df = pd.DataFrame({'created_at': mock_dates, 'quantity': [10, 20, 30], 'name': ['Mock Item'] * 3})
        forecast_fig = px.line(mock_df, x='created_at', y='quantity', color='name', title='Demand Forecast (No Data)')

    # Anomalies Detected: Quantity > 100
    anomalies = [item for item in items if item.quantity > 100]
    anomalies_df = pd.DataFrame([{'name': item.name, 'quantity': item.quantity} for item in anomalies])
    if not anomalies_df.empty:
        anomalies_fig = px.bar(anomalies_df, x='name', y='quantity', title='Anomalies Detected')
    else:
        anomalies_fig = px.bar(x=['None'], y=[0], title='Anomalies Detected (None Yet)')

    # Stock Trends: Stock levels by item
    stock_data = items.values('name').annotate(total=Sum('quantity')).order_by('-total')
    stock_fig = px.bar(stock_data, x='name', y='total', title='Stock Trends')

    low_stock = [item for item in items if item.quantity < 10]
    low_stock_list = [{'name': item.name, 'quantity': item.quantity, 'location': item.location.name if item.location else 'N/A'} for item in low_stock]
    restock_suggestions = [{'name': item.name, 'suggested_quantity': max(100 - item.quantity, 0)} for item in items if item.quantity < 50]

    return render(request, 'insights.html', {
        'forecast_chart_data': forecast_fig.to_json(),
        'anomalies_chart_data': anomalies_fig.to_json(),
        'stock_trend_data': stock_fig.to_json(),
        'low_stock': low_stock_list,
        'restock_suggestions': restock_suggestions
    })

@login_required
def delete_item_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item = InventoryItem.objects.get(id=data['id'], user=request.user)
        item.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_item_api(request, id):
    item = InventoryItem.objects.get(id=id, user=request.user)
    return JsonResponse({
        'name': item.name,
        'quantity': item.quantity,
        'price': float(item.price),
        'supplier': item.supplier.name if item.supplier else '',
        'location': item.location.name if item.location else ''
    })

@login_required
def edit_item_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item = InventoryItem.objects.get(id=data['id'], user=request.user)
        location, _ = Location.objects.get_or_create(name=data['location'], defaults={'user': request.user})
        supplier, _ = Supplier.objects.get_or_create(name=data['supplier'], defaults={'user': request.user})
        item.name = data['name']
        item.quantity = data['quantity']
        item.price = data['price']
        item.location = location
        item.supplier = supplier
        item.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def export_inventory(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Quantity', 'Price', 'Supplier', 'Location'])
    for item in InventoryItem.objects.filter(user=request.user):
        writer.writerow([item.name, item.quantity, item.price, item.supplier.name if item.supplier else 'N/A', item.location.name if item.location else 'N/A'])
    return response