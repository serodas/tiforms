"use client";

import React, {
    useEffect,
    useRef,
    useImperativeHandle,
    forwardRef,
    MouseEvent,
    TouchEvent,
} from "react";
import { FaTimes } from "react-icons/fa";

export interface SignaturePadHandle {
    clear: () => void;
    getDataURL: () => string | null;
    isSigned: () => boolean;
}

interface SignaturePadProps {
    hasError?: boolean;
    resetTrigger?: number;
}

const SignaturePad = forwardRef<SignaturePadHandle, SignaturePadProps>(
    ({ hasError = false, resetTrigger = 0 }, ref) => {
        const canvasRef = useRef<HTMLCanvasElement | null>(null);
        const ctxRef = useRef<CanvasRenderingContext2D | null>(null);
        const drawing = useRef(false);
        const hasSignature = useRef(false);

        /** 🔹 Inicializa el canvas y contexto */
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
                const { offsetWidth, offsetHeight } = canvas;
                canvas.width = offsetWidth * ratio;
                canvas.height = offsetHeight * ratio;
                ctx.scale(ratio, ratio);
                ctx.lineWidth = 2;
            };

            resizeCanvas();
            window.addEventListener("resize", resizeCanvas);
            return () => window.removeEventListener("resize", resizeCanvas);
        }, []);

        /** 🔹 Limpia el canvas cuando cambia resetTrigger */
        useEffect(() => {
            clearCanvas();
        }, [resetTrigger]);

        /** 🔹 Inicia dibujo */
        function startDrawing(e: MouseEvent<HTMLCanvasElement> | TouchEvent<HTMLCanvasElement>) {
            const ctx = ctxRef.current;
            const canvas = canvasRef.current;
            if (!ctx || !canvas) return;

            drawing.current = true;
            hasSignature.current = true;

            const { x, y } = getPosition(e, canvas);
            ctx.beginPath();
            ctx.moveTo(x, y);
        }

        /** 🔹 Dibuja mientras se arrastra */
        function draw(e: MouseEvent<HTMLCanvasElement> | TouchEvent<HTMLCanvasElement>) {
            if (!drawing.current) return;
            const ctx = ctxRef.current;
            const canvas = canvasRef.current;
            if (!ctx || !canvas) return;

            const { x, y } = getPosition(e, canvas);
            ctx.lineTo(x, y);
            ctx.stroke();
        }

        /** 🔹 Termina el trazo */
        function stopDrawing() {
            drawing.current = false;
        }

        /** 🔹 Obtiene posición (mouse o touch) */
        function getPosition(
            e: MouseEvent<HTMLCanvasElement> | TouchEvent<HTMLCanvasElement>,
            canvas: HTMLCanvasElement
        ) {
            const rect = canvas.getBoundingClientRect();
            if ("touches" in e && e.touches[0]) {
                const touch = e.touches[0];
                return { x: touch.clientX - rect.left, y: touch.clientY - rect.top };
            }
            return { x: (e as MouseEvent).clientX - rect.left, y: (e as MouseEvent).clientY - rect.top };
        }

        /** 🔹 Limpia el canvas */
        function clearCanvas() {
            const canvas = canvasRef.current;
            const ctx = ctxRef.current;
            if (canvas && ctx) {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                hasSignature.current = false;
            }
        }

        /** 🔹 Expone API pública al padre */
        useImperativeHandle(ref, () => ({
            clear: clearCanvas,
            getDataURL: () => canvasRef.current?.toDataURL("image/png") ?? null,
            isSigned: () => hasSignature.current,
        }));

        return (
            <div className="relative flex flex-col space-y-2">
                <canvas
                    ref={canvasRef}
                    onMouseDown={startDrawing}
                    onMouseMove={draw}
                    onMouseUp={stopDrawing}
                    onMouseLeave={stopDrawing}
                    onTouchStart={startDrawing}
                    onTouchMove={draw}
                    onTouchEnd={stopDrawing}
                    className="signature-canvas w-full h-40 rounded-md border bg-white"
                    style={{
                        borderColor: hasError ? "#f6abab" : "#d1d5db",
                        touchAction: "none", // previene scroll en móviles al dibujar
                    }}
                />
                <button
                    type="button"
                    onClick={clearCanvas}
                    className="absolute bottom-2 right-2 p-2 bg-white/80 hover:bg-red-500 hover:text-white text-gray-600 rounded-full shadow-md transition"
                    title="Limpiar firma"
                >
                    <FaTimes className="text-lg" />
                </button>
            </div>
        );
    }
);

SignaturePad.displayName = "SignaturePad";
export default SignaturePad;

