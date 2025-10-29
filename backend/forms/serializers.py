import os
import sys
import traceback
import logging

from dbal.ibmi.base import DatabaseWrapper
from rest_framework import serializers
from .models import Form, FormField, FormFieldForm, FormFieldOption, FormSubmission

logger = logging.getLogger("forms")


class FormFieldOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormFieldOption
        fields = ["id", "value", "order"]
        extra_kwargs = {
            "id": {"required": False},
        }


class FormFieldSerializer(serializers.ModelSerializer):
    options = FormFieldOptionSerializer(many=True, read_only=True)

    class Meta:
        model = FormField
        fields = ["id", "name", "label", "field_type", "required", "options"]
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

            for ff_data in formfields_data:
                name = ff_data.get("name")
                label = ff_data.get("label")
                field_type = ff_data.get("field_type")
                required = 1 if ff_data.get("required", True) else 0
                options_data = ff_data.get("options", [])
                depends_on_id = ff_data.get("depends_on")
                depends_value = ff_data.get("depends_value")

                cursor.execute(
                    "SELECT ID FROM TIFORMS.FORMFIELD WHERE LABEL = ? AND FIELD_TYPE = ? AND REQUIRED = ?",
                    [label, field_type, required],
                )
                row = cursor.fetchone()

                if row:
                    formfield_id = row[0]
                else:
                    cursor.execute(
                        "INSERT INTO TIFORMS.FORMFIELD (NAME, LABEL, FIELD_TYPE, REQUIRED, DEPENDS_ON, DEPENDS_VALUE) VALUES (?, ?, ?, ?, ?, ?)",
                        [
                            name,
                            label,
                            field_type,
                            required,
                            depends_on_id,
                            depends_value,
                        ],
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

                if field_type == "checkbox" and options_data:
                    for opt in options_data:
                        value = opt.get("value")
                        label_opt = opt.get("label")
                        order = opt.get("order", 0)
                        cursor.execute(
                            "INSERT INTO TIFORMS.FORMFIELDOPTION (FORMFIELD_ID, VALUE, LABEL, ORDER) VALUES (?, ?, ?, ?)",
                            [formfield_id, value, label_opt, order],
                        )

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
