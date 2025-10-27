"use client";

import React, { useState, useRef } from "react";
import SignaturePad, { SignaturePadHandle } from "./SignaturePad";
import "@/styles/form.css";
import { normalizeLabel } from "@/utils/utils";
import FileInputCamera, { FileItem } from "./FileInputCamera";

interface FormField {
    id: number;
    label: string;
    field_type: string;
    required: number;
}

interface FormData {
    id: number;
    name: string;
    description: string;
    fields: FormField[];
}

export default function DynamicFormClient({ form }: { form: FormData }) {
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [successMsg, setSuccessMsg] = useState<string | null>(null);

    const valuesRef = useRef<Record<number, string>>({});
    const fileRefs = useRef<Record<number, FileItem[]>>({});
    const signatureRef = useRef<SignaturePadHandle | null>(null);

    function validate(): string[] {
        const missing: string[] = [];
        for (const field of form.fields) {
            if (field.required) {
                if (field.field_type === "file") {
                    const files = fileRefs.current[field.id] || [];
                    if (files.length === 0) missing.push(field.label);
                } else if (field.field_type === "signature") {
                    if (!signatureRef.current?.isSigned()) missing.push(field.label);
                } else {
                    const val = valuesRef.current[field.id];
                    if (!val) missing.push(field.label);
                }
            }
        }
        return missing;
    }

    async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();
        setError(null);
        setSuccessMsg(null);

        const missing = validate();
        if (missing.length) {
            setError("Faltan campos requeridos: " + missing.join(", "));
            return;
        }

        setSubmitting(true);
        try {
            const fd = new FormData();
            fd.append("form_id", form.id.toString());

            for (const field of form.fields) {
                const key = normalizeLabel(field.label);

                if (field.field_type === "file") {
                    const files = fileRefs.current[field.id] || [];
                    files.forEach(item => {
                        if (item.file) fd.append(key, item.file, item.name);
                    });
                } else if (field.field_type === "signature") {
                    const dataUrl = signatureRef.current?.getDataURL();
                    if (dataUrl) {
                        const blob = dataURLtoBlob(dataUrl);
                        fd.append(key, blob, `signature-${field.id}.png`);
                    }
                } else {
                    const value = valuesRef.current[field.id];
                    fd.append(key, value ?? "");
                }
            }

            const base = process.env.NEXT_PUBLIC_API_BASE;
            const res = await fetch(`${base}/submissions/`, {
                method: "POST",
                body: fd,
            });

            if (!res.ok) throw new Error("Error al enviar formulario");

            setSuccessMsg("✅ Formulario enviado correctamente");
            e.currentTarget.reset();
            signatureRef.current?.clear();
            valuesRef.current = {};
            fileRefs.current = {};
        } catch (err: any) {
            setError(err.message);
        } finally {
            setSubmitting(false);
        }
    }

    function dataURLtoBlob(dataurl: string): Blob {
        const [header, data] = dataurl.split(",");
        const mime = header.match(/:(.*?);/)?.[1] || "image/png";
        const binary = atob(data);
        const array = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) array[i] = binary.charCodeAt(i);
        return new Blob([array], { type: mime });
    }

    function renderField(field: FormField) {
        const id = field.id;
        const requiredMark = field.required ? <span className="text-red-500">*</span> : null;

        const commonClass =
            "w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none";

        switch (field.field_type) {
            case "text":
                return (
                    <div className="mb-4" key={id}>
                        <label className="block text-gray-700 font-medium mb-1">
                            {field.label} {requiredMark}
                        </label>
                        <input
                            type="text"
                            className={commonClass}
                            onChange={(e) => (valuesRef.current[id] = e.target.value)}
                            placeholder={field.label}
                        />
                    </div>
                );
            case "date":
                return (
                    <div className="mb-4" key={id}>
                        <label className="block text-gray-700 font-medium mb-1">
                            {field.label} {requiredMark}
                        </label>
                        <input
                            type="date"
                            className={commonClass}
                            onChange={(e) => (valuesRef.current[id] = e.target.value)}
                        />
                    </div>
                );
            case "file":
                return (
                    <FileInputCamera
                        key={field.id}
                        fieldId={field.id}
                        label={field.label}
                        fileRefs={fileRefs}
                    />
                );
            case "signature":
                return (
                    <div className="mb-6" key={id}>
                        <label className="block text-gray-700 font-medium mb-2">
                            {field.label} {requiredMark}
                        </label>
                        <div className="border border-gray-300 rounded-md overflow-hidden bg-gray-50">
                            <SignaturePad ref={signatureRef} />
                        </div>
                    </div>
                );
            default:
                return (
                    <div className="mb-4" key={id}>
                        <label className="block text-gray-700 font-medium mb-1">{field.label}</label>
                        <input
                            type="text"
                            className={commonClass}
                            onChange={(e) => (valuesRef.current[id] = e.target.value)}
                        />
                    </div>
                );
        }
    }

    return (
        <form onSubmit={handleSubmit} className="max-w-xl mx-auto bg-white p-6 rounded-xl shadow-md">
            <h1 className="text-2xl font-semibold text-gray-800 mb-6">{form.name}</h1>
            <p className="text-gray-600 mb-6">{form.description}</p>

            {form.fields.map(renderField)}

            <button
                type="submit"
                disabled={submitting}
                className={`w-full py-2 rounded-md text-white font-medium transition ${submitting ? "bg-gray-400 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"
                    }`}
            >
                {submitting ? "Enviando..." : "Enviar"}
            </button>

            {error && <div className="mt-4 text-red-600 bg-red-50 border border-red-200 p-3 rounded">{error}</div>}
            {successMsg && <div className="mt-4 text-green-700 bg-green-50 border border-green-200 p-3 rounded">{successMsg}</div>}
        </form>
    );
}

