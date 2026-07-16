import { useEffect, useRef, useState } from "react";

/**
 * Reveals text word-by-word on mount to read as a streaming AI response.
 * Purely presentational — runs once per mount, no effect on message data.
 */
export function StreamingText({ text, speed = 18 }: { text: string; speed?: number }) {
  const words = useRef(text.split(" "));
  const [count, setCount] = useState(0);

  useEffect(() => {
    setCount(0);
    if (words.current.length === 0) return;
    let i = 0;
    const id = setInterval(() => {
      i += 1;
      setCount(i);
      if (i >= words.current.length) clearInterval(id);
    }, speed);
    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [text]);

  return <>{words.current.slice(0, count).join(" ")}</>;
}
