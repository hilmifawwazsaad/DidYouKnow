import { useState, useEffect } from "react";
import { AnimatedThemeToggler } from "@/components/ui/animated-theme-toggler";
import { DottedMap } from "@/components/ui/dotted-map";

interface Fact {
  date: string;
  fact: string;
}

function App() {
  const [data, setData] = useState<Fact | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/data/latest.json")
      .then((res) => {
        if (!res.ok) throw new Error("Data belum tersedia");
        return res.json();
      })
      .then((json: Fact) => {
        setData(json);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="min-h-svh relative flex flex-col items-center justify-center px-6 md:px-12 lg:px-20 text-center">
      <div className="absolute inset-0 flex items-center justify-center overflow-hidden pointer-events-none">
        <div className="w-full aspect-2/1 scale-[3] md:scale-[1.5] lg:scale-100 opacity-30 dark:opacity-48">
          <DottedMap dotRadius={0.11} />
        </div>
      </div>
      <AnimatedThemeToggler
        className="fixed top-4 right-4 z-50 p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        variant="circle"
      />

      {loading && (
        <p className="text-xl md:text-2xl font-medium text-gray-400">
          Memuat...
        </p>
      )}

      {error && <p className="text-base md:text-lg text-gray-400">{error}</p>}

      {data && (
        <div className="relative z-10">
          <p className="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-medium text-gray-900 dark:text-white max-w-xs sm:max-w-lg md:max-w-2xl lg:max-w-4xl xl:max-w-6xl">
            {data.fact}
          </p>
        </div>
      )}
    </div>
  );
}

export default App;
