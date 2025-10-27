import React, { useRef, useState, useEffect } from "react";
import Webcam from "react-webcam";
import { FaCamera, FaPaperclip, FaTimes, FaFilePdf, FaFileAlt } from "react-icons/fa";

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
}

const FileInputCamera: React.FC<FileInputCameraProps> = ({
    fieldId,
    label,
    fileRefs,
    hasError,
    required
}) => {
    const webcamRef = useRef<Webcam | null>(null);
    const fileInputRef = useRef<HTMLInputElement | null>(null);
    const [files, setFiles] = useState<FileItem[]>([]);
    const [showCamera, setShowCamera] = useState(false);

    useEffect(() => {
        const currentFiles = fileRefs.current[fieldId] || [];
        setFiles(currentFiles);
    }, [fileRefs, fieldId]);

    const capture = () => {
        const imageSrc = webcamRef.current?.getScreenshot();
        if (imageSrc) {
            const blob = dataURLtoBlob(imageSrc);
            const file = new File([blob], "captura.jpg", { type: "image/jpeg" });
            const newFile: FileItem = { name: file.name, src: imageSrc, type: file.type, file };
            const updatedFiles = [...files, newFile];
            setFiles(updatedFiles);
            fileRefs.current[fieldId] = updatedFiles;
            setShowCamera(false);
        }
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFiles = e.target.files;
        if (!selectedFiles) return;

        Array.from(selectedFiles).forEach(f => {
            const reader = new FileReader();
            reader.onloadend = () => {
                const fileItem: FileItem = { name: f.name, src: reader.result as string, type: f.type, file: f };
                const updatedFiles = [...files, fileItem];
                setFiles(updatedFiles);
                fileRefs.current[fieldId] = updatedFiles;
            };

            if (f.type.startsWith("image/") || f.type === "application/pdf") {
                reader.readAsDataURL(f);
            } else {
                const fileItem: FileItem = { name: f.name, src: null, type: f.type, file: f };
                const updatedFiles = [...files, fileItem];
                setFiles(updatedFiles);
                fileRefs.current[fieldId] = updatedFiles;
            }
        });

        if (fileInputRef.current) fileInputRef.current.value = "";
    };

    const removeFile = (index: number) => {
        const updatedFiles = files.filter((_, i) => i !== index);
        setFiles(updatedFiles);
        fileRefs.current[fieldId] = updatedFiles;

        if (fileInputRef.current) fileInputRef.current.value = "";
    };

    function dataURLtoBlob(dataurl: string): Blob {
        const [header, data] = dataurl.split(",");
        const mime = header.match(/:(.*?);/)?.[1] || "image/png";
        const binary = atob(data);
        const array = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) array[i] = binary.charCodeAt(i);
        return new Blob([array], { type: mime });
    }

    const requiredMark = required ? <span className="text-red-500">*</span> : null;

    return (
        <div className="w-full flex flex-col gap-2 mb-4">
            <label className="block text-gray-700 font-medium mb-1">
                {label} {requiredMark}
            </label>

            <div
                className="flex items-center rounded-lg overflow-hidden shadow-sm bg-white"
                style={{ border: hasError ? "1px solid #f6abab" : "1px solid #d1d5db" }}
            >
                <div className="flex-grow px-3 py-2 text-gray-600 truncate">
                    {files.length === 0 ? "Seleccionar archivos" : `${files.length} archivo(s) seleccionado(s)`}
                </div>
                <div className="flex items-center bg-gray-50 border-l border-gray-200">
                    <button
                        type="button"
                        onClick={() => fileInputRef.current?.click()}
                        className="p-3 hover:bg-gray-100 transition"
                    >
                        <FaPaperclip className="text-gray-600 text-lg" />
                    </button>
                    <button
                        type="button"
                        onClick={() => setShowCamera(true)}
                        className="p-3 hover:bg-gray-100 transition"
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
                    <Webcam
                        ref={webcamRef}
                        audio={false}
                        screenshotFormat="image/jpeg"
                        videoConstraints={{ facingMode: "environment" }}
                        className="rounded-lg w-full aspect-video bg-black"
                    />
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
                            className="relative w-32 h-32 border border-gray-300 rounded-lg shadow-sm overflow-hidden"
                        >
                            {file.type?.startsWith("image/") && file.src ? (
                                <img src={file.src} alt={file.name} className="w-full h-full object-cover" />
                            ) : file.type === "application/pdf" ? (
                                <div className="flex flex-col items-center justify-center w-full h-full text-red-600">
                                    <FaFilePdf className="text-5xl mb-1" />
                                    <span className="text-xs text-gray-700 truncate w-28 text-center">
                                        {file.name}
                                    </span>
                                </div>
                            ) : (
                                <div className="flex flex-col items-center justify-center w-full h-full text-gray-600">
                                    <FaFileAlt className="text-4xl mb-1" />
                                    <span className="text-xs text-gray-700 truncate w-28 text-center">
                                        {file.name}
                                    </span>
                                </div>
                            )}

                            <button
                                onClick={() => removeFile(idx)}
                                className="absolute top-1 right-1 bg-white/80 hover:bg-red-500 hover:text-white text-gray-700 rounded-full p-1 shadow-md transition"
                                title="Eliminar archivo"
                            >
                                <FaTimes className="text-sm" />
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default FileInputCamera;


