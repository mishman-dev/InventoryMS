from django.shortcuts import render
from django.db.models import F
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import Item, Category
import random, string
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from datetime import datetime
from .models import Issue, Employee, Project, Item, IssueItem
from django.utils import timezone


def issue_list(request):
    issues = Issue.objects.all().order_by('-issue_date', '-id')
    today_issues = issues.filter(issue_date=datetime.today().date()).count()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        issues = issues.filter(
            Q(utilize_no__icontains=search_query) |
            Q(issued_to__first_name__icontains=search_query) |
            Q(issued_to__last_name__icontains=search_query) |
            Q(item__name__icontains=search_query) |
            Q(project__name__icontains=search_query)
        )
    
    # Filter by project
    project_filter = request.GET.get('project', '')
    if project_filter:
        issues = issues.filter(project_id=project_filter)
    
    # Filter by employee
    employee_filter = request.GET.get('employee', '')
    if employee_filter:
        issues = issues.filter(issued_to_id=employee_filter)
    
    context = {
        'issues': issues,
        'projects': Project.objects.all(),
        'employees': Employee.objects.all(),
        'search_query': search_query,
        'project_filter': project_filter,
        'employee_filter': employee_filter,
        'today_issues':today_issues,
    }
    
    return render(request, 'issues/issue_list.html', context)


