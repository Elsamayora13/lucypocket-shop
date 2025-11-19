import datetime
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import render, redirect, get_object_or_404
from main.forms import ProductForm
from main.models import Product
from django.http import HttpResponseRedirect, JsonResponse
import traceback
import requests
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import strip_tags
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import strip_tags
import json
from django.http import JsonResponse


@csrf_exempt
@require_POST
def add_product_entry_ajax(request):
    try:
        
        # Check if user is authenticated
        if not request.user.is_authenticated:
            print("❌ User not authenticated")
            return HttpResponse(b"User not authenticated", status=401)
        
        # Get and validate required fields
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        price_str = request.POST.get("price", "")
        stock_str = request.POST.get("stock", "0")
        
        print(f"Raw values - name: '{name}', desc: '{description}', price: '{price_str}'")
        
        if not name:
            print("❌ Name is empty")
            return HttpResponse(b"Product name is required", status=400)
        
        if not description:
            print("❌ Description is empty")
            return HttpResponse(b"Product description is required", status=400)
        
        if not price_str:
            print("❌ Price is empty")
            return HttpResponse(b"Product price is required", status=400)
        
        # Strip HTML tags
        name = strip_tags(name)
        description = strip_tags(description)
        
        # Parse integers safely
        try:
            price = int(price_str)
            if price < 0:
                return HttpResponse(b"Price must be positive", status=400)
        except ValueError:
            print(f"❌ Invalid price value: {price_str}")
            return HttpResponse(b"Invalid price value", status=400)
        
        try:
            stock = int(stock_str)
            if stock < 0:
                stock = 0
        except ValueError:
            print(f"⚠️ Invalid stock value: {stock_str}, using 0")
            stock = 0
        
        # Get optional fields
        category = request.POST.get("category", "other")
        thumbnail = request.POST.get("thumbnail", "").strip()
        color = request.POST.get("color", "").strip()
        is_featured = request.POST.get("is_featured") == "on"
        
      
        
        # Create product
        new_product = Product(
            name=name,
            description=description,
            category=category,
            price=price,
            stock=stock,
            thumbnail=thumbnail if thumbnail else None,
            color=color if color else None,
            is_featured=is_featured,
            user=request.user,
        )
        new_product.save()
        
       
    
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ Error in add_product_entry_ajax:")
        print(error_trace)
        return HttpResponse(f"Error: {str(e)}".encode(), status=500)


@login_required(login_url='/login')
def show_main(request):
    filter_type = request.GET.get("filter", "all")

    if filter_type == "all":
        product_list = Product.objects.all()
    else:
        product_list = Product.objects.filter(user=request.user)

    context = {
        'npm': '240123456',
        'name': request.user.username,
        'class': 'PBP A',
        'product_list': product_list,
        'last_login': request.COOKIES.get('last_login', 'Never')
    }

    return render(request, "main.html", context)

@login_required(login_url='/login')
def create_product(request):
    form = ProductForm(request.POST or None)

    if form.is_valid() and request.method == "POST":
        product_entry = form.save(commit=False)
        product_entry.user = request.user
        product_entry.save()
        return redirect('main:show_main')

    context = {
        'form': form
    }

    return render(request, "create_product.html", context)

@login_required(login_url='/login')
def show_product(request, id):
    product = get_object_or_404(Product, pk=id)

    context = {
        'product': product
    }

    return render(request, "product_detail.html", context)

def show_xml(request):
     product_list = Product.objects.all()
     xml_data = serializers.serialize("xml", product_list)
     return HttpResponse(xml_data, content_type="application/xml")

def show_json(request):
    product_list = Product.objects.all()
    data = [
        {
            "id": str(product.id),
            "name": product.name,
            "price": product.price,
            "description": product.description,
            "category": product.category,
            "thumbnail": product.thumbnail,
            "is_featured": product.is_featured,
            "stock": product.stock,
            "color": product.color,
            "user_id": product.user.id if product.user else None,
        }
        for product in product_list
    ]

    return JsonResponse(data, safe=False)

@login_required(login_url='/login')
def show_my_json(request):
    products = Product.objects.filter(user=request.user)

    data = [
        {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description,
            "category": product.category,
            "thumbnail": product.thumbnail,
            "is_featured": product.is_featured,
            "stock": product.stock,
            "color": product.color,
            "user_id": product.user.id,
        }
        for product in products
    ]

    return JsonResponse(data, safe=False)



def show_xml_by_id(request, product_id):
    try:
        product_item = Product.objects.filter(pk=product_id)
        xml_data = serializers.serialize("xml", product_item)
        return HttpResponse(xml_data, content_type="application/xml")
    except Product.DoesNotExist:
        return HttpResponse(status=404)    

def show_json_by_id(request, product_id):
    try:
        product = Product.objects.select_related('user').get(pk=product_id)
        data = {
            "id": str(product.id),
            "name": product.name,
            "price": product.price,
            "description": product.description,
            "category": product.category,
            "thumbnail": product.thumbnail,
            "is_featured": product.is_featured,
            "stock": product.stock,
            "color": product.color,
            "user_id": product.user.id if product.user_id else None,
            "user_username": product.user.username if product.user_id else None,
        }
        return JsonResponse(data)
    except Product.DoesNotExist:
        return JsonResponse({"detail": "Not found"}, status=404)
    

def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('main:login')
    context = {'form':form}
    return render(request, 'register.html', context)

def login_user(request):
   if request.method == 'POST':
      form = AuthenticationForm(data=request.POST)

      if form.is_valid():
        user = form.get_user()
        login(request, user)
        response = HttpResponseRedirect(reverse("main:show_main"))
        response.set_cookie('last_login', str(datetime.datetime.now()))
        return response

   else:
      form = AuthenticationForm(request)
   context = {'form': form}
   return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('last_login')
    return response

def edit_product(request, id):
    product = get_object_or_404(Product, pk=id)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid() and request.method == 'POST':
        form.save()
        return redirect('main:show_main')

    context = {
        'form': form
    }

    return render(request, "edit_product.html", context)


def delete_product(request, id):
    product = get_object_or_404(Product, pk=id)
    product.delete()
    return HttpResponseRedirect(reverse('main:show_main'))

def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse('No URL provided', status=400)
    
    try:
        # Fetch image from external source
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Return the image with proper content type
        return HttpResponse(
            response.content,
            content_type=response.headers.get('Content-Type', 'image/jpeg')
        )
    except requests.RequestException as e:
        return HttpResponse(f'Error fetching image: {str(e)}', status=500)
    
@csrf_exempt
def create_product_flutter(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Ambil data sesuai dengan field Product
            name = strip_tags(data.get("name", ""))
            description = strip_tags(data.get("description", ""))
            price = int(data.get("price", 0))
            stock = int(data.get("stock", 0))
            category = data.get("category", "other")
            thumbnail = data.get("thumbnail", "")
            color = data.get("color", "")
            is_featured = data.get("is_featured", False)
            user = request.user
            
            # Validasi data required
            if not name or not description or price <= 0:
                return JsonResponse({
                    "status": "error",
                    "message": "Name, description, and valid price are required"
                }, status=400)
            
            # Create product
            new_product = Product(
                name=name,
                description=description,
                price=price,
                stock=stock,
                category=category,
                thumbnail=thumbnail if thumbnail else None,
                color=color if color else None,
                is_featured=is_featured,
                user=user
            )
            new_product.save()
            
            return JsonResponse({"status": "success"}, status=200)
            
        except (ValueError, KeyError) as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=400)
    else:
        return JsonResponse({"status": "error"}, status=405)