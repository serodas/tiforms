from django.db import models


class FormField(models.Model):
    FORM_FIELD_TYPES = [
        ("text", "Texto"),
        ("file", "Archivo"),
        ("signature", "Firma"),
        ("date", "Fecha"),
    ]

    id = models.AutoField(primary_key=True, db_column="ID")
    label = models.CharField(max_length=200, db_column="LABEL")
    field_type = models.CharField(
        max_length=50, choices=FORM_FIELD_TYPES, db_column="FIELD_TYPE"
    )
    required = models.SmallIntegerField(default=1, db_column="REQUIRED")
    created_at = models.DateTimeField(auto_now_add=True, db_column="CREATED_AT")

    class Meta:
        db_table = '"TIFORMS"."FORMFIELD"'
        managed = False
        unique_together = ("label", "field_type", "required")

    def __str__(self):
        return f"Campo: {self.label} ({self.field_type})"


class Form(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    name = models.CharField(max_length=200, db_column="NAME")
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


class FormFieldForm(models.Model):
    id = models.BigAutoField(primary_key=True)
    form = models.ForeignKey(Form, db_column="FORM_ID", on_delete=models.CASCADE)
    formfield = models.ForeignKey(
        FormField, db_column="FORMFIELD_ID", on_delete=models.CASCADE
    )

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
