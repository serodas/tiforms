"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import Select from "react-select";

interface Option {
    label: string;
    value: string;
    [key: string]: any;
}

interface DynamicSelectFieldProps {
    fieldId: number;
    label: string;
    required: boolean;
    hasError: boolean;
    dependsOnField: string;
    dependsValue: string | null;
    dynamicOptionsUrl: string;
    dynamicResultKey?: string | null;
    labelKey: string;
    valueKey: string;
    onChange: (value: string) => void;
    onBlur: () => void;
    resetTrigger?: number;
}

export default function DynamicSelectField({
    fieldId,
    label,
    required,
    hasError,
    dependsOnField,
    dependsValue,
    dynamicOptionsUrl,
    dynamicResultKey,
    labelKey,
    valueKey,
    onChange,
    onBlur,
    resetTrigger = 0
}: DynamicSelectFieldProps) {
    const [options, setOptions] = useState<Option[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [selectedValue, setSelectedValue] = useState<string>("");
    const previousDependsValue = useRef<string | null>(null);
    const isMounted = useRef(true);

    // Función para cargar opciones - memoizada con useCallback
    const loadDynamicOptions = useCallback(async (currentDependsValue: string) => {
        if (!currentDependsValue) {
            setOptions([]);
            return;
        }

        setIsLoading(true);
        try {
            const base = process.env.NEXT_PUBLIC_API_BASE;
            const response = await fetch(
                `${base}${dynamicOptionsUrl}?search=${encodeURIComponent(currentDependsValue)}`
            );

            if (!response.ok) {
                throw new Error("Error al cargar opciones dinámicas");
            }

            const data = await response.json();

            // Navegar por la respuesta usando dynamicResultKey
            let results = data;
            if (dynamicResultKey) {
                const keys = dynamicResultKey.split('.');
                for (const key of keys) {
                    results = results?.[key];
                }
            }

            // Solo actualizar si el componente sigue montado y el dependsValue no ha cambiado
            if (isMounted.current && previousDependsValue.current === currentDependsValue) {
                if (Array.isArray(results)) {
                    const mappedOptions = results.map((item: any) => ({
                        value: item[valueKey]?.toString() || "",
                        label: item[labelKey]?.toString() || "",
                        rawData: item
                    }));
                    setOptions(mappedOptions);
                } else {
                    setOptions([]);
                }
            }
        } catch (error) {
            console.error("Error loading dynamic options:", error);
            if (isMounted.current) {
                setOptions([]);
            }
        } finally {
            if (isMounted.current) {
                setIsLoading(false);
            }
        }
    }, [fieldId, dynamicOptionsUrl, dynamicResultKey, labelKey, valueKey]);

    // Efecto principal - solo se ejecuta cuando dependsValue cambia realmente
    useEffect(() => {
        isMounted.current = true;

        // Solo hacer fetch si el dependsValue cambió y no es null/undefined
        if (dependsValue !== previousDependsValue.current) {
            // Resetear el valor seleccionado cuando cambia el documento
            if (previousDependsValue.current !== null) {
                setSelectedValue("");
                onChange("");
            }

            previousDependsValue.current = dependsValue;

            if (dependsValue) {
                loadDynamicOptions(dependsValue);
            } else {
                setOptions([]);
            }
        }

        return () => {
            isMounted.current = false;
        };
    }, [dependsValue, loadDynamicOptions, onChange]);

    // Efecto para reset completo
    useEffect(() => {
        if (resetTrigger > 0) {
            setSelectedValue("");
            setOptions([]);
            previousDependsValue.current = null;
        }
    }, [resetTrigger]);

    const handleChange = useCallback((selectedOption: Option | null) => {
        const value = selectedOption?.value || "";
        setSelectedValue(value);
        onChange(value);
    }, [onChange]);

    const customStyles = {
        control: (base: any, state: any) => ({
            ...base,
            borderColor: hasError ? "#f6abab" : state.isFocused ? "#3b82f6" : "#d1d5db",
            boxShadow: state.isFocused && !hasError ? "0 0 0 2px rgba(59, 130, 246, 0.2)" : "none",
            "&:hover": {
                borderColor: hasError ? "#f6abab" : "#9ca3af"
            },
            minHeight: "42px",
            backgroundColor: !dependsValue ? "#f9fafb" : "white",
            cursor: !dependsValue ? "not-allowed" : "default"
        }),
        menu: (base: any) => ({
            ...base,
            zIndex: 50
        }),
        option: (base: any, state: any) => ({
            ...base,
            backgroundColor: state.isSelected ? "#3b82f6" : state.isFocused ? "#eff6ff" : "white",
            color: state.isSelected ? "white" : "#374151",
            cursor: "pointer"
        }),
        singleValue: (base: any) => ({
            ...base,
            color: "#374151"
        }),
        placeholder: (base: any) => ({
            ...base,
            color: "#9ca3af"
        }),
        loadingIndicator: (base: any) => ({
            ...base,
            color: "#3b82f6"
        }),
        loadingMessage: (base: any) => ({
            ...base,
            color: "#6b7280"
        }),
        noOptionsMessage: (base: any) => ({
            ...base,
            color: "#6b7280"
        })
    };

    return (
        <div className="mb-4">
            <label className="block text-gray-700 font-medium mb-1">
                {label} {required && <span className="text-red-500">*</span>}
            </label>
            <Select
                options={options}
                value={options.find(opt => opt.value === selectedValue) || null}
                onChange={handleChange}
                onBlur={onBlur}
                isLoading={isLoading}
                styles={customStyles}
                isDisabled={!dependsValue || isLoading}
                placeholder={
                    !dependsValue
                        ? `Seleccione primero el documento`
                        : isLoading
                            ? "Cargando consecutivos..."
                            : options.length === 0
                                ? "No hay consecutivos disponibles"
                                : "Seleccione un consecutivo"
                }
                noOptionsMessage={() =>
                    !dependsValue
                        ? `Seleccione primero el documento`
                        : "No hay consecutivos disponibles"
                }
                loadingMessage={() => "Cargando..."}
                isClearable={false}
                isSearchable={false}
            />
            {hasError && (
                <p className="text-sm mt-1" style={{ color: "#f6abab" }}>
                    Este campo es obligatorio
                </p>
            )}
        </div>
    );
}