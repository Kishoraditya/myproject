from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtail.snippets.models import register_snippet


class FeatureBlock(blocks.StructBlock):
    icon = ImageChooserBlock(required=False)
    title = blocks.CharBlock(required=True)
    text = blocks.TextBlock(required=True)

    class Meta:
        template = "blocks/feature_block.html"
        icon = "placeholder"
        label = "Feature"


class TestimonialBlock(blocks.StructBlock):
    quote = blocks.TextBlock(required=True)
    author = blocks.CharBlock(required=True)
    role = blocks.CharBlock(required=False)

    class Meta:
        template = "blocks/testimonial_block.html"
        icon = "openquote"
        label = "Testimonial"


class PartnerBlock(blocks.StructBlock):
    logo = ImageChooserBlock(required=True)
    name = blocks.CharBlock(required=True)
    url = blocks.URLBlock(required=False)

    class Meta:
        template = "blocks/partner_block.html"
        icon = "link"
        label = "Partner"


@register_snippet
class SEOSettings(models.Model):
    site_name = models.CharField(max_length=100, blank=True)
    default_description = models.TextField(blank=True)
    default_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    og_type = models.CharField(max_length=20, default="website")
    twitter_card = models.CharField(max_length=20, default="summary_large_image")
    twitter_site = models.CharField(max_length=100, blank=True, null=True)

    panels = [
        FieldPanel("site_name"),
        FieldPanel("default_description"),
        FieldPanel("default_image"),
        FieldPanel("og_type"),
        FieldPanel("twitter_card"),
        FieldPanel("twitter_site"),
    ]

    def get_admin_display_title(self):
        """Return the display title for the admin interface."""
        return "SEO Settings"

    class Meta:
        verbose_name = "SEO Settings"


class HomePage(Page):
    # Hero Section
    hero_title = models.CharField(max_length=100, blank=True)
    hero_subtitle = models.CharField(max_length=200, blank=True)
    hero_cta_text = models.CharField(max_length=50, blank=True)
    hero_cta_link = models.URLField(blank=True, default="https://example.com")
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    # Features Section
    features_title = models.CharField(max_length=100, blank=True)
    features = StreamField(
        [
            ("feature", FeatureBlock()),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    # Pricing Section
    pricing_title = models.CharField(max_length=100, blank=True)
    pricing_subtitle = models.CharField(max_length=200, blank=True)
    pricing_description = models.TextField(blank=True)
    pricing_features = StreamField(
        [
            ("feature", blocks.CharBlock()),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )
    pricing_cta_text = models.CharField(max_length=50, blank=True)
    pricing_cta_link = models.URLField(blank=True, default="https://example.com")

    # Newsletter Section
    newsletter_title = models.CharField(max_length=100, blank=True)
    newsletter_text = models.TextField(blank=True)
    newsletter_button_text = models.CharField(max_length=50, blank=True)

    # Partners Section
    partners_title = models.CharField(max_length=100, blank=True)
    partners_text = models.TextField(blank=True)
    partners = StreamField(
        [
            ("partner", PartnerBlock()),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    # Testimonials Section
    testimonials_title = models.CharField(max_length=100, blank=True)
    testimonials = StreamField(
        [
            ("testimonial", TestimonialBlock()),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    # SEO Fields
    custom_seo_title = models.CharField(
        max_length=100, blank=True, help_text="Custom SEO title (optional)"
    )
    seo_description = models.TextField(
        blank=True, help_text="Custom SEO description (optional)"
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_title"),
                FieldPanel("hero_subtitle"),
                FieldPanel("hero_cta_text"),
                FieldPanel("hero_cta_link"),
                FieldPanel("hero_image"),
            ],
            heading="Hero Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("features_title"),
                FieldPanel("features"),
            ],
            heading="Features Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("pricing_title"),
                FieldPanel("pricing_subtitle"),
                FieldPanel("pricing_description"),
                FieldPanel("pricing_features"),
                FieldPanel("pricing_cta_text"),
                FieldPanel("pricing_cta_link"),
            ],
            heading="Pricing Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("newsletter_title"),
                FieldPanel("newsletter_text"),
                FieldPanel("newsletter_button_text"),
            ],
            heading="Newsletter Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("partners_title"),
                FieldPanel("partners_text"),
                FieldPanel("partners"),
            ],
            heading="Partners Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("testimonials_title"),
                FieldPanel("testimonials"),
            ],
            heading="Testimonials Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("custom_seo_title"),
                FieldPanel("seo_description"),
            ],
            heading="SEO",
        ),
    ]

    class Meta:
        verbose_name = "Home Page"


