from django.db import models


class TiForm(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"TiForm: {self.name}"

    class Meta:
        db_table = '"BDRIPS"."TIFORM"'
        managed = False


class TiFormField(models.Model):
    FORM_FIELD_TYPES = [
        ("text", "Texto"),
        ("file", "Archivo"),
        ("signature", "Firma"),
        ("date", "Fecha"),
    ]
    form = models.ForeignKey(TiForm, related_name="fields", on_delete=models.CASCADE)
    label = models.CharField(max_length=200)
    field_type = models.CharField(max_length=50, choices=FORM_FIELD_TYPES)
    required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.label} ({self.get_field_type_display()})"

    class Meta:
        db_table = '"BDRIPS"."TIFORMFIELD"'
        managed = False


class TiFormSubmission(models.Model):
    form = models.ForeignKey(TiForm, on_delete=models.CASCADE)
    data = models.JSONField()  # Guardamos respuestas dinámicas
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TiFormSubmission {self.form.name} - {self.created_at}"

    class Meta:
        db_table = '"BDRIPS"."TIFORMSUBMISSION"'
        managed = False
