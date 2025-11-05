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
            "dynamic_options_url",
            "depends_on_field",
            "dynamic_result_key",
        ]
        validators = []

    def create(self, validated_data):
        options_data = validated_data.pop("options", [])

        form_field = FormField.objects.create(**validated_data)

        for option_data in options_data:
            form_field.options.create(**option_data)

        return form_field

    def update(self, instance, validated_data):
        options_data = validated_data.pop("options", [])
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
        instance.dynamic_options_url = validated_data.get(
            "dynamic_options_url", instance.dynamic_options_url
        )
        instance.depends_on_field = validated_data.get(
            "depends_on_field", instance.depends_on_field
        )
        instance.dynamic_result_key = validated_data.get(
            "dynamic_result_key", instance.dynamic_result_key
        )
        instance.save()
        if options_data is not None:
            instance.options.all().delete()
            for option_data in options_data:
                instance.options.create(**option_data)

        return instance


class FormFieldThroughSerializer(serializers.ModelSerializer):
    formfield = FormFieldSerializer()
    field_order = serializers.IntegerField(required=False, default=0)

    class Meta:
        model = FormFieldForm
        fields = ["formfield", "field_order"]

    def to_representation(self, instance):
        """Para mostrar los datos en formato plano"""
        representation = super().to_representation(instance)
        # Aplanar la estructura: mover campos de formfield al nivel superior
        formfield_data = representation.pop("formfield", {})
        for key, value in formfield_data.items():
            representation[key] = value
        return representation

    def to_internal_value(self, data):
        """Para procesar los datos entrantes en formato plano"""
        # Reestructurar los datos para que formfield esté anidado
        formfield_fields = [
            "id",
            "name",
            "label",
            "field_type",
            "required",
            "depends_on",
            "depends_value",
            "api_url",
            "min_search_chars",
            "result_key",
            "label_key",
            "value_key",
            "dynamic_options_url",
            "depends_on_field",
            "dynamic_result_key",
            "options",
        ]

        formfield_data = {}
        other_data = {}

        for key, value in data.items():
            if key in formfield_fields:
                formfield_data[key] = value
            else:
                other_data[key] = value

        other_data["formfield"] = formfield_data
        return super().to_internal_value(other_data)


class FormSerializer(serializers.ModelSerializer):
    fields = FormFieldThroughSerializer(many=True, source="formfieldform_set")

    class Meta:
        model = Form
        fields = ["id", "name", "slug", "description", "fields"]
        read_only_fields = ["id", "slug"]

    def to_representation(self, instance):
        """Sobrescribir para ordenar los fields por field_order"""
        representation = super().to_representation(instance)

        ordered_formfields = instance.formfieldform_set.all().order_by("field_order")

        representation["fields"] = FormFieldThroughSerializer(
            ordered_formfields, many=True
        ).data

        return representation

    def validate_name(self, value):
        """
        Validar que el nombre sea único para evitar slugs duplicados.
        Usa count() en lugar de exists() para compatibilidad con IBM i,
        exists() genera error (-418) Use of parameter marker or NULL not valid.
        """
        value = value.strip() if isinstance(value, str) else value

        if self.instance is None:
            count = Form.objects.filter(name=value).count()
            if count > 0:
                raise serializers.ValidationError(
                    "Ya existe un formulario con este nombre. El slug generado estaría duplicado."
                )
        else:
            count = Form.objects.filter(name=value).exclude(id=self.instance.id).count()
            if count > 0:
                raise serializers.ValidationError(
                    "Ya existe otro formulario con este nombre. El slug generado estaría duplicado."
                )

        return value

    def create(self, validated_data):
        formfields_data = validated_data.pop("formfieldform_set", [])

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
        """Procesa todos los campos del formulario y sus relaciones con orden"""
        for field_data in formfields_data:
            form_field = self._get_or_create_form_field(field_data["formfield"])
            self._process_field_options(form_field, field_data)
            self._link_field_to_form(form, form_field, field_data)

    def _get_or_create_form_field(self, field_data):
        """Obtiene o crea un FormField"""
        field_id = field_data.get("id")

        # Si viene con ID, buscar el field existente
        if field_id:
            try:
                return FormField.objects.get(id=field_id)
            except FormField.DoesNotExist:
                pass

        # Si no existe o no viene con ID, crear uno nuevo
        return FormField.objects.create(
            name=field_data.get("name"),
            label=field_data.get("label"),
            field_type=field_data.get("field_type"),
            required=field_data.get("required", True),
            depends_on=field_data.get("depends_on"),
            depends_value=field_data.get("depends_value"),
            api_url=field_data.get("api_url"),
            min_search_chars=field_data.get("min_search_chars", 3),
            result_key=field_data.get("result_key"),
            label_key=field_data.get("label_key"),
            value_key=field_data.get("value_key"),
            dynamic_options_url=field_data.get("dynamic_options_url"),
            depends_on_field=field_data.get("depends_on_field"),
            dynamic_result_key=field_data.get("dynamic_result_key"),
        )

    def _process_field_options(self, form_field, field_data):
        """Procesa las opciones para campos de tipo checkbox/select"""
        field_type = field_data["formfield"].get("field_type")
        options_data = field_data["formfield"].get("options", [])

        if field_type in ["checkbox", "select", "radio"] and options_data:
            for option_data in options_data:
                FormFieldOption.objects.create(
                    formfield=form_field,
                    value=option_data.get("value"),
                    label=option_data.get("label"),
                    order=option_data.get("order", 0),
                )

    def _link_field_to_form(self, form, form_field, field_data):
        """Crea la relación entre el formulario y el campo con el orden"""
        FormFieldForm.objects.create(
            form=form,
            formfield=form_field,
            field_order=field_data.get("field_order", 0),
        )

    def update(self, instance, validated_data):
        """Actualiza el formulario y sus campos"""
        fields_data = validated_data.pop("formfieldform_set", None)

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
        """Actualiza los campos del formulario con orden"""
        # Limpiar relaciones existentes
        FormFieldForm.objects.filter(form=instance).delete()

        # Crear nuevas relaciones con orden
        for field_data in fields_data:
            form_field = self._get_or_create_form_field(field_data["formfield"])
            self._update_field_options(form_field, field_data)
            FormFieldForm.objects.create(
                form=instance,
                formfield=form_field,
                field_order=field_data.get("field_order", 0),
            )

    def _update_field_options(self, form_field, field_data):
        """Actualiza las opciones para campos de tipo checkbox/select"""
        field_type = field_data["formfield"].get("field_type")
        options_data = field_data["formfield"].get("options", [])

        if field_type in ["checkbox", "select", "radio"] and options_data:
            # Eliminar opciones existentes y crear nuevas
            form_field.options.all().delete()
            for option_data in options_data:
                FormFieldOption.objects.create(
                    formfield=form_field,
                    value=option_data.get("value"),
                    label=option_data.get("label"),
                    order=option_data.get("order", 0),
                )


class FormSubmissionSerializer(serializers.ModelSerializer):
    form = serializers.PrimaryKeyRelatedField(queryset=Form.objects.all())

    class Meta:
        model = FormSubmission
        fields = ["form", "data"]
