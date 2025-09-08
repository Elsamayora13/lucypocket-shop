from django.shortcuts import render

# Create your views here.
def show_main(request):
    context = {
        'app_name': 'Lucy Pocket',
        'name': 'Elsa Mayora Sidabutar',
        'class': 'PBP A'
    }

    return render(request, "main.html", context)
