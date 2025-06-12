from django.urls import path
from app_home import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', auth_views.LoginView.as_view(), name='login'), 
    path('home/', views.home_view, name='home'),
    path('cadastrar_colaborador/', views.cadastrar_colaborador, name='cadastrar_colaborador'),
    path('sucesso/', views.sucesso, name='sucesso'),
    path('cadastrar_epi/', views.cadastrar_epi, name='cadastrar_epi'),
    path('cadastro_epi_sucesso/', views.cadastro_epi_sucesso, name= 'cadastro_epi_sucesso'),
    path('registrar/', views.registrar, name='registrar'),
    path('registro_sucesso/', views.registro_sucesso, name= 'registro_sucesso'),
    path('listar_colaboradores/', views.listar_colaboradores, name= 'listar_colaboradores'),
    path('editar_colaborador/<int:id>/', views.editar_colaborador, name= 'editar_colaborador'),
    path('excluir_colaborador/<int:id>/', views.excluir_colaborador, name='excluir_colaborador'),
    path('listar_epi/', views.listar_epi, name= 'listar_epi'),
    path('editar_epi/<int:id>/', views.editar_epi, name= 'editar_epi'),
    path('excluir_epi/<int:id>/', views.excluir_epi, name= 'excluir_epi'),
    path('listar_registro_relatorio/', views.listar_registro_relatorio, name= 'listar_registro_relatorio'),
    path('relatorio_colaborador/', views.relatorio_colaborador, name= 'relatorio_colaborador'),
    path('perfil/', views.perfil, name='perfil'),
    path('editar_status/<int:id>/', views.editar_status, name='editar_status'),
    path('visualizar_quantidade_epi/', views.visualizar_quantidade_epi, name= 'visualizar_quantidade_epi'),
    path('avisos/', views.avisos, name= 'avisos'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login.html'), name='logout'),
]

