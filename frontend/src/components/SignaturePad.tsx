"use client";

import React, {
    useEffect,
    useRef,
    useImperativeHandle,
    forwardRef,
} from "react";
import { FaTimes } from "react-icons/fa";

export interface SignaturePadHandle {
    clear: () => void;
    getDataURL: () => string | null;
    isSigned: () => boolean;
}

interface SignaturePadProps {
    hasError?: boolean;
}

const SignaturePad = forwardRef<SignaturePadHandle, SignaturePadProps>(({ hasError }, ref) => {
    const canvasRef = useRef<HTMLCanvasElement | null>(null);
    const ctxRef = useRef<CanvasRenderingContext2D | null>(null);
    const drawing = useRef(false);
    const hasSignature = useRef(false);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        if (!ctx) return;
        ctx.lineWidth = 2;
        ctx.lineCap = "round";
        ctx.strokeStyle = "#111827";
        ctxRef.current = ctx;

        const resizeCanvas = () => {
            const ratio = window.devicePixelRatio || 1;
            canvas.width = canvas.offsetWidth * ratio;
            canvas.height = canvas.offsetHeight * ratio;
            ctx.scale(ratio, ratio);
            ctx.lineWidth = 2;
        };

        resizeCanvas();
        window.addEventListener("resize", resizeCanvas);
        return () => window.removeEventListener("resize", resizeCanvas);
    }, []);

    function startDrawing(e: React.MouseEvent<HTMLCanvasElement>) {
        const ctx = ctxRef.current;
        if (!ctx) return;
        drawing.current = true;
        hasSignature.current = true;
        const rect = e.currentTarget.getBoundingClientRect();
        ctx.beginPath();
        ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
    }

    function draw(e: React.MouseEvent<HTMLCanvasElement>) {
        if (!drawing.current) return;
        const ctx = ctxRef.current;
        if (!ctx) return;
        const rect = e.currentTarget.getBoundingClientRect();
        ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top);
        ctx.stroke();
    }

    function stopDrawing() {
        drawing.current = false;
    }

    useImperativeHandle(ref, () => ({
        clear() {
            const canvas = canvasRef.current;
            const ctx = ctxRef.current;
            if (canvas && ctx) {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                hasSignature.current = false;
            }
        },
        getDataURL() {
            const canvas = canvasRef.current;
            return canvas ? canvas.toDataURL("image/png") : null;
        },
        isSigned() {
            return hasSignature.current;
        },
    }));

    return (
        <div className="relative flex flex-col space-y-2">
            <canvas
                ref={canvasRef}
                onMouseDown={startDrawing}
                onMouseMove={draw}
                onMouseUp={stopDrawing}
                onMouseLeave={stopDrawing}
                className="signature-canvas w-full h-40 rounded-md border"
                style={{
                    borderColor: hasError ? "#f6abab" : "#d1d5db",
                }}
            />
            {/* Botón flotante en la esquina superior derecha */}
            <button
                type="button"
                onClick={() => ref && (ref as any).current?.clear()}
                className="absolute bottom-2 right-2 p-2 bg-white/80 hover:bg-red-500 hover:text-white text-gray-600 rounded-full shadow-md transition"
                title="Limpiar firma"
            >
                <FaTimes className="text-lg" />
            </button>
        </div>
    );
});

SignaturePad.displayName = "SignaturePad";
export default SignaturePad;
