"use client";
import React, { useState, useEffect } from "react";
import { Check } from "lucide-react";

interface CheckboxFieldProps {
    fieldId: number;
    label: string;
    required?: boolean;
    hasError?: boolean;
    defaultValue?: string;
    onChange?: (value: string) => void;
}

const CheckboxField: React.FC<CheckboxFieldProps> = ({
    fieldId,
    label,
    required,
    hasError,
    defaultValue = "",
    onChange,
}) => {
    const [selected, setSelected] = useState(defaultValue);

    const options = [
        { label: "SI", value: "SI" },
        { label: "NO", value: "NO" },
    ];

    useEffect(() => {
        onChange?.(selected);
    }, [selected]);

    return (
        <div className="mb-4">
            <label className="block text-gray-700 font-medium mb-2">
                {label} {required && <span className="text-red-500">*</span>}
            </label>

            <div className="sideBySide flex gap-4">
                {options.map((opt) => (
                    <span
                        key={opt.value}
                        onClick={() => setSelected(opt.value)}
                        className={`relative flex items-center justify-center w-28 h-12 border rounded-2xl cursor-pointer transition-all
                            ${selected === opt.value
                                ? "bg-blue-100 border-blue-500 shadow-md"
                                : "bg-white border-gray-300 hover:border-blue-300"
                            }
                            ${hasError ? "border-red-500" : ""}
                        `}
                    >
                        <em className="font-medium">{opt.label}</em>
                        {selected === opt.value && (
                            <Check
                                size={18}
                                className="text-blue-600 absolute right-3"
                            />
                        )}
                    </span>
                ))}
            </div>
        </div>
    );
};

export default CheckboxField;


