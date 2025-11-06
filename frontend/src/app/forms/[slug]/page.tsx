import DynamicFormClient from "@/components/DynamicFormClient";
import Image from "next/image";

interface Option {
    label: string;
    value: string;
}

interface FormField {
    id: number;
    name: string;
    label: string;
    field_type: string;
    required: number;
    options?: Option[];
    depends_on?: string | null;
    depends_value?: string | null;
    api_url?: string | null;
    min_search_chars?: number;
    result_key?: string | null;
    label_key?: string;
    value_key?: string;
    dynamic_options_url?: string | null;
    depends_on_field?: string | null;
    dynamic_result_key?: string | null;
}

interface FormData {
    id: number;
    name: string;
    description: string;
    fields: FormField[];
}

export default async function FormPage({ params }: { params: Promise<{ slug: string }> }) {
    const base = process.env.NEXT_PUBLIC_API_BASE;

    const { slug } = await params;
    const res = await fetch(`${base}/forms/${slug}/`, { cache: "no-store" });

    if (!res.ok) {
        throw new Error("No se pudo obtener el formulario");
    }

    const form: FormData = await res.json();

    return (
        <main className="p-4 md:p-8 lg:p-12">
            {/* Header */}
            <div className="bg-[#003886] border-gray-800 py-4 md:py-6 shadow-lg rounded-xl max-w-4xl mx-auto">
                <div className="px-4 sm:px-6 lg:px-8">
                    <div className="flex flex-col md:flex-row items-center gap-4 md:gap-8 justify-center">
                        {/* Logo */}
                        <div className="flex-shrink-0 order-2 md:order-1 w-32 md:w-48 lg:w-64">
                            <Image
                                src="/forms/logo.png"
                                alt="Logo Comfamiliar Risaralda"
                                width={200}
                                height={44}
                                priority
                                className="object-contain w-full h-auto"
                            />
                        </div>

                        {/* Título */}
                        <div className="flex-[2] text-center order-1 md:order-2">
                            <h2
                                role="heading"
                                aria-level={1}
                                className="m-0 text-white text-xl md:text-2xl lg:text-3xl font-bold uppercase tracking-tight md:tracking-wide leading-tight"
                            >
                                {form.description}
                            </h2>
                        </div>
                    </div>
                </div>
            </div>

            {/* Formulario */}
            <div className="max-w-4xl mx-auto">
                <div className="bg-white rounded-xl shadow-lg border border-gray-300 p-6 md:p-8">
                    <DynamicFormClient form={form} />
                </div>
            </div>
        </main>
    );
}