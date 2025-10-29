"use client";
import React, { useEffect, useState } from "react";
import { Check } from "lucide-react";

interface Option {
    label: string;
    value: string;
}

interface CheckboxFieldProps {
    fieldId: number;
    label: string;
    required?: boolean;
    hasError?: boolean;
    defaultValue?: string;
    options?: Option[];
    onChange?: (value: string) => void;
    resetTrigger?: number;
}

const CheckboxField: React.FC<CheckboxFieldProps> = ({
    fieldId,
    label,
    required,
    hasError,
    defaultValue = "",
    options = [
        { label: "SI", value: "SI" },
        { label: "NO", value: "NO" },
    ],
    onChange,
    resetTrigger = 0,
}) => {
    const [selected, setSelected] = useState(defaultValue);

    const handleSelect = (value: string) => {
        setSelected(value);
        onChange?.(value);
    };

    useEffect(() => {
        setSelected(defaultValue);
    }, [resetTrigger, defaultValue]);

    return (
        <div className="mb-4">
            <label className="block text-gray-700 font-medium mb-2">
                {label} {required && <span className="text-red-500">*</span>}
            </label>

            <div className="sideBySide flex gap-4 flex-wrap">
                {options.map((opt) => (
                    <span
                        key={opt.value}
                        onClick={() => handleSelect(opt.value)}
                        className={`relative flex items-center justify-center w-28 h-12 border rounded-2xl cursor-pointer transition-all
                            ${selected === opt.value
                                ? "bg-blue-100 border-blue-500 shadow-md"
                                : "bg-white border-gray-300 hover:border-blue-300"}
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


