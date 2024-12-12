# meetings/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Meeting, Organizer
from .forms import MeetingForm, OrganizerForm, ReportForm
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.db.models import Q
from datetime import datetime
import io
from django.db import connection

def meeting_list(request):
    meetings = Meeting.objects.prefetch_related('organizers').all()
    return render(request, 'meetings/meeting_list.html', {'meetings': meetings})

def meeting_create(request):
    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.save()
            form.save_m2m()  # Save the many-to-many relationships
            return redirect('meeting_list')
    else:
        form = MeetingForm()
    return render(request, 'meetings/meeting_form.html', {'form': form})

def meeting_edit(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.save()
            form.save_m2m()  # Save the many-to-many relationships
            return redirect('meeting_list')
    else:
        form = MeetingForm(instance=meeting)
    return render(request, 'meetings/meeting_form.html', {'form': form, 'meeting': meeting})

def meeting_delete(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        meeting.delete()
    return redirect('meeting_list')

# Organizer views
def organizer_list(request):
    organizers = Organizer.objects.all()
    return render(request, 'meetings/organizer_list.html', {'organizers': organizers})

def organizer_create(request):
    if request.method == 'POST':
        form = OrganizerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('organizer_list')
    else:
        form = OrganizerForm()
    return render(request, 'meetings/organizer_form.html', {'form': form})

def organizer_edit(request, pk):
    organizer = get_object_or_404(Organizer, pk=pk)
    if request.method == 'POST':
        form = OrganizerForm(request.POST, instance=organizer)
        if form.is_valid():
            form.save()
            return redirect('organizer_list')
    else:
        form = OrganizerForm(instance=organizer)
    return render(request, 'meetings/organizer_form.html', {'form': form, 'organizer': organizer})

def organizer_delete(request, pk):
    organizer = get_object_or_404(Organizer, pk=pk)
    if request.method == 'POST':
        organizer.delete()
    return redirect('organizer_list')

def generate_report(request):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            # Get filter parameters
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            mandatory_only = form.cleaned_data['mandatory_only']
            organizer = form.cleaned_data['organizer']
            industry_type = form.cleaned_data['industry_type']

            # Build SQL query without FORCE INDEX hints
            query = """
                SELECT DISTINCT 
                    m.title,
                    m.date,
                    m.mandatory,
                    GROUP_CONCAT(o.name) as organizers
                FROM meetings_meeting m
                LEFT JOIN meetings_meetingorganizer mo ON m.id = mo.meeting_id
                LEFT JOIN meetings_organizer o ON mo.organizer_id = o.organizer_id
                WHERE 1=1
            """
            params = []

            # Add filters using indexed columns first
            if start_date or end_date:
                if start_date:
                    query += " AND DATE(m.date) >= %s"
                    params.append(start_date)
                if end_date:
                    query += " AND DATE(m.date) <= %s"
                    params.append(end_date)

            if mandatory_only:
                query += " AND m.mandatory = 1"

            if industry_type:
                query += " AND o.industry_type = %s"
                params.append(industry_type)

            if organizer:
                query += " AND mo.organizer_id = %s"
                params.append(organizer.organizer_id)

            # Group by and order using indexed columns
            query += """
                GROUP BY m.id, m.title, m.date, m.mandatory
                ORDER BY m.date DESC, m.mandatory DESC
            """

            # Add query timing for debugging
            with connection.cursor() as cursor:
                from time import time
                start_time = time()
                cursor.execute(query, params)
                end_time = time()
                meetings = cursor.fetchall()
                query_time = end_time - start_time

            # Add query timing to the report
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            
            styles = getSampleStyleSheet()
            elements.append(Paragraph("Meetings Report", styles['Title']))
            elements.append(Spacer(1, 20))
            
            # Add query performance info
            elements.append(Paragraph(f"Query execution time: {query_time:.3f} seconds", styles['Normal']))
            elements.append(Spacer(1, 20))

            # Filter information
            filter_info = []
            if start_date:
                filter_info.append(f"Start Date: {start_date}")
            if end_date:
                filter_info.append(f"End Date: {end_date}")
            if mandatory_only:
                filter_info.append("Mandatory Meetings Only")
            if organizer:
                filter_info.append(f"Organizer: {organizer.name}")
            if industry_type:
                filter_info.append(f"Industry: {industry_type}")
            
            if filter_info:
                elements.append(Paragraph("Filters Applied:", styles['Heading2']))
                for info in filter_info:
                    elements.append(Paragraph(f"• {info}", styles['Normal']))
                elements.append(Spacer(1, 20))

            # Table data
            data = [['Title', 'Date', 'Mandatory', 'Organizers']]
            for meeting in meetings:
                data.append([
                    meeting[0],  # title
                    meeting[1].strftime("%Y-%m-%d %H:%M") if meeting[1] else '',  # date
                    "Yes" if meeting[2] else "No",  # mandatory
                    meeting[3] or ''  # organizers
                ])

            # Create table
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            doc.build(elements)
            
            buffer.seek(0)
            response = HttpResponse(
                buffer.getvalue(),
                content_type='application/pdf'
            )
            
            # Check which button was clicked
            if request.POST.get('action') == 'download':
                response['Content-Disposition'] = 'attachment; filename="meetings_report.pdf"'
            else:  # view
                response['Content-Disposition'] = 'inline; filename="meetings_report.pdf"'
            
            return response
    else:
        form = ReportForm()
    
    return render(request, 'meetings/report_form.html', {'form': form})
