import os
import logging
from rest_framework import serializers
from .models import Form, FormField, FormFieldForm, FormSubmission
from dbal.ibmi.base import DatabaseWrapper

logger = logging.getLogger(__name__)  # <-- logger configurado


class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = ["id", "label", "field_type", "required"]
        validators = []


class FormSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True)

    class Meta:
        model = Form
        fields = ["id", "name", "description", "fields"]

    def create(self, validated_data):
        print("🚀 Entró a FormSerializer.create con:", validated_data, flush=True)
        formfields_data = validated_data.pop("fields", [])

        dsn = os.getenv("DB2_DSN")
        from dbal.ibmi.base import DatabaseWrapper

        db = DatabaseWrapper({"NAME": dsn})
        cursor = db.create_cursor()
        print("🧩 Cursor DB2 creado", flush=True)

        try:
            # 1️⃣ Crear el FORM principal con SQL directo
            cursor.execute(
                "INSERT INTO TIFORMS.FORM (NAME, DESCRIPTION, CREATED_AT) VALUES (?, ?, CURRENT_TIMESTAMP)",
                [validated_data["name"], validated_data.get("description", "")],
            )
            # Obtener ID del nuevo FORM — seguro frente a concurrencia
            cursor.execute("SELECT IDENTITY_VAL_LOCAL() FROM SYSIBM.SYSDUMMY1")
            row = cursor.fetchone()
            if not row or not row[0]:
                raise Exception("No se pudo obtener el IDENTITY del nuevo FORM")
            form_id = row[0]
            print("✅ FORM creado con ID:", form_id, flush=True)

            # 2️⃣ Insertar o reutilizar los fields
            for ff_data in formfields_data:
                label = ff_data.get("label")
                field_type = ff_data.get("field_type")
                required = 1 if ff_data.get("required", True) else 0

                cursor.execute(
                    "SELECT ID FROM TIFORMS.FORMFIELD WHERE LABEL = ? AND FIELD_TYPE = ? AND REQUIRED = ?",
                    [label, field_type, required],
                )
                row = cursor.fetchone()

                if row:
                    formfield_id = row[0]
                    print("🟢 Reutilizando FormField ID:", formfield_id, flush=True)
                else:
                    print("🟢LABEL:", label, flush=True)
                    print("field_type:", field_type, flush=True)
                    print("required:", required, flush=True)
                    cursor.execute(
                        "INSERT INTO TIFORMS.FORMFIELD (FORM_ID, LABEL, FIELD_TYPE, REQUIRED) VALUES (?, ?, ?, ?)",
                        [form_id, label, field_type, required],
                    )
                    cursor.execute("SELECT IDENTITY_VAL_LOCAL() FROM SYSIBM.SYSDUMMY1")
                    row = cursor.fetchone()
                    print("FORMFIEL NUEVO ES :", row[0], flush=True)
                    if not row or not row[0]:
                        raise Exception(
                            "No se pudo obtener el IDENTITY del nuevo FormField"
                        )
                    formfield_id = row[0]
                    print("🆕 FormField creado con ID:", formfield_id, flush=True)

                cursor.execute(
                    "SELECT 1 FROM TIFORMS.FORM_FORMFIELDS WHERE FORM_ID = ? AND FORMFIELD_ID = ?",
                    [form_id, formfield_id],
                )
                exists = cursor.fetchone()

                if not exists:
                    cursor.execute(
                        "INSERT INTO TIFORMS.FORM_FORMFIELDS (FORM_ID, FORMFIELD_ID) VALUES (?, ?)",
                        [form_id, formfield_id],
                    )
                    print("✅ Relación insertada:", formfield_id, flush=True)
                else:
                    print("⚠️ Relación ya existía:", formfield_id, flush=True)

            db._commit()
            print("💾 Commit hecho", flush=True)

            # 4️⃣ Crear instancia Django con el ID recuperado
            form = Form(id=form_id, **validated_data)

        except Exception as e:
            db._rollback()
            print("❌ Error en create():", str(e), flush=True)
            raise serializers.ValidationError(f"Error creando form: {str(e)}")

        finally:
            db.close()
            print("🔒 Conexión cerrada", flush=True)

        return form

    def update(self, instance, validated_data):
        fields_data = validated_data.pop("fields", None)

        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.save()

        if fields_data is not None:
            # Borramos relaciones anteriores
            FormFieldForm.objects.filter(form=instance).delete()

            for field_data in fields_data:
                required = 1 if field_data.get("required", True) else 0
                formfield, _ = FormField.objects.get_or_create(
                    label=field_data["label"],
                    field_type=field_data["field_type"],
                    required=required,
                )
                FormFieldForm.objects.create(form=instance, formfield=formfield)

        return instance


class FormSubmissionSerializer(serializers.ModelSerializer):
    form = serializers.PrimaryKeyRelatedField(queryset=Form.objects.all())

    class Meta:
        model = FormSubmission
        fields = ["form", "data"]
