import { useEffect, useRef, useState } from "react";
import { useInView } from "framer-motion";

export function CountUp({
  value,
  duration = 1.2,
  formatter,
}: {
  value: number;
  duration?: number;
  formatter?: (v: number) => string;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-40px" });
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    if (!inView) return;
    let raf: number;
    const start = performance.now();
    const animate = (now: number) => {
      const progress = Math.min(1, (now - start) / (duration * 1000));
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(value * eased);
      if (progress < 1) raf = requestAnimationFrame(animate);
    };
    raf = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(raf);
  }, [inView, value, duration]);

  return <span ref={ref}>{formatter ? formatter(display) : Math.round(display).toLocaleString()}</span>;
}
