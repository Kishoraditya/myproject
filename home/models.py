from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel


class HomePage(Page):
    body = RichTextField(blank=True, help_text="Hello World content")

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]