class LandingPage(Page):
    """
    A flexible landing page model for SEO-optimized content.
    This can be created as a child page of any page type.
    """

    # Hero Section
    hero_title = models.CharField(max_length=100, blank=True)
    hero_subtitle = models.CharField(max_length=200, blank=True)
    hero_cta_text = models.CharField(max_length=50, blank=True)
    hero_cta_link = models.URLField(blank=True, default="https://example.com")
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    # Main Content Section
    intro = RichTextField(blank=True)
    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="full title")),
            ("paragraph", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
            ("feature", FeatureBlock()),
            ("testimonial", TestimonialBlock()),
            ("quote", blocks.BlockQuoteBlock()),
            (
                "cta",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock(required=True)),
                        ("text", blocks.RichTextBlock(required=False)),
                        ("button_text", blocks.CharBlock(required=True)),
                        ("button_link", blocks.URLBlock(required=True)),
                    ]
                ),
            ),
        ],
        use_json_field=True,
        blank=True,
    )

    # Enhanced SEO Fields - Wagtail already has search_description
    og_title = models.CharField(
        verbose_name="Open Graph Title",
        max_length=100,
        blank=True,
        help_text="Custom title for social media sharing (Facebook, LinkedIn)",
    )
    og_description = models.TextField(
        verbose_name="Open Graph Description",
        blank=True,
        help_text="Custom description for social media sharing",
    )
    og_image = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name="Open Graph Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Image for social media sharing (ideally 1200×630px)",
    )
    twitter_title = models.CharField(
        max_length=100, blank=True, help_text="Custom title for Twitter sharing"
    )
    twitter_description = models.TextField(
        blank=True, help_text="Custom description for Twitter sharing"
    )
    twitter_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Image for Twitter sharing (ideally 1200×600px)",
    )
    canonical_url = models.URLField(
        blank=True, help_text="Override canonical URL if this page has a preferred URL"
    )

    # Schema.org structured data
    enable_schema_org = models.BooleanField(
        default=True, help_text="Enable Schema.org structured data"
    )
    schema_org_type = models.CharField(
        max_length=100,
        default="WebPage",
        help_text="Type of Schema.org entity (e.g., WebPage, Article, Product)",
    )
    publish_date = models.DateField(
        null=True, blank=True, help_text="When this content was first published"
    )
    update_date = models.DateField(
        null=True,
        blank=True,
        help_text="When this content was last significantly updated",
    )

    # Keywords and taxonomies
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated keywords for search engines",
    )

    # Content options
    show_breadcrumbs = models.BooleanField(
        default=True, help_text="Show breadcrumb navigation"
    )
    show_share_buttons = models.BooleanField(
        default=True, help_text="Show social sharing buttons"
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_title"),
                FieldPanel("hero_subtitle"),
                FieldPanel("hero_cta_text"),
                FieldPanel("hero_cta_link"),
                FieldPanel("hero_image"),
            ],
            heading="Hero Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("intro"),
                FieldPanel("body"),
            ],
            heading="Main Content",
        ),
        MultiFieldPanel(
            [
                FieldPanel("show_breadcrumbs"),
                FieldPanel("show_share_buttons"),
            ],
            heading="Content Options",
        ),
    ]

    promote_panels = Page.promote_panels + [
        MultiFieldPanel(
            [
                FieldPanel("meta_keywords"),
                FieldPanel("canonical_url"),
            ],
            heading="Search Engine Optimization",
        ),
        MultiFieldPanel(
            [
                FieldPanel("og_title"),
                FieldPanel("og_description"),
                FieldPanel("og_image"),
            ],
            heading="Open Graph (Facebook, LinkedIn)",
        ),
        MultiFieldPanel(
            [
                FieldPanel("twitter_title"),
                FieldPanel("twitter_description"),
                FieldPanel("twitter_image"),
            ],
            heading="Twitter",
        ),
        MultiFieldPanel(
            [
                FieldPanel("enable_schema_org"),
                FieldPanel("schema_org_type"),
                FieldPanel("publish_date"),
                FieldPanel("update_date"),
            ],
            heading="Structured Data",
        ),
    ]

    class Meta:
        verbose_name = "Landing Page"
