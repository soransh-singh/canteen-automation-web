from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from rest_framework import viewsets, permissions, status, views
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from django.http import Http404
from . import choices
from .models import Order, MenuItem, User, StudentProfile, TeacherProfile
from .serializers import (
    OrderSerializer,
    MenuItemSerializer,
    SignUpSerializer,
    LoginSerializer,
    StudentProfileSerializer,
    TeacherProfileSerializer,
)


# Create your views here.
class MenuItemList(views.APIView):
    def get(self, request):
        menu_item = MenuItem.objects.all()
        serializer = MenuItemSerializer(menu_item, many=True)
        return Response(serializer.data)


class AddMenuItem(views.APIView):
    def post(self, request):
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MenuItemDetails(views.APIView):
    def get_object(self, id):
        try:
            return MenuItem.objects.get(id=id)
        except MenuItem.DoesNotExist:
            raise Http404

    def get(self, request, *args, **kwargs):
        menu_item_id = kwargs["menu_item_id"]
        menu_item = self.get_object(id=menu_item_id)
        serializer = MenuItemSerializer(menu_item)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        menu_item_id = kwargs["menu_item_id"]
        menu_item = self.get_object(id=menu_item_id)
        serializer = MenuItemSerializer(menu_item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# FIXME: Change to ModelViewSet and add CRUD operations, with OrderItem support.
class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    # TODO: Add permissions.

    @action(detail=True, methods=["get", "post"])  # TODO: Remove get
    def accept(self, request, pk=None):
        order = self.get_object()
        order.status = choices.STATUS_DICTIONARY["Preparing"]
        order.save()
        return Response({"message": "Order accepted"})

    @action(detail=True, methods=["get", "post"])  # TODO: Remove get
    def reject(self, request, pk=None):
        order = self.get_object()
        order.status = choices.STATUS_DICTIONARY["Rejected by Canteen"]
        order.save()
        return Response({"message": "Order rejected"})

    @action(detail=False)
    def completed(self, request):
        completed_orders = Order.objects.filter(is_fulfilled=True)
        serializer = self.get_serializer(completed_orders, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def pending(self, request):
        pending_orders = Order.objects.filter(
            is_fulfilled=False, status__gte=0
        )  # Should not be fulfilled and status should be positive.
        serializer = self.get_serializer(pending_orders, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def status_options(self, request):
        return Response(choices.STATUS_DICTIONARY)

    @action(detail=True, methods=["get", "post"])
    def change_status(self, request, pk=None):
        order = self.get_object()
        data = request.data
        if "status" in data:
            if int(data["status"]) in choices.STATUS_DICTIONARY_REVERSE:
                order.status = int(data["status"])
                order.save()
                return Response(
                    {
                        "message": "Order status changed",
                        "status": choices.STATUS_DICTIONARY_REVERSE[order.status],
                    }
                )
            else:
                return Response(
                    {"error": "Status not recognised", "status": data["status"]},
                    status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"error": "Missing status in request body"}, status.HTTP_400_BAD_REQUEST
            )


class SignUp(APIView):
    serializer_class = SignUpSerializer

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            if(serializer.data.get("is_student")):
                return HttpResponseRedirect(redirect_to="/student-registration/")
            elif(serializer.data.get("is_teacher")):
                return HttpResponseRedirect(redirect_to="/student-registration/")
            else:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


class Login(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.data.get("username"),
                password=serializer.data.get("password"),
            )
            login(request, user)
            return HttpResponseRedirect(redirect_to="/menu_item/")
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


class Logout(APIView):
    def post(self, request):
        logout(request)
        return HttpResponseRedirect(redirect_to="/login/")


class StudentRegistration(APIView):
    serializer_class = StudentProfileSerializer
    def post(self, request):
        serializer = StudentProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeacherRegistration(APIView):
    serializer_class = TeacherProfileSerializer
    def post(self, request):
        serializer = TeacherProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
