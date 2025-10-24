from django.db import models


class Transaccion(models.Model):
    interno = models.AutoField(primary_key=True, db_column="INTERNO")
    num_documento_id_obligado = models.CharField(
        max_length=50, db_column="NUMDOCUMENTOIDOBLIGADO"
    )
    num_factura = models.CharField(max_length=50, db_column="NUMFACTURA")
    tipo_nota = models.CharField(max_length=10, db_column="TIPONOTA")
    num_nota = models.CharField(max_length=50, db_column="NUMNOTA")
    estado = models.CharField(max_length=20, db_column="ESTADO")
    estado_nota = models.CharField(max_length=20, db_column="ESTADO_NOTA")

    class Meta:
        db_table = '"BDRIPS"."TRANSACCION"'
        managed = False  # evita que Django intente crear/modificar la tabla

    def __str__(self):
        return f"Transaccion {self.num_factura} - Estado: {self.estado}"


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
