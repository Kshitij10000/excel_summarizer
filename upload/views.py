import pandas as pd
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .forms import UploadFileForm, RecipientForm
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            try:
                # Read file into pandas DataFrame
                if file.name.endswith('.csv'):
                    data = pd.read_csv(file)
                else:
                    data = pd.read_excel(file)
                
                # Check required columns
                if 'Cust State' not in data.columns or 'DPD' not in data.columns:
                    messages.error(request, "Uploaded file must contain 'Cust State' and 'DPD' columns.")
                    return render(request, 'upload/upload.html', {'form': form})
                
                # Convert DataFrame to JSON and store in session
                data_json = data.to_json()
                request.session['data_json'] = data_json
                
                messages.success(request, "File uploaded and processed successfully.")
                return redirect('display_data')
            except Exception as e:
                messages.error(request, f"An error occurred while processing the file: {e}")
                return render(request, 'upload/upload.html', {'form': form})
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UploadFileForm()
    
    return render(request, 'upload/upload.html', {'form': form})

def display_data(request):
    data_json = request.session.get('data_json', None)
    if not data_json:
        messages.error(request, "No data found. Please upload a file first.")
        return redirect('upload_file')
    
    # Convert JSON back to DataFrame
    data = pd.read_json(data_json)
    
    # Convert DataFrame to HTML with Bootstrap table classes
    data_html = data.to_html(index=False, classes='table table-striped table-hover')
    
    context = {
        'data_html': data_html
    }
    return render(request, 'upload/display_data.html', context)

def summarize_data(request):
    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('display_data')

    data_json = request.session.get('data_json', None)
    if not data_json:
        messages.error(request, "No data found to summarize. Please upload a file first.")
        return redirect('upload_file')
    
    # Convert JSON back to DataFrame
    data = pd.read_json(data_json)
    
    try:
        # Summarize data
        summary = data.groupby('Cust State', as_index=False)['DPD'].sum()
        
        # Convert summary to HTML and plain text with Bootstrap table classes
        summary_html = summary.to_html(index=False, classes='table table-bordered table-hover')
        summary_text = summary.to_string(index=False)
        
        # Store summary in session
        request.session['summary_text'] = summary_text
        request.session['summary_html'] = summary_html
        
        messages.success(request, "Data summarized successfully.")
        return redirect('send_email')
    except Exception as e:
        messages.error(request, f"An error occurred while summarizing the data: {e}")
        return redirect('display_data')

def send_email_view(request):
    summary_html = request.session.get('summary_html', None)
    summary_text = request.session.get('summary_text', None)
    if not summary_text or not summary_html:
        messages.error(request, "No summary found. Please summarize the data first.")
        return redirect('upload_file')
    
    if request.method == 'POST':
        form = RecipientForm(request.POST)
        if form.is_valid():
            recipient_email = form.cleaned_data['recipient_email']
            try:
                subject = 'Python Assignment - Kshitij Sarve'
                from_email = settings.EMAIL_HOST_USER
                to = [recipient_email]
                
                # Render the HTML content using a template
                html_content = render_to_string('upload/email_summary.html', {
                    'summary_html': summary_html,
                })
                
                # Create the plain text content
                summary_df = pd.read_html(summary_html)[0]  # Convert HTML table back to DataFrame
                summary_text_plain = summary_df.to_string(index=False)
                
                # Create the email
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=summary_text_plain,  # Plain text version
                    from_email=from_email,
                    to=to,
                )
                email.attach_alternative(html_content, "text/html")
                email.send(fail_silently=False)
                
                messages.success(request, "Email sent successfully!")
                # Clear session data
                request.session.pop('data_json', None)
                request.session.pop('summary_text', None)
                request.session.pop('summary_html', None)
                return redirect('send_email_success')
            except Exception as e:
                messages.error(request, f"An error occurred while sending the email: {e}")
    else:
        form = RecipientForm()
    
    context = {
        'summary_html': summary_html,
        'form': form
    }
    return render(request, 'upload/send_email.html', context)

def send_email_success(request):
    return render(request, 'upload/send_email_success.html')
