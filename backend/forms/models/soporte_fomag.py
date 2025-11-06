from django.db import models
from forms.decorators import register_model_for_api


@register_model_for_api("soporte_fomag")
class SoporteFomag(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    mrcodcons = models.DecimalField(
        max_digits=15, decimal_places=0, db_column="MRCODCONS", blank=True, null=True
    )
    benumdocbe = models.CharField(
        max_length=15, db_column="BENUMDOCBE", blank=True, null=True
    )
    autorizacion = models.CharField(
        max_length=2, db_column="AUTORIZACION", blank=True, null=True
    )
    img_autorizacion = models.CharField(
        max_length=250, db_column="IMG_AUTORIZACION", blank=True, null=True
    )
    servicio_directo = models.CharField(
        max_length=2, db_column="SERVICIO_DIRECTO", blank=True, null=True
    )
    orden_comfamiliar = models.CharField(
        max_length=2, db_column="ORDEN_COMFAMILIAR", blank=True, null=True
    )
    img_orden = models.CharField(
        max_length=250, db_column="IMG_ORDEN", blank=True, null=True
    )
    ipzoho = models.CharField(max_length=20, db_column="IPZOHO", blank=True, null=True)
    usuario = models.CharField(
        max_length=15, db_column="USUARIO", blank=True, null=True
    )
    aufecmod = models.DecimalField(
        max_digits=8, decimal_places=0, db_column="AUFECMOD", blank=True, null=True
    )
    auhormod = models.DecimalField(
        max_digits=6, decimal_places=0, db_column="AUHORMOD", blank=True, null=True
    )
    aufeccrea = models.DateTimeField(db_column="AUFECCREA", blank=True, null=True)
    certificado = models.CharField(
        max_length=2, db_column="CERTIFICADO", blank=True, null=True
    )

    class Meta:
        db_table = '"BDSALUD"."TBSOPORTES"'
        managed = False
