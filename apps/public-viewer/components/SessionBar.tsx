"use client";

import { useEffect, useState } from "react";

type SessionMe = {
  tenantId: string | null;
  displayName: string | null;
  count: number;
};

export function SessionBar() {
  const [session, setSession] = useState<SessionMe | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const response = await fetch("/session/me", { credentials: "include" });
        if (!response.ok) return;
        setSession((await response.json()) as SessionMe);
      } catch {
        // ローカル起動では選択画面が無い
      }
    };
    load();
  }, []);

  if (!session?.tenantId) return null;
  const returnTo = encodeURIComponent(window.location.href);

  return (
    <nav
      aria-label="テナント"
      style={{
        display: "flex",
        justifyContent: "flex-end",
        gap: "16px",
        padding: "12px 24px",
        fontSize: "14px",
      }}
    >
      <span>{session.displayName}</span>
      {session.count > 1 ? (
        <a href={`/session?switch=1&return=${returnTo}`}>切り替える</a>
      ) : null}
      <a href="/logout">ログアウト</a>
    </nav>
  );
}
