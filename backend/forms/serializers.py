import logging

from django.db import transaction
from rest_framework import serializers
from .models import Form, FormField, FormFieldForm, FormFieldOption, FormSubmission

logger = logging.getLogger("forms")


class FormFieldOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormFieldOption
        fields = ["id", "label", "value", "order"]
        extra_kwargs = {
            "id": {"required": False},
        }


class FormFieldSerializer(serializers.ModelSerializer):
    options = FormFieldOptionSerializer(many=True, required=False)

    class Meta:
        model = FormField
        fields = [
            "id",
            "name",
            "label",
            "field_type",
            "required",
            "options",
            "depends_on",
            "depends_value",
            "api_url",
            "min_search_chars",
            "result_key",
            "label_key",
            "value_key",
        ]
        validators = []

    def create(self, validated_data):
        options_data = validated_data.pop("options", [])

        form_field = FormField.objects.create(**validated_data)

        for option_data in options_data:
            form_field.options.create(**option_data)

        return form_field

    def update(self, instance, validated_data):
        print("✏️ FormFieldSerializer.update() llamado", flush=True)
        options_data = validated_data.pop("options", [])
        print(f"🔧 Options data: {options_data}", flush=True)
        instance.name = validated_data.get("name", instance.name)
        instance.label = validated_data.get("label", instance.label)
        instance.field_type = validated_data.get("field_type", instance.field_type)
        instance.required = validated_data.get("required", instance.required)
        instance.depends_on = validated_data.get("depends_on", instance.depends_on)
        instance.depends_value = validated_data.get(
            "depends_value", instance.depends_value
        )
        instance.api_url = validated_data.get("api_url", instance.api_url)
        instance.min_search_chars = validated_data.get(
            "min_search_chars", instance.min_search_chars
        )
        instance.result_key = validated_data.get("result_key", instance.result_key)
        instance.label_key = validated_data.get("label_key", instance.label_key)
        instance.value_key = validated_data.get("value_key", instance.value_key)
        instance.save()
        if options_data is not None:
            instance.options.all().delete()
            for option_data in options_data:
                instance.options.create(**option_data)

        return instance


class FormSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True)

    class Meta:
        model = Form
        fields = ["id", "name", "description", "fields"]

    def create(self, validated_data):
        formfields_data = validated_data.pop("fields", [])

        try:
            with transaction.atomic():
                form = Form.objects.create(
                    name=validated_data["name"],
                    description=validated_data.get("description", ""),
                )

                self._process_form_fields(form, formfields_data)

                return form

        except Exception as e:
            raise serializers.ValidationError(f"Error creando form: {str(e)}")

    def _process_form_fields(self, form, formfields_data):
        """Procesa todos los campos del formulario y sus relaciones"""
        for field_data in formfields_data:
            form_field = self._get_or_create_form_field(field_data)
            self._process_field_options(form_field, field_data)
            self._link_field_to_form(form, form_field)

    def _get_or_create_form_field(self, field_data):
        """Obtiene o crea un FormField"""
        name = field_data.get("name")
        label = field_data.get("label")
        field_type = field_data.get("field_type")
        required = field_data.get("required", True)
        depends_on = field_data.get("depends_on")
        depends_value = field_data.get("depends_value")
        api_url = field_data.get("api_url")
        min_search_chars = field_data.get("min_search_chars")
        result_key = field_data.get("result_key")
        label_key = field_data.get("label_key")
        value_key = field_data.get("value_key")

        # Buscar field existente con los mismos atributos clave
        form_field = FormField.objects.filter(
            label=label, field_type=field_type, required=required
        ).first()

        if form_field:
            return form_field
        else:
            form_field = FormField.objects.create(
                name=name,
                label=label,
                field_type=field_type,
                required=required,
                depends_on=depends_on,
                depends_value=depends_value,
                api_url=api_url,
                min_search_chars=min_search_chars,
                result_key=result_key,
                label_key=label_key,
                value_key=value_key,
            )
            return form_field

    def _process_field_options(self, form_field, field_data):
        """Procesa las opciones para campos de tipo checkbox/select"""
        field_type = field_data.get("field_type")
        options_data = field_data.get("options", [])

        if field_type in ["checkbox", "select", "radio"] and options_data:
            for option_data in options_data:
                self._create_field_option(form_field, option_data)

    def _create_field_option(self, form_field, option_data):
        """Crea una opción para un campo del formulario"""
        FormFieldOption.objects.create(
            formfield=form_field,
            value=option_data.get("value"),
            label=option_data.get("label"),
            order=option_data.get("order", 0),
        )

    def _link_field_to_form(self, form, form_field):
        """Crea la relación entre el formulario y el campo usando el related_name"""
        if form_field not in form.fields.all():
            form.fields.add(form_field)

    def update(self, instance, validated_data):
        """Actualiza el formulario y sus campos"""
        fields_data = validated_data.pop("fields", None)

        try:
            with transaction.atomic():
                # Actualizar datos básicos del formulario
                instance.name = validated_data.get("name", instance.name)
                instance.description = validated_data.get(
                    "description", instance.description
                )
                instance.save()

                # Actualizar campos si se proporcionan
                if fields_data is not None:
                    self._update_form_fields(instance, fields_data)

                return instance

        except Exception as e:
            raise serializers.ValidationError(f"Error actualizando form: {str(e)}")

    def _update_form_fields(self, instance, fields_data):
        """Actualiza los campos del formulario de manera más eficiente"""
        # Limpiar campos existentes
        instance.fields.clear()

        # Crear nuevos campos y relaciones
        for field_data in fields_data:
            form_field = self._get_or_create_form_field(field_data)
            self._process_field_options(form_field, field_data)
            instance.fields.add(form_field)


class FormSubmissionSerializer(serializers.ModelSerializer):
    form = serializers.PrimaryKeyRelatedField(queryset=Form.objects.all())

    class Meta:
        model = FormSubmission
        fields = ["form", "data"]
