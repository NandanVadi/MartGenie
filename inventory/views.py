from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def scanner_view(request):
    store_code = request.session.get('store_code', 'MARTGENIE-STORE-001') # Default for now if missing
    return render(request, 'Scanner.html', {'store_code': store_code})

@login_required
def gatepass_view(request):
    return render(request, 'GatePass.html')
