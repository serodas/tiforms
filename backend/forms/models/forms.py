import time
from django.utils.text import slugify

from django.db import models


class FormField(models.Model):
    FORM_FIELD_TYPES = [
        ("text", "Texto"),
        ("file", "Archivo"),
        ("signature", "Firma"),
        ("date", "Fecha"),
        ("checkbox", "Checkbox"),
        ("select", "Lista Desplegable"),
        ("radio", "Lista seleccion unica"),
        ("async_select", "Select con búsqueda asíncrona"),
    ]

    id = models.AutoField(primary_key=True, db_column="ID")
    name = models.CharField(max_length=200, db_column="NAME")
    label = models.CharField(max_length=200, db_column="LABEL")
    field_type = models.CharField(
        max_length=50, choices=FORM_FIELD_TYPES, db_column="FIELD_TYPE"
    )
    required = models.SmallIntegerField(default=1, db_column="REQUIRED")
    created_at = models.DateTimeField(auto_now_add=True, db_column="CREATED_AT")

    depends_on = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        db_column="DEPENDS_ON",
        help_text="Nombre del campo del que depende",
    )
    depends_value = models.CharField(
        max_length=200, blank=True, null=True, db_column="DEPENDS_VALUE"
    )

    api_url = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        db_column="API_URL",
        help_text="URL para consultar opciones (ej: /api/search-documentos/)",
    )
    min_search_chars = models.IntegerField(
        default=3,
        db_column="MIN_SEARCH_CHARS",
        help_text="Mínimo de caracteres para realizar búsqueda",
    )
    result_key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_column="RESULT_KEY",
        help_text="Clave donde vienen los resultados en la respuesta JSON",
    )
    label_key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default="label",
        db_column="LABEL_KEY",
        help_text="Campo a usar como label en las opciones",
    )
    value_key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default="value",
        db_column="VALUE_KEY",
        help_text="Campo a usar como value en las opciones",
    )
    dynamic_options_url = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        db_column="DYNAMIC_OPTIONS_URL",
        help_text="URL para obtener opciones dinámicas basadas en otro campo",
    )
    depends_on_field = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        db_column="DEPENDS_ON_FIELD",
        help_text="Nombre del campo del que dependen las opciones",
    )
    dynamic_result_key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_column="DYNAMIC_RESULT_KEY",
        help_text="Clave para los resultados en la respuesta dinámica",
    )

    class Meta:
        db_table = '"TIFORMS"."FORMFIELD"'
        managed = False
        unique_together = ("label", "field_type", "required")

    def __str__(self):
        return f"Campo: {self.label} ({self.field_type})"

    @property
    def has_options(self):
        opts = getattr(self, "options", None)
        return self.field_type == "checkbox" and opts and opts.exists()

    def is_active(self, submission_data):
        if not self.depends_on:
            return True
        return submission_data.get(self.depends_on) == self.depends_value


class Form(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    name = models.CharField(max_length=200, db_column="NAME")
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        null=True,
        db_column="SLUG",
        help_text="Identificador único para URLs",
    )
    description = models.TextField(blank=True, db_column="DESCRIPTION")
    created_at = models.DateTimeField(auto_now_add=True, db_column="CREATED_AT")
    fields = models.ManyToManyField(
        FormField, through="FormFieldForm", related_name="forms"
    )

    class Meta:
        db_table = '"TIFORMS"."FORM"'
        managed = False

    def __str__(self):
        return f"Formulario: {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            max_attempts = 100

            while (
                Form.objects.filter(slug=slug).count() > 0 and counter <= max_attempts
            ):
                slug = f"{base_slug}-{counter}"
                counter += 1

            if counter > max_attempts:
                slug = f"{base_slug}-{int(time.time())}"

            self.slug = slug
        super().save(*args, **kwargs)


class FormFieldForm(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    form = models.ForeignKey(Form, db_column="FORM_ID", on_delete=models.CASCADE)
    formfield = models.ForeignKey(
        FormField, db_column="FORMFIELD_ID", on_delete=models.CASCADE
    )
    field_order = models.IntegerField(default=0, db_column="FIELD_ORDER")

    class Meta:
        db_table = '"TIFORMS"."FORM_FORMFIELDS"'
        managed = False
        unique_together = (("form", "formfield"),)


class FormSubmission(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    form = models.ForeignKey(Form, on_delete=models.CASCADE, db_column="FORM_ID")
    data = models.TextField(db_column="DATA")
    created_at = models.DateTimeField(auto_now_add=True, db_column="CREATED_AT")

    class Meta:
        db_table = '"TIFORMS"."FORMSUBMISSION"'
        managed = False

    def __str__(self):
        return f"Respuesta al formulario {self.form.name}"


class FormFieldOption(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    formfield = models.ForeignKey(
        "FormField",
        db_column="FORMFIELD_ID",
        on_delete=models.CASCADE,
        related_name="options",
    )
    value = models.CharField(max_length=200, db_column="VALUE")
    label = models.CharField(max_length=200, db_column="LABEL")
    order = models.PositiveSmallIntegerField(default=0, db_column="ORDER")

    class Meta:
        db_table = '"TIFORMS"."FORMFIELDOPTION"'
        managed = False
        ordering = ["order"]

    def __str__(self):
        return f"Opción: {self.label} ({self.formfield.label})"