def export_issues_excel(request):
    """Export issues to Excel with date range filter"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Filter issues by date range
    issues = Issue.objects.all().select_related('issued_to', 'project', 'item')
    
    if start_date:
        issues = issues.filter(issue_date__gte=start_date)
    if end_date:
        issues = issues.filter(issue_date__lte=end_date)
    
    issues = issues.order_by('-issue_date')
    
    # Create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Issues Report"
    
    # Define header style
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_alignment = Alignment(horizontal="center", vertical="center")
    
    # Add title
    ws.merge_cells('A1:H1')
    title_cell = ws['A1']
    title_cell.value = "Issues Report"
    title_cell.font = Font(bold=True, size=16)
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # Add date range info
    if start_date or end_date:
        ws.merge_cells('A2:H2')
        date_info = ws['A2']
        date_range_text = f"Period: {start_date or 'Beginning'} to {end_date or 'Present'}"
        date_info.value = date_range_text
        date_info.alignment = Alignment(horizontal="center")
    
    # Headers
    header_row = 4 if (start_date or end_date) else 3
    headers = ['Utilize No', 'Issue Date', 'Issued To', 'Project', 'Item', 'Quantity', 'Unit', 'Remarks']
    
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=header_row, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
    
    # Add data
    data_start_row = header_row + 1
    for row_num, issue in enumerate(issues, data_start_row):
        ws.cell(row=row_num, column=1, value=issue.utilize_no)
        ws.cell(row=row_num, column=2, value=issue.issue_date.strftime('%Y-%m-%d'))
        ws.cell(row=row_num, column=3, value=f"{issue.issued_to.first_name} {issue.issued_to.last_name}")
        ws.cell(row=row_num, column=4, value=issue.project.name if issue.project else 'N/A')
        ws.cell(row=row_num, column=5, value=issue.item.name)
        ws.cell(row=row_num, column=6, value=issue.quantity_issued)
        ws.cell(row=row_num, column=7, value=issue.item.unit if hasattr(issue.item, 'unit') else '')
        ws.cell(row=row_num, column=8, value=issue.remarks or '')
    
    # Adjust column widths
    column_widths = [15, 12, 20, 20, 25, 10, 10, 30]
    for col_num, width in enumerate(column_widths, 1):
        ws.column_dimensions[chr(64 + col_num)].width = width
    
    # Prepare response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"issues_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    wb.save(response)
    return response


def dashboard(request):
    items = Item.objects.select_related('category').all()
    all_items = Item.objects.all()
    categories = Category.objects.all() 
    dashboard_items = Item.objects.all()[:6]
    # Calculate statistics
    total_products = items.count()
    in_stock = items.filter(current_stock__gt=0).count()
    low_stock = items.filter(current_stock__lte=F('reorder_level'), current_stock__gt=0)
    out_of_stock = items.filter(current_stock=0)
    recent_logs = LogEntry.objects.select_related('content_type', 'user').order_by('-action_time')[:5]

    context = {
        'items': items,
        'total_products': total_products,
        'in_stock': in_stock,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'recent_logs': recent_logs,
        'activities': recent_logs,
        'all_items':all_items,
        'dashboard_items':dashboard_items,
        'categories':categories,
    }
    return render(request, 'inventory/dashboard.html', context)

def item_tab(request):
    items = Item.objects.all().order_by('name')
    items_cat = Item.objects.all().select_related('category_name')
    filter_type = request.GET.get('filter', 'all')
    search_query = request.GET.get('search', '')

    # Filter logic
    if filter_type == 'low_stock':
        items = items.filter(current_stock__lte=F('reorder_level'), current_stock__gt=0)
    elif filter_type == 'out_of_stock':
        items = items.filter(current_stock=0)
    elif filter_type == 'expired_warranty':
        items = items.filter(warrenty__lt=datetime.today().date())

    # Search logic
    if search_query:
        items = items.filter(name__icontains=search_query)

    context = {
        'items_cat': items_cat,
        'filter_type': filter_type,
        'search_query': search_query,
        'items': items,
    }
    return render(request, 'inventory/items.html', context)

def generate_item_code():
    """Generate unique item code like 'ITM-AX45G9'"""
    while True:
        code = 'CCST-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not Item.objects.filter(item_code=code).exists():
            return code


@csrf_exempt
def add_item(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            category_name = request.POST.get('category_name')
            default_unit_of_measure = request.POST.get('default_unit_of_measure')
            unit_price = request.POST.get('unit_price')
            current_stock = request.POST.get('current_stock')
            reorder_level = request.POST.get('reorder_level')

            item_code = generate_item_code()

            # 🔹 Use the correct lookup field
            category = Category.objects.get(id=category_name) if category_name else None
            # OR
            # category = Category.objects.get(category_id=category_name) if category_name else None

            item = Item.objects.create(
                item_code=item_code,
                name=name,
                category=category,
                warrenty=timezone.now().date(),
                default_unit_of_measure=default_unit_of_measure,
                unit_price=unit_price,
                current_stock=current_stock,
                reorder_level=reorder_level,
            )

            return JsonResponse({
                'success': True,
                'item': {
                    'id': item.id,
                    'item_code': item.item_code,
                    'name': item.name,
                    'category': {
                        'id': category.id if category else None,
                        'name': category.category_name if category else "N/A",
                        'display': category.get_category_name_display() if category else "N/A",
                    },
                    'unit_price': float(item.unit_price),
                    'current_stock': item.current_stock,
                    'reorder_level': item.reorder_level,
                    'warrenty': item.warrenty.strftime('%Y-%m-%d') if item.warrenty else "N/A",
                }
            })

        except Category.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid category selected'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def generate_utilize_no():
    """Generate a unique utilization number"""
    prefix = "UTZ-"
    random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"{prefix}{random_code}"



def add_issue(request):
    if request.method == 'POST':
        try:
            utilize_no = generate_utilize_no()
            issued_to_id = request.POST.get('issued_to')
            project_id = request.POST.get('project')
            remarks = request.POST.get('remarks', '')

            items = request.POST.getlist('items[]')
            quantities = request.POST.getlist('quantities[]')

            # Validate foreign keys
            issued_to = Employee.objects.get(id=issued_to_id)
            project = Project.objects.get(id=project_id) if project_id else None

            # Create the main Issue record
            issue = Issue.objects.create(
                utilize_no=utilize_no,
                issued_to=issued_to,
                project=project,
                remarks=remarks,
                issue_date=timezone.now().date()
            )

            # Create individual IssueItems
            for i in range(len(items)):
                item_obj = Item.objects.get(id=items[i])
                qty = int(quantities[i])
                IssueItem.objects.create(issue=issue, item=item_obj, quantity_issued=qty)

            return JsonResponse({
                'success': True,
                'issue': {
                    'id': issue.id,
                    'utilize_no': issue.utilize_no,
                    'issued_to': issued_to.first_name,
                    'project': project.name if project else "N/A",
                    'issue_date': issue.issue_date.strftime('%Y-%m-%d'),
                    'remarks': issue.remarks or "N/A",
                    'items': [
                        {
                            'item': Item.objects.get(id=items[i]).name,
                            'quantity_issued': quantities[i]
                        } for i in range(len(items))
                    ]
                }
            })

        except (Item.DoesNotExist, Employee.DoesNotExist, Project.DoesNotExist) as e:
            return JsonResponse({'success': False, 'error': str(e)})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})