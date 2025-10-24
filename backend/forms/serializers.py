from rest_framework import serializers
from .models import Form, FormField, FormSubmission


class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = ["label", "field_type", "required"]


class FormSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True)

    class Meta:
        model = Form
        fields = ["name", "description", "fields"]

    def create(self, validated_data):
        fields_data = validated_data.pop("fields", [])
        form = Form.objects.create(**validated_data)
        for field_data in fields_data:
            FormField.objects.create(form=form, **field_data)
        return form

    def update(self, instance, validated_data):
        fields_data = validated_data.pop("fields", None)

        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.save()

        if fields_data is not None:
            instance.fields.all().delete()
            for field_data in fields_data:
                FormField.objects.create(form=instance, **field_data)

        return instance


class FormSubmissionSerializer(serializers.ModelSerializer):
    form = serializers.PrimaryKeyRelatedField(queryset=Form.objects.all())

    class Meta:
        model = FormSubmission
        fields = ["form", "data"]
