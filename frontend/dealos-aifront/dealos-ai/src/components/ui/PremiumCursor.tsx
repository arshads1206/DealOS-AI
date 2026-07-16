import { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";

export function PremiumCursor() {
  const cursorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const cursor = cursorRef.current;
    if (!cursor) return;

    // Check if the device supports hover (ignore touch devices)
    if (window.matchMedia("(pointer: coarse)").matches) {
      cursor.style.display = "none";
      return;
    }

    let rafId: number;
    let mouseX = 0;
    let mouseY = 0;

    const onMouseMove = (e: MouseEvent) => {
      mouseX = e.clientX;
      mouseY = e.clientY;

      const target = e.target as HTMLElement;
      
      // Determine if hovering over an interactive element
      const isInteractive = !!target.closest(
        'a, button, input, textarea, select, [role="button"], .interactive, .clickable, label'
      );

      if (isInteractive) {
        cursor.classList.add("scale-[1.15]");
        cursor.classList.add("opacity-100");
        cursor.classList.remove("opacity-40");
      } else {
        cursor.classList.remove("scale-[1.15]");
        cursor.classList.remove("opacity-100");
        cursor.classList.add("opacity-40");
      }

      // Fast DOM update without React state overhead
      if (!rafId) {
        rafId = requestAnimationFrame(() => {
          cursor.style.transform = `translate3d(${mouseX}px, ${mouseY}px, 0)`;
          rafId = 0;
        });
      }
    };

    window.addEventListener("mousemove", onMouseMove, { passive: true });
    
    return () => {
      window.removeEventListener("mousemove", onMouseMove);
      if (rafId) cancelAnimationFrame(rafId);
    };
  }, []);

  return (
    <div
      ref={cursorRef}
      className={cn(
        "pointer-events-none fixed top-0 left-0 z-[99999] h-6 w-6 -ml-3 -mt-3 rounded-full",
        "bg-[var(--color-gold-500)]/15 blur-[3px]",
        "border border-[var(--color-gold-400)]/30",
        "shadow-[0_0_15px_3px_rgba(201,162,39,0.25)]",
        "transition-[scale,opacity] duration-200 ease-out opacity-0 hidden sm:block"
      )}
      style={{ willChange: "transform, scale" }}
    />
  );
}
