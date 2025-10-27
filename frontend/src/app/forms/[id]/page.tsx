import DynamicFormClient from "@/components/DynamicFormClient";

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

export default async function FormPage({ params }: { params: Promise<{ id: string }> }) {
    const base = process.env.NEXT_PUBLIC_API_BASE;

      const { id } = await params;
    const res = await fetch(`${base}/forms/${id}/`, { cache: "no-store" });
    console.log(res);
    if (!res.ok) {
        throw new Error("No se pudo obtener el formulario");
    }

    const form: FormData = await res.json();

    return (
        <main style={{ padding: "2rem" }}>
            <h1>{form.name}</h1>
            <p>{form.description}</p>
            <DynamicFormClient form={form} />
        </main>
    );
}
