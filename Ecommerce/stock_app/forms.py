from django import forms
from .models import Product, UserProfile

class ProductForm(forms.ModelForm):
    """Form for creating and updating products"""
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'stock', 'imageUrl', 'is_available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'min': '0'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError("Price must be greater than zero")
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError("Stock cannot be negative")
        return stock

class ProductSearchForm(forms.Form):
    """Form for searching products"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search products...'})
    )
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + Product.CATEGORY_CHOICES,
        required=False
    )
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Min price'})
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Max price'})
    )
    in_stock_only = forms.BooleanField(required=False)

class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information"""

    class Meta:
        model = UserProfile
        fields = ['position', 'department', 'bio', 'phone']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Enter phone number (e.g. 0700123456)',
            })
        }


    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove all non-digit characters except +
            cleaned_phone = ''.join(c for c in phone if c.isdigit() or c == '+')

            # Ensure it starts with +
            if not cleaned_phone.startswith('+'):
                cleaned_phone = '+' + cleaned_phone

            # If it starts with +0 (e.g., +0700123456), replace with +256
            if cleaned_phone.startswith('+0'):
                cleaned_phone = '+256' + cleaned_phone[2:]  # remove +0, replace with +256

            # If it just starts with 0 (like 0700123456), add +256
            elif cleaned_phone.startswith('0'):
                cleaned_phone = '+256' + cleaned_phone[1:]  # remove leading 0, add +256

            # If it doesn't already have +256 at the start, force it
            elif not cleaned_phone.startswith('+256'):
                cleaned_phone = '+256' + cleaned_phone.lstrip('+')

            return cleaned_phone
        return phone
