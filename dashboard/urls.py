from django.urls import path

from . import views


app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path(
        "donaciones/",
        views.donation_settings,
        name="donation_settings",
    ),
    path(
        "videos/",
        views.youtube_video_list,
        name="youtube_video_list",
    ),
    path(
        "videos/agregar/",
        views.youtube_video_create,
        name="youtube_video_create",
    ),
    path(
        "videos/<int:pk>/editar/",
        views.youtube_video_update,
        name="youtube_video_update",
    ),
    path(
        "videos/<int:pk>/sincronizar/",
        views.youtube_video_sync,
        name="youtube_video_sync",
    ),
    path(
        "videos/<int:pk>/eliminar/",
        views.youtube_video_delete,
        name="youtube_video_delete",
    ),
    path("banners/", views.banner_list, name="banner_list"),
    path("banners/crear/", views.banner_create, name="banner_create"),
    path("banners/<int:pk>/editar/", views.banner_update, name="banner_update"),
    path("banners/<int:pk>/eliminar/", views.banner_delete, name="banner_delete"),
    path("eventos/", views.event_list, name="event_list"),
    path("eventos/crear/", views.event_create, name="event_create"),
    path("eventos/<int:pk>/editar/", views.event_update, name="event_update"),
    path(
        "eventos/<int:pk>/seleccionar/",
        views.event_feature,
        name="event_feature",
    ),
    path("eventos/<int:pk>/eliminar/", views.event_delete, name="event_delete"),
    path("galeria/", views.gallery_image_list, name="gallery_image_list"),
    path(
        "galeria/agregar/",
        views.gallery_image_create,
        name="gallery_image_create",
    ),
    path(
        "galeria/<int:pk>/editar/",
        views.gallery_image_update,
        name="gallery_image_update",
    ),
    path(
        "galeria/<int:pk>/eliminar/",
        views.gallery_image_delete,
        name="gallery_image_delete",
    ),
    path("destacados/", views.showcase_list, name="showcase_list"),
    path(
        "destacados/categorias/crear/",
        views.showcase_category_create,
        name="showcase_category_create",
    ),
    path(
        "destacados/categorias/<int:pk>/editar/",
        views.showcase_category_update,
        name="showcase_category_update",
    ),
    path(
        "destacados/categorias/<int:pk>/eliminar/",
        views.showcase_category_delete,
        name="showcase_category_delete",
    ),
    path(
        "destacados/tarjetas/crear/",
        views.showcase_item_create,
        name="showcase_item_create",
    ),
    path(
        "destacados/tarjetas/<int:pk>/editar/",
        views.showcase_item_update,
        name="showcase_item_update",
    ),
    path(
        "destacados/tarjetas/<int:pk>/eliminar/",
        views.showcase_item_delete,
        name="showcase_item_delete",
    ),
    path(
        "equipo-ministerial/",
        views.ministry_profile_list,
        name="ministry_profile_list",
    ),
    path(
        "equipo-ministerial/agregar/",
        views.ministry_profile_create,
        name="ministry_profile_create",
    ),
    path(
        "equipo-ministerial/<int:pk>/editar/",
        views.ministry_profile_update,
        name="ministry_profile_update",
    ),
    path(
        "equipo-ministerial/<int:pk>/eliminar/",
        views.ministry_profile_delete,
        name="ministry_profile_delete",
    ),
    path("usuarios/", views.user_list, name="user_list"),
    path("usuarios/crear/", views.user_create, name="user_create"),
    path("usuarios/<int:pk>/editar/", views.user_update, name="user_update"),
    path(
        "usuarios/<int:pk>/contrasena/",
        views.user_password,
        name="user_password",
    ),
    path("usuarios/<int:pk>/eliminar/", views.user_delete, name="user_delete"),
]
