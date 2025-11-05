"use client";

import React, { useState, useCallback, useRef, useEffect } from "react";
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
    debounceDelay?: number;
    resetTrigger?: number; // Nueva prop
}

// Función debounce mejorada
function debounce<T extends (...args: any[]) => any>(
    func: T,
    delay: number
): (...args: Parameters<T>) => void {
    let timeoutId: NodeJS.Timeout;
    return (...args: Parameters<T>) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(null, args), delay);
    };
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
    onBlur,
    debounceDelay = 300,
    resetTrigger = 0 // Valor por defecto
}: AsyncSelectFieldProps) {
    const [isLoading, setIsLoading] = useState(false);
    const [selectedValue, setSelectedValue] = useState<Option | null>(null);
    const abortControllerRef = useRef<AbortController | null>(null);
    const asyncSelectRef = useRef<any>(null);

    // Función para cancelar la request anterior
    const cancelPreviousRequest = useCallback(() => {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            abortControllerRef.current = null;
        }
    }, []);

    // Resetear el campo cuando cambie resetTrigger
    useEffect(() => {
        if (resetTrigger > 0) {
            setSelectedValue(null);
            if (asyncSelectRef.current) {
                asyncSelectRef.current.clearValue();
            }
            cancelPreviousRequest();
            setIsLoading(false);
        }
    }, [resetTrigger, cancelPreviousRequest]);

    const loadOptionsReal = useCallback(
        async (inputValue: string): Promise<Option[]> => {
            if (inputValue.length < minSearchChars) {
                return [];
            }

            // Cancelar request anterior antes de iniciar una nueva
            cancelPreviousRequest();

            setIsLoading(true);

            // Crear nuevo AbortController para esta request
            const abortController = new AbortController();
            abortControllerRef.current = abortController;

            try {
                const base = process.env.NEXT_PUBLIC_API_BASE;
                const response = await fetch(
                    `${base}${apiUrl}?search=${encodeURIComponent(inputValue)}`,
                    {
                        signal: abortController.signal
                    }
                );

                // Si la request fue cancelada, no hacer nada
                if (abortController.signal.aborted) {
                    return [];
                }

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
            } catch (error: any) {
                // Solo mostrar error si no fue por cancelación
                if (error.name !== 'AbortError') {
                    console.error("Error loading options:", error);
                }
                return [];
            } finally {
                // Solo limpiar el loading state si esta request no fue cancelada
                // y si todavía somos el controller actual
                if (abortControllerRef.current === abortController && !abortController.signal.aborted) {
                    setIsLoading(false);
                    abortControllerRef.current = null;
                }
            }
        },
        [apiUrl, minSearchChars, resultKey, labelKey, valueKey, cancelPreviousRequest]
    );

    // Versión con debounce de loadOptions
    const loadOptions = useCallback(
        debounce(async (inputValue: string, callback: (options: Option[]) => void) => {
            const options = await loadOptionsReal(inputValue);
            callback(options);
        }, debounceDelay),
        [loadOptionsReal, debounceDelay]
    );

    const handleChange = (selectedOption: Option | null) => {
        setSelectedValue(selectedOption);
        onChange(selectedOption?.value || "");
    };

    // Cancelar requests pendientes cuando el componente se desmonte
    React.useEffect(() => {
        return () => {
            cancelPreviousRequest();
        };
    }, [cancelPreviousRequest]);

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
                ref={asyncSelectRef}
                cacheOptions
                defaultOptions
                loadOptions={loadOptions}
                onChange={handleChange}
                onBlur={onBlur}
                value={selectedValue}
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