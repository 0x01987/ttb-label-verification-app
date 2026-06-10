"use client";

import { useState } from "react";

type VerificationResponse = {
  filename: string;
  ocr_text: string;
  verification: {
    expected: {
      brand_name: string;
      abv: string;
      net_contents: string;
    };
    found: {
      brand_name: string | null;
      abv: string | null;
      net_contents: string | null;
      government_warning: {
        found: boolean;
        matched_parts: string[];
      };
    };
    checks: {
      brand_name: { match: boolean; score: number };
      abv: { match: boolean; score: number };
      net_contents: { match: boolean; score: number };
      government_warning: { match: boolean; score: number };
    };
    compliance_score: number;
    overall_status: string;
  };
};

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [brandName, setBrandName] = useState("MALT & HOP");
  const [abv, setAbv] = useState("5%");
  const [netContents, setNetContents] = useState("1 PINT");
  const [result, setResult] = useState<VerificationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setResult(null);

    if (!file) {
      setError("Please upload a label image.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("brand_name", brandName);
    formData.append("abv", abv);
    formData.append("net_contents", netContents);

    try {
      setLoading(true);

      const response = await fetch("https://ttb-label-verification-app-api.onrender.com/verify", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Verification request failed.");
      }

      const data = await response.json();
      setResult(data);
    } catch {
      setError("Unable to verify label. Make sure the deployed API is reachable.");
    } finally {
      setLoading(false);
    }
  }

  const status = result?.verification.overall_status;
  const score = result?.verification.compliance_score;

  return (
    <main className="min-h-screen bg-slate-100 p-6 text-slate-900">
      <div className="mx-auto max-w-6xl">
        <header className="mb-8">
          <p className="text-sm font-semibold uppercase tracking-wide text-blue-700">
            AI-Powered Compliance Prototype
          </p>
          <h1 className="mt-2 text-4xl font-bold">
            TTB Label Verification App
          </h1>
          <p className="mt-3 max-w-3xl text-slate-600">
            Upload an alcohol label, enter expected application values, and verify
            whether the label matches required compliance fields.
          </p>
        </header>

        <div className="grid gap-6 lg:grid-cols-2">
          <section className="rounded-xl bg-white p-6 shadow">
            <h2 className="text-xl font-semibold">Application Data</h2>
            <p className="mt-1 text-sm text-slate-500">
              These fields represent the values submitted in the label application.
            </p>

            <form onSubmit={handleSubmit} className="mt-6 space-y-4">
              <div>
                <label className="block text-sm font-medium">Label Image</label>
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/jpg"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  className="mt-2 w-full rounded-lg border border-slate-300 p-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium">Brand Name</label>
                <input
                  value={brandName}
                  onChange={(e) => setBrandName(e.target.value)}
                  className="mt-2 w-full rounded-lg border border-slate-300 p-3"
                  placeholder="OLD TOM DISTILLERY"
                />
              </div>

              <div>
                <label className="block text-sm font-medium">Alcohol Content</label>
                <input
                  value={abv}
                  onChange={(e) => setAbv(e.target.value)}
                  className="mt-2 w-full rounded-lg border border-slate-300 p-3"
                  placeholder="45%"
                />
              </div>

              <div>
                <label className="block text-sm font-medium">Net Contents</label>
                <input
                  value={netContents}
                  onChange={(e) => setNetContents(e.target.value)}
                  className="mt-2 w-full rounded-lg border border-slate-300 p-3"
                  placeholder="750 mL"
                />
              </div>

              {error && (
                <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-lg bg-blue-700 px-4 py-3 font-semibold text-white hover:bg-blue-800 disabled:bg-slate-400"
              >
                {loading ? "Verifying..." : "Verify Label"}
              </button>
            </form>
          </section>

          <section className="rounded-xl bg-white p-6 shadow">
            <h2 className="text-xl font-semibold">Verification Result</h2>

            {!result && (
              <div className="mt-6 rounded-lg border border-dashed border-slate-300 p-8 text-center text-slate-500">
                Upload a label and run verification to see results.
              </div>
            )}

            {result && (
              <div className="mt-6 space-y-5">
                <div
                  className={`rounded-xl p-5 ${
                    status === "PASS"
                      ? "bg-green-50 text-green-800"
                      : "bg-yellow-50 text-yellow-800"
                  }`}
                >
                  <p className="text-sm font-medium">Overall Status</p>
                  <p className="mt-1 text-3xl font-bold">{status}</p>
                  <p className="mt-1 text-sm">Compliance Score: {score}%</p>
                </div>

                <div className="overflow-hidden rounded-lg border border-slate-200">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-slate-50">
                      <tr>
                        <th className="p-3">Field</th>
                        <th className="p-3">Expected</th>
                        <th className="p-3">Found</th>
                        <th className="p-3">Result</th>
                      </tr>
                    </thead>
                    <tbody>
                      <ResultRow
                        field="Brand Name"
                        expected={result.verification.expected.brand_name}
                        found={result.verification.found.brand_name}
                        check={result.verification.checks.brand_name}
                      />
                      <ResultRow
                        field="ABV"
                        expected={result.verification.expected.abv}
                        found={result.verification.found.abv}
                        check={result.verification.checks.abv}
                      />
                      <ResultRow
                        field="Net Contents"
                        expected={result.verification.expected.net_contents}
                        found={result.verification.found.net_contents}
                        check={result.verification.checks.net_contents}
                      />
                      <ResultRow
                        field="Government Warning"
                        expected="Required"
                        found={
                          result.verification.found.government_warning.found
                            ? "Detected"
                            : "Missing"
                        }
                        check={result.verification.checks.government_warning}
                      />
                    </tbody>
                  </table>
                </div>

                <div>
                  <h3 className="font-semibold">OCR Text</h3>
                  <pre className="mt-2 max-h-72 overflow-auto rounded-lg bg-slate-900 p-4 text-sm text-slate-100">
                    {result.ocr_text}
                  </pre>
                </div>
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}

function ResultRow({
  field,
  expected,
  found,
  check,
}: {
  field: string;
  expected: string;
  found: string | null;
  check: { match: boolean; score: number };
}) {
  return (
    <tr className="border-t border-slate-200">
      <td className="p-3 font-medium">{field}</td>
      <td className="p-3">{expected}</td>
      <td className="p-3">{found || "Not detected"}</td>
      <td className="p-3">
        <span
          className={`rounded-full px-3 py-1 text-xs font-semibold ${
            check.match
              ? "bg-green-100 text-green-700"
              : "bg-yellow-100 text-yellow-700"
          }`}
        >
          {check.match ? "PASS" : "REVIEW"} ({check.score})
        </span>
      </td>
    </tr>
  );
}