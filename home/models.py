from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class HomePage(Page):
    body = RichTextField(blank=True, help_text="Hello World content")

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]
