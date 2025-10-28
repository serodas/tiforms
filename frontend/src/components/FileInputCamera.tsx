"use client";

import React, { useRef, useState, useEffect } from "react";
import Webcam from "react-webcam";
import {
    FaCamera,
    FaPaperclip,
    FaTimes,
    FaFilePdf,
    FaFileAlt,
    FaSearch,
} from "react-icons/fa";

export interface FileItem {
    name: string;
    src: string | null;
    type: string | null;
    file?: File;
}

interface FileInputCameraProps {
    fieldId: number;
    label: string;
    fileRefs: React.MutableRefObject<Record<number, FileItem[]>>;
    hasError?: boolean;
    required?: boolean;
    resetTrigger?: number;
}

const FileInputCamera: React.FC<FileInputCameraProps> = ({
    fieldId,
    label,
    fileRefs,
    hasError = false,
    required = false,
    resetTrigger = 0,
}) => {
    const webcamRef = useRef<Webcam | null>(null);
    const fileInputRef = useRef<HTMLInputElement | null>(null);
    const [files, setFiles] = useState<FileItem[]>([]);
    const [showCamera, setShowCamera] = useState(false);
    const [zoomImage, setZoomImage] = useState<string | null>(null);

    useEffect(() => {
        setFiles([]);
        fileRefs.current[fieldId] = [];
        setShowCamera(false);
        setZoomImage(null);
        if (fileInputRef.current) fileInputRef.current.value = "";
    }, [resetTrigger, fieldId, fileRefs]);

    useEffect(() => {
        fileRefs.current[fieldId] = files;
    }, [files, fieldId, fileRefs]);

    function dataURLtoBlob(dataurl: string): Blob {
        const [header, data] = dataurl.split(",");
        const mime = header.match(/:(.*?);/)?.[1] || "image/png";
        const binary = atob(data);
        const array = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) array[i] = binary.charCodeAt(i);
        return new Blob([array], { type: mime });
    }

    const capture = () => {
        const video = webcamRef.current?.video;
        if (!video) return;

        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageSrc = canvas.toDataURL("image/jpeg", 1);
        const blob = dataURLtoBlob(imageSrc);
        const file = new File([blob], "captura.jpg", { type: "image/jpeg" });
        addFile({ name: file.name, src: imageSrc, type: file.type, file });
        setShowCamera(false);
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selected = e.target.files;
        if (!selected) return;

        Array.from(selected).forEach((f) => {
            if (f.type.startsWith("image/") || f.type === "application/pdf") {
                const reader = new FileReader();
                reader.onloadend = () => {
                    addFile({
                        name: f.name,
                        src: reader.result as string,
                        type: f.type,
                        file: f,
                    });
                };
                reader.readAsDataURL(f);
            } else {
                addFile({ name: f.name, src: null, type: f.type, file: f });
            }
        });

        if (fileInputRef.current) fileInputRef.current.value = "";
    };

    const addFile = (file: FileItem) => setFiles((prev) => [...prev, file]);

    const removeFile = (index: number) => {
        setFiles((prev) => prev.filter((_, i) => i !== index));
        if (fileInputRef.current) fileInputRef.current.value = "";
    };

    const requiredMark = required ? (
        <span className="text-red-500">*</span>
    ) : null;

    return (
        <div className="w-full flex flex-col gap-2 mb-4">
            <label className="block text-gray-700 font-medium mb-1">
                {label} {requiredMark}
            </label>

            <div
                className="flex items-center rounded-lg overflow-hidden shadow-sm bg-white w-full h-18"
                style={{
                    border: hasError
                        ? "1px dashed #f6abab"
                        : "1px dashed #d1d5db",
                }}
            >
                <div className="flex-grow px-3 py-2 text-gray-600 truncate">
                    {files.length === 0
                        ? "Seleccionar archivos"
                        : `${files.length} archivo(s) seleccionado(s)`}
                </div>
                <div className="flex items-center">
                    <button
                        type="button"
                        onClick={() => fileInputRef.current?.click()}
                        className="p-3 hover:bg-gray-100 transition"
                        title="Subir archivo"
                    >
                        <FaPaperclip className="text-gray-600 text-lg" />
                    </button>
                    <button
                        type="button"
                        onClick={() => setShowCamera(true)}
                        className="p-3 hover:bg-gray-100 transition"
                        title="Usar cámara"
                    >
                        <FaCamera className="text-gray-600 text-lg" />
                    </button>
                </div>
            </div>

            {hasError && (
                <p className="text-sm mt-1" style={{ color: "#f6abab" }}>
                    Este campo es obligatorio
                </p>
            )}

            <input
                ref={fileInputRef}
                type="file"
                accept="*"
                multiple
                onChange={handleFileChange}
                className="hidden"
            />

            {showCamera && (
                <div className="flex flex-col items-center border border-gray-200 rounded-lg overflow-hidden bg-gray-50 mt-2">
                    <div className="w-full" style={{ aspectRatio: "16/9" }}>
                        <Webcam
                            ref={webcamRef}
                            audio={false}
                            screenshotFormat="image/jpeg"
                            videoConstraints={{
                                facingMode: "environment",
                                width: 1920,
                                height: 1080,
                            }}
                            className="w-full h-full object-contain bg-black rounded-lg"
                        />
                    </div>
                    <div className="flex gap-2 py-3">
                        <button
                            onClick={capture}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg shadow-md transition"
                        >
                            Capturar
                        </button>
                        <button
                            onClick={() => setShowCamera(false)}
                            className="bg-gray-400 hover:bg-gray-500 text-white px-4 py-2 rounded-lg shadow-md transition"
                        >
                            Cancelar
                        </button>
                    </div>
                </div>
            )}

            {files.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                    {files.map((file, idx) => (
                        <div
                            key={idx}
                            className="relative w-28 h-28 border border-gray-300 rounded-lg shadow-sm overflow-hidden flex flex-col items-center justify-center p-2 cursor-pointer group"
                            onClick={() => file.src && setZoomImage(file.src)}
                        >
                            {file.type?.startsWith("image/") && file.src ? (
                                <img
                                    src={file.src}
                                    alt={file.name}
                                    className="w-full h-full object-contain rounded"
                                />
                            ) : file.type === "application/pdf" ? (
                                <FaFilePdf className="text-3xl text-red-600" />
                            ) : (
                                <FaFileAlt className="text-3xl text-gray-600" />
                            )}

                            <div className="text-xs text-gray-700 text-center mt-1">
                                <span className="truncate">{file.name}</span>
                                {file.file?.size && (
                                    <span className="text-gray-500">
                                        {(file.file.size / 1024).toFixed(1)} KB
                                    </span>
                                )}
                            </div>

                            {file.src && (
                                <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 flex items-center justify-center transition">
                                    <FaSearch className="text-white text-xl" />
                                </div>
                            )}

                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    removeFile(idx);
                                }}
                                className="absolute top-1 right-1 bg-white/80 hover:bg-red-500 hover:text-white text-gray-700 rounded-full p-1 shadow-md transition"
                                title="Eliminar archivo"
                            >
                                <FaTimes className="text-sm" />
                            </button>
                        </div>
                    ))}
                </div>
            )}

            {zoomImage && (
                <div
                    className="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
                    onClick={() => setZoomImage(null)}
                >
                    <img
                        src={zoomImage}
                        className="max-h-[90%] max-w-[90%] rounded-lg shadow-lg"
                        alt="Zoom"
                    />
                </div>
            )}
        </div>
    );
};

export default FileInputCamera;

