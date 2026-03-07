"""
Cleanly rebuilds profile.html by:
1. Reading current file
2. Replacing everything from line 64 ({% if orders %}) to line 170 ({% endif %}) 
   with a clean, correct version that has no split template tags
"""

with open('templates/accounts/profile.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with {% if orders %} and the line just after {% endif %}
start_line = None
end_line = None
for i, line in enumerate(lines):
    if '{% if orders %}' in line and start_line is None:
        start_line = i
    if start_line and '</main>' in line:
        end_line = i
        break

print(f"Replacing lines {start_line+1} to {end_line+1}")

CLEAN_ORDERS_SECTION = """            {% if orders %}
            <div class="space-y-3">
                {% for order in orders %}
                <div class="bg-white p-4 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                    <div class="flex items-center justify-between mb-2">
                        <span class="font-mono text-xs font-bold bg-slate-100 px-2 py-1 rounded text-slate-600">{{ order.order_id }}</span>
                        <span class="text-xs text-slate-400">{{ order.created_at|date:"d M, h:i A" }}</span>
                    </div>
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <span class="w-2 h-2 rounded-full {% if order.status == 'COMPLETED' %}bg-emerald-500{% else %}bg-amber-500{% endif %}"></span>
                            <span class="text-sm font-medium text-slate-700">{{ order.store.name|default:"Unknown Store" }}</span>
                        </div>
                        <div class="flex items-center gap-3">
                            <span class="font-bold text-emerald-600">Rs {{ order.total_amount }}</span>
                        </div>
                    </div>

                    <!-- Actions -->
                    <div class="mt-4 pt-3 border-t border-slate-50 flex gap-2">
                        <button onclick="openReceipt('{{ order.order_id }}', '{{ order.qr_data|escapejs }}')"
                            class="flex-1 text-xs font-semibold text-emerald-600 bg-emerald-50 py-2 rounded-lg hover:bg-emerald-100 transition-colors flex items-center justify-center gap-2">
                            <i data-lucide="receipt" class="w-4 h-4"></i> View Bill
                        </button>
                    </div>

                    <!-- Hidden Receipt Data -->
                    <div id="receipt-data-{{ order.order_id }}" class="hidden">
                        <div style="background:#fff;padding:24px;max-width:360px;font-family:'Segoe UI',sans-serif;" id="printable-area-{{ order.order_id }}">
                            <div style="text-align:center;border-bottom:2px dashed #e2e8f0;padding-bottom:16px;margin-bottom:16px;">
                                <div style="width:48px;height:48px;background:linear-gradient(135deg,#10b981,#0d9488);border-radius:12px;display:inline-flex;align-items:center;justify-content:center;margin-bottom:8px;">
                                    <span style="color:white;font-size:20px;font-weight:bold;">M</span>
                                </div>
                                <p style="font-size:20px;font-weight:800;color:#0f172a;margin:0;">MartGenie</p>
                                <p style="font-size:12px;color:#64748b;margin:4px 0 0;">{{ order.store.name|default:"Store" }}</p>
                                <p style="font-size:11px;color:#94a3b8;margin:2px 0 0;">{{ order.created_at|date:"d M Y, h:i A" }}</p>
                            </div>
                            <div style="margin-bottom:16px;">
                                {% for item in order.items.all %}
                                <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #f1f5f9;">
                                    <span style="font-size:13px;color:#334155;">{{ item.product_name }} <span style="color:#94a3b8;font-size:11px;">x{{ item.quantity }}</span></span>
                                    <span style="font-size:13px;font-weight:600;color:#0f172a;">Rs {{ item.price }}</span>
                                </div>
                                {% endfor %}
                            </div>
                            <div style="background:#f0fdf4;border-radius:12px;padding:12px 16px;margin-bottom:16px;">
                                <div style="display:flex;justify-content:space-between;align-items:center;">
                                    <span style="font-size:14px;font-weight:700;color:#0f172a;">Total</span>
                                    <span style="font-size:18px;font-weight:800;color:#059669;">Rs {{ order.total_amount }}</span>
                                </div>
                                <div style="display:flex;justify-content:space-between;margin-top:4px;">
                                    <span style="font-size:10px;color:#64748b;">Order ID</span>
                                    <span style="font-size:10px;font-family:monospace;color:#64748b;">{{ order.order_id }}</span>
                                </div>
                            </div>
                            <div style="text-align:center;">
                                <div class="receipt-qr" style="display:inline-block;padding:8px;background:#fff;border:1px solid #e2e8f0;border-radius:8px;"></div>
                                <p style="font-size:9px;color:#94a3b8;margin-top:4px;text-transform:uppercase;letter-spacing:0.1em;">Scan at Exit Gate</p>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% else %}
            <div class="text-center py-10 bg-white rounded-2xl border border-slate-100 border-dashed">
                <div class="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-3">
                    <i data-lucide="shopping-bag" class="w-8 h-8 text-slate-300"></i>
                </div>
                <p class="text-slate-500 font-medium">No orders yet</p>
                <a href="{% url 'scanner' %}" class="inline-block mt-4 text-emerald-600 font-semibold text-sm hover:underline">Start Shopping</a>
            </div>
            {% endif %}
        </div>
    </main>
"""

new_lines = lines[:start_line] + [CLEAN_ORDERS_SECTION] + lines[end_line+1:]

with open('templates/accounts/profile.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

# Verify
with open('templates/accounts/profile.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
splits = re.findall(r'\{\{[^}]*\n', content)
if splits:
    print(f"WARNING: Still {len(splits)} split tags remain!")
    for s in splits:
        print(f"  {repr(s[:80])}")
else:
    print("SUCCESS: No split template tags remain!")
    print(f"Total lines: {len(content.splitlines())}")
