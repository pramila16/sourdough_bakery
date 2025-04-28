from django.apps import AppConfig
from mongoengine import connect,disconnect


class BakeryAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bakery_app'

    def ready(self):
        disconnect(alias='default')
        connect(
            db="sourdough_bakery",
            host="mongodb://db:27017",
            username="bakery_user",
            password="99h8#9ZLUxh",
        )
