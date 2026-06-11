"use client";

import { useState } from "react";

const API_URL = "https://ttb-label-verification-app-api.onrender.com";

type VerificationResponse = {
  filename: string;
  ocr_text: string;
  verification: {
    expected: Record<string, string>;
    found: {
      brand_name: string | null;
      class_type: string | null;
      abv: string | null;
      net_contents: string | null;
      producer: string | null;
      country_of_origin: string | null;
      government_warning: {
        found: boolean;
        matched_parts: string[];
      };
    };
    checks: Record<string, { match: boolean; score: number }>;
    compliance_score: number;
    overall_status: string;
  };
};

type BatchResponse = {
  total_files: number;
  results: {
    filename: string;
    overall_status: string;
    compliance_score: number;
  }[];
};

export default function Home() {
  const [files, setFiles] = useState<File[]>([]);
  const [brandName, setBrandName] = useState("");
  const [classType, setClassType] = useState("");
  const [abv, setAbv] = useState("");
  const [netContents, setNetContents] = useState("");
  const [producer, setProducer] = useState("");
  const [countryOfOrigin, setCountryOfOrigin] = useState("");
  const [result, setResult] = useState<VerificationResponse | null>(null);
  const [batchResult, setBatchResult] = useState<BatchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function buildFormData() {
    const formData = new FormData();
    formData.append("brand_name", brandName);
    formData.append("class_type", classType);
    formData.append("abv", abv);
    formData.append("net_contents", netContents);
    formData.append("producer", producer);
    formData.append("country_of_origin", countryOfOrigin);
    return formData;
  }

  async function handleSingleVerify(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setResult(null);
    setBatchResult(null);

    if (files.length === 0) {
      setError("Please upload a label image.");
      return;
    }

    const formData = buildFormData();
    formData.append("file", files[0]);

    try {
      setLoading(true);

      const response = await fetch(`${API_URL}/verify`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Verification failed.");
      }

      const data = await response.json();
      setResult(data);
    } catch {
      setError("Unable to scan label. Make sure the deployed API is reachable.");
    } finally {
      setLoading(false);
    }
  }

  async function handleBatchVerify() {
    setError("");
    setResult(null);
    setBatchResult(null);

    if (files.length === 0) {
      setError("Please upload one or more label images.");
      return;
    }

    const formData = buildFormData();

    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      setLoading(true);

      const response = await fetch(`${API_URL}/batch-verify`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Batch verification failed.");
      }

      const data = await response.json();
      setBatchResult(data);
    } catch {
      setError("Unable to process batch. Make sure the deployed API is reachable.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-100 p-6 text-slate-900">
      <div className="mx-auto max-w-7xl">
        <header className="mb-8">
          <p className="text-sm font-semibold uppercase tracking-wide text-blue-700">
            AI-Powered Compliance Prototype
          </p>
          <h1 className="mt-2 text-4xl font-bold">
            TTB Label Verification App
          </h1>
          <p className="mt-3 max-w-3xl text-slate-600">
            Upload an alcohol beverage label to automatically extract and validate
            key TTB-required label elements. Application data may be entered
            optionally for comparison and verification.
          </p>
        </header>

        <div className="grid gap-6 lg:grid-cols-2">
          <section className="rounded-xl bg-white p-6 shadow">
            <h2 className="text-xl font-semibold">Scan Alcohol Label</h2>
            <p className="mt-1 text-sm text-slate-500">
              Upload a label image first. Application data is optional and can be
              used to compare OCR results against submitted values.
            </p>

            <form onSubmit={handleSingleVerify} className="mt-6 space-y-4">
              <div>
                <label className="block text-sm font-medium">
                  Alcohol Label Image
                </label>

                <label className="mt-2 flex min-h-[180px] cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 p-6 text-center transition hover:border-blue-400 hover:bg-blue-50">
                  <div className="text-4xl">📄</div>

                  <div className="mt-3 text-lg font-semibold text-slate-700">
                    {files.length > 0
                      ? `${files.length} file(s) selected`
                      : "Click here to upload label image(s)"}
                  </div>

                  <div className="mt-2 text-sm text-slate-500">
                    PNG, JPG, or JPEG supported. Multiple files allowed for batch review.
                  </div>

                  <input
                    type="file"
                    multiple
                    accept="image/png,image/jpeg,image/jpg"
                    onChange={(e) =>
                      setFiles(Array.from(e.target.files || []))
                    }
                    className="hidden"
                  />
                </label>

                {files.length > 0 && (
                  <div className="mt-3 rounded-lg bg-green-50 p-3">
                    <div className="mb-2 text-sm font-semibold text-green-700">
                      ✓ Selected Files
                    </div>
                    <ul className="space-y-1 text-sm text-green-700">
                      {files.map((file) => (
                        <li key={file.name}>{file.name}</li>
                      ))}
                    </ul>

                    <button
                      type="button"
                      onClick={() => setFiles([])}
                      className="mt-3 text-sm font-medium text-red-600 hover:text-red-700"
                    >
                      Remove all
                    </button>
                  </div>
                )}
              </div>

              <div className="rounded-lg bg-blue-50 p-4 text-sm text-blue-800">
                Optional: Enter application values below to compare OCR results
                against submitted label application data. Leave fields blank to
                scan and extract label information only.
              </div>

              <Input
                label="Brand Name"
                value={brandName}
                setValue={setBrandName}
                placeholder="OLD TOM DISTILLERY"
              />
              <Input
                label="Class / Type Designation"
                value={classType}
                setValue={setClassType}
                placeholder="Kentucky Straight Bourbon Whiskey"
              />
              <Input
                label="Alcohol Content"
                value={abv}
                setValue={setAbv}
                placeholder="45%"
              />
              <Input
                label="Net Contents"
                value={netContents}
                setValue={setNetContents}
                placeholder="750 mL"
              />
              <Input
                label="Producer / Bottler"
                value={producer}
                setValue={setProducer}
                placeholder="Bottled by Old Tom Distillery"
              />
              <Input
                label="Country of Origin"
                value={countryOfOrigin}
                setValue={setCountryOfOrigin}
                placeholder="Product of Mexico"
              />

              {error && (
                <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
                  {error}
                </div>
              )}

              <div className="grid gap-3 md:grid-cols-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="rounded-lg bg-blue-700 px-4 py-3 font-semibold text-white hover:bg-blue-800 disabled:bg-slate-400"
                >
                  {loading ? "Scanning..." : "Scan & Verify Label"}
                </button>

                <button
                  type="button"
                  disabled={loading}
                  onClick={handleBatchVerify}
                  className="rounded-lg bg-slate-800 px-4 py-3 font-semibold text-white hover:bg-slate-900 disabled:bg-slate-400"
                >
                  {loading ? "Processing..." : "Batch Scan"}
                </button>
              </div>
            </form>
          </section>

          <section className="rounded-xl bg-white p-6 shadow">
            <h2 className="text-xl font-semibold">Scan Result</h2>

            {!result && !batchResult && (
              <div className="mt-6 rounded-lg border border-dashed border-slate-300 p-8 text-center text-slate-500">
                Upload label image(s) and run scan to see detected fields and
                verification results.
              </div>
            )}

            {result && <SingleResult result={result} />}

            {batchResult && (
              <div className="mt-6">
                <div className="rounded-xl bg-blue-50 p-5 text-blue-800">
                  <p className="text-sm font-medium">Batch Processed</p>
                  <p className="mt-1 text-3xl font-bold">
                    {batchResult.total_files} file(s)
                  </p>
                </div>

                <div className="mt-5 overflow-hidden rounded-lg border border-slate-200">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-slate-50">
                      <tr>
                        <th className="p-3">Filename</th>
                        <th className="p-3">Status</th>
                        <th className="p-3">Score</th>
                      </tr>
                    </thead>
                    <tbody>
                      {batchResult.results.map((item) => (
                        <tr key={item.filename} className="border-t border-slate-200">
                          <td className="p-3 font-medium">{item.filename}</td>
                          <td className="p-3">{item.overall_status}</td>
                          <td className="p-3">{item.compliance_score}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}

function Input({
  label,
  value,
  setValue,
  placeholder,
}: {
  label: string;
  value: string;
  setValue: (value: string) => void;
  placeholder: string;
}) {
  return (
    <div>
      <label className="block text-sm font-medium">{label}</label>
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        className="mt-2 w-full rounded-lg border border-slate-300 p-3"
        placeholder={placeholder}
      />
    </div>
  );
}

function SingleResult({ result }: { result: VerificationResponse }) {
  const status = result.verification.overall_status;
  const score = result.verification.compliance_score;
  const found = result.verification.found;

  return (
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

      <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
        <h3 className="mb-3 font-semibold">Detected Label Information</h3>

        <div className="grid gap-2 text-sm">
          <DetectedField label="Brand" value={found.brand_name} />
          <DetectedField label="Class / Type" value={found.class_type} />
          <DetectedField label="ABV" value={found.abv} />
          <DetectedField label="Net Contents" value={found.net_contents} />
          <DetectedField label="Producer / Bottler" value={found.producer} />
          <DetectedField label="Country of Origin" value={found.country_of_origin} />
          <DetectedField
            label="Government Warning"
            value={found.government_warning.found ? "Detected" : "Missing"}
          />
        </div>
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
              found={found.brand_name}
              check={result.verification.checks.brand_name}
            />
            <ResultRow
              field="Class / Type"
              expected={result.verification.expected.class_type}
              found={found.class_type}
              check={result.verification.checks.class_type}
            />
            <ResultRow
              field="ABV"
              expected={result.verification.expected.abv}
              found={found.abv}
              check={result.verification.checks.abv}
            />
            <ResultRow
              field="Net Contents"
              expected={result.verification.expected.net_contents}
              found={found.net_contents}
              check={result.verification.checks.net_contents}
            />
            <ResultRow
              field="Producer / Bottler"
              expected={result.verification.expected.producer}
              found={found.producer}
              check={result.verification.checks.producer}
            />
            <ResultRow
              field="Country of Origin"
              expected={result.verification.expected.country_of_origin}
              found={found.country_of_origin}
              check={result.verification.checks.country_of_origin}
            />
            <ResultRow
              field="Government Warning"
              expected="Required"
              found={found.government_warning.found ? "Detected" : "Missing"}
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
  );
}

function DetectedField({
  label,
  value,
}: {
  label: string;
  value: string | null;
}) {
  return (
    <div>
      <strong>{label}:</strong> {value || "Not detected"}
    </div>
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
      <td className="p-3">{expected || "Not provided"}</td>
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