import { NextResponse } from "next/server";

// ALB のヘルスチェック用。API やテナントに依存せず、サーバーが応答できるかだけを返す。
// "/" はログイン利用者のテナントで API を呼ぶので、ヘルスチェックには使えない。
export const dynamic = "force-dynamic";

export function GET() {
  return NextResponse.json({ status: "ok" });
}
