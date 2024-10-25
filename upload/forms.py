from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField(
        label='Select an Excel or CSV file',
        help_text='Max. 42 megabytes',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    def clean_file(self):
        file = self.cleaned_data.get('file', False)
        if file:
            if not file.name.endswith(('.xlsx', '.xls', '.csv')):
                raise forms.ValidationError("Unsupported file extension.")
            if file.size > 42 * 1024 * 1024:
                raise forms.ValidationError("File size exceeds 42MB.")
            return file
        else:
            raise forms.ValidationError("Couldn't read uploaded file.")

class RecipientForm(forms.Form):
    recipient_email = forms.EmailField(
        label='Recipient Email',
        help_text='Enter the email address to send the summary report.',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g., recipient@example.com'})
    )
