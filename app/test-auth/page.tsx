"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function TestAuthPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect directly to agent page
    router.push("/agent");
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div>Redirecting to Agent...</div>
    </div>
  );
}
