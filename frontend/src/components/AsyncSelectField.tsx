"use client";

import React, { useState, useCallback } from "react";
import AsyncSelect from "react-select/async";

interface Option {
    label: string;
    value: string;
    [key: string]: any;
}

interface AsyncSelectFieldProps {
    fieldId: number;
    label: string;
    required: boolean;
    hasError: boolean;
    apiUrl: string;
    minSearchChars: number;
    resultKey?: string | null;
    labelKey: string;
    valueKey: string;
    onChange: (value: string) => void;
    onBlur: () => void;
}

export default function AsyncSelectField({
    fieldId,
    label,
    required,
    hasError,
    apiUrl,
    minSearchChars,
    resultKey,
    labelKey,
    valueKey,
    onChange,
    onBlur
}: AsyncSelectFieldProps) {
    const [isLoading, setIsLoading] = useState(false);
    const [inputValue, setInputValue] = useState("");

    const loadOptions = useCallback(
        async (inputValue: string): Promise<Option[]> => {
            if (inputValue.length < minSearchChars) {
                return [];
            }

            setIsLoading(true);
            try {
                const base = process.env.NEXT_PUBLIC_API_BASE;
                const response = await fetch(
                    `${base}${apiUrl}?search=${encodeURIComponent(inputValue)}`
                );
                
                if (!response.ok) {
                    throw new Error("Error al cargar opciones");
                }

                const data = await response.json();

                let results = data;
                if (resultKey) {
                    const keys = resultKey.split('.');
                    for (const key of keys) {
                        results = results?.[key];
                    }
                }

                if (Array.isArray(results)) {
                    return results.map((item: any) => ({
                        value: item[valueKey]?.toString() || "",
                        label: item[labelKey]?.toString() || "",
                        rawData: item
                    }));
                }

                return [];
            } catch (error) {
                console.error("Error loading options:", error);
                return [];
            } finally {
                setIsLoading(false);
            }
        },
        [apiUrl, minSearchChars, resultKey, labelKey, valueKey]
    );

    const handleChange = (selectedOption: Option | null) => {
        onChange(selectedOption?.value || "");
    };

    const borderStyle = hasError 
        ? { borderColor: "#f6abab" } 
        : { borderColor: "#d1d5db" };

    const customStyles = {
        control: (base: any, state: any) => ({
            ...base,
            borderColor: hasError ? "#f6abab" : state.isFocused ? "#3b82f6" : "#d1d5db",
            boxShadow: state.isFocused && !hasError ? "0 0 0 2px rgba(59, 130, 246, 0.2)" : "none",
            "&:hover": {
                borderColor: hasError ? "#f6abab" : "#9ca3af"
            },
            minHeight: "42px"
        }),
        menu: (base: any) => ({
            ...base,
            zIndex: 50
        })
    };

    return (
        <div className="mb-4">
            <label className="block text-gray-700 font-medium mb-1">
                {label} {required && <span className="text-red-500">*</span>}
            </label>
            <AsyncSelect
                cacheOptions
                defaultOptions
                loadOptions={loadOptions}
                onInputChange={setInputValue}
                onChange={handleChange}
                onBlur={onBlur}
                isLoading={isLoading}
                styles={customStyles}
                placeholder={`Escriba al menos ${minSearchChars} caracteres...`}
                loadingMessage={({ inputValue }) => 
                    inputValue.length < minSearchChars 
                        ? `Escriba al menos ${minSearchChars} caracteres` 
                        : "Buscando..."
                }
                noOptionsMessage={({ inputValue }) =>
                    inputValue.length < minSearchChars
                        ? `Escriba al menos ${minSearchChars} caracteres`
                        : "No se encontraron resultados"
                }
            />
            {hasError && (
                <p className="text-sm mt-1" style={{ color: "#f6abab" }}>
                    Este campo es obligatorio
                </p>
            )}
        </div>
    );
}