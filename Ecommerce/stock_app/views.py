from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

from rest_framework import viewsets, filters, status, throttling
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product
from .serializers import ProductSerializer
from .forms import ProductForm
from .utils import log_product_change

# ----------------------------
# Custom Permissions
# ----------------------------
class IsOwnerOrStaff(BasePermission):
    """Allow only owners or staff to modify objects."""

    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return obj.owner == request.user or request.user.is_staff


# ----------------------------
# Web Views
# ----------------------------
class ProductListView(ListView):
    model = Product
    template_name = 'stock_app/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        queryset = Product.objects.select_related('owner').all()
        search_query = self.request.GET.get('search')
        category = self.request.GET.get('category')
        sort_by = self.request.GET.get('sort', 'name')

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(category__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        if category and category != 'all':
            queryset = queryset.filter(category__iexact=category)

        valid_sort_fields = ['name', 'price', 'stock', 'created_date',
                             '-name', '-price', '-stock', '-created_date']
        if sort_by in valid_sort_fields:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', 'all')
        context['sort_by'] = self.request.GET.get('sort', 'name')
        context['categories'] = dict(Product.CATEGORY_CHOICES)  # ✅ use model choices
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'stock_app/product_form.html'
    success_url = reverse_lazy('product-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        log_product_change(form.instance, self.request.user, "created", None, form.instance.price)
        messages.success(self.request, f'Product "{form.instance.name}" was created successfully!')
        return response


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'stock_app/product_form.html'
    success_url = reverse_lazy('product-list')

    def get_object(self, queryset=None):
        obj = get_object_or_404(Product, pk=self.kwargs['pk'])
        if obj.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You don't have permission to edit this product.")
        return obj

    def form_valid(self, form):
        old_instance = Product.objects.get(pk=self.get_object().pk)
        response = super().form_valid(form)

        if old_instance.price != form.instance.price:
            log_product_change(form.instance, self.request.user, "price_changed",
                               old_instance.price, form.instance.price)

        messages.success(self.request, f'Product "{form.instance.name}" was updated successfully!')
        return response


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'stock_app/product_confirm_delete.html'
    success_url = reverse_lazy('product-list')

    def get_object(self, queryset=None):
        obj = get_object_or_404(Product, pk=self.kwargs['pk'])
        if obj.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You don't have permission to delete this product.")
        return obj

    def delete(self, request, *args, **kwargs):
        product = self.get_object()
        product_name = product.name
        log_product_change(product, request.user, "deleted", product.price, None)
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Product "{product_name}" was deleted successfully!')
        return response


# ----------------------------
# API Views (DRF)
# ----------------------------
class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrStaff]
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_available']
    search_fields = ['name', 'description', 'category']
    ordering_fields = ['price', 'created_date', 'stock']
    ordering = ['name']

    def get_queryset(self):
        queryset = Product.objects.select_related('owner').all()
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')

        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass

        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass

        if self.request.GET.get('owner_only') and self.request.user.is_authenticated:
            queryset = queryset.filter(owner=self.request.user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        log_product_change(serializer.instance, self.request.user, "created",
                           None, serializer.instance.price)

    def perform_update(self, serializer):
        instance = self.get_object()
        old_price = instance.price
        serializer.save()

        if old_price != serializer.instance.price:
            log_product_change(serializer.instance, self.request.user, "price_changed",
                               old_price, serializer.instance.price)

    def perform_destroy(self, instance):
        log_product_change(instance, self.request.user, "deleted", instance.price, None)
        instance.delete()

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Return categories from model choices (no extra query)."""
        return Response({'categories': dict(Product.CATEGORY_CHOICES)})

    @action(detail=True, methods=['post'],
            throttle_classes=[throttling.UserRateThrottle])  # ✅ Security: rate-limit
    def adjust_stock(self, request, pk=None):
        product = self.get_object()
        adjustment = request.data.get('adjustment')

        if adjustment is None:
            return Response({'error': 'Adjustment value required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            adjustment = int(adjustment)
        except ValueError:
            return Response({'error': 'Invalid adjustment value'}, status=status.HTTP_400_BAD_REQUEST)

        old_stock = product.stock
        new_stock = old_stock + adjustment

        if new_stock < 0:
            return Response({'error': 'Stock cannot be negative'}, status=status.HTTP_400_BAD_REQUEST)

        product.stock = new_stock
        product.save()

        log_product_change(product, request.user, "stock_adjusted", old_stock, new_stock)

        return Response({
            "message": "Stock updated successfully",
            "old_stock": old_stock,
            "new_stock": new_stock,
            "product": self.get_serializer(product).data
        })


# ----------------------------
# AJAX Utility View
# ----------------------------
def product_categories_ajax(request):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({'categories': dict(Product.CATEGORY_CHOICES)})
    return JsonResponse({'error': 'Invalid request'}, status=400)
