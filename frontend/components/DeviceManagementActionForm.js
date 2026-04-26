"use client";

import { useMemo, useState } from "react";

function getInitialValues(fields) {
  const initial = {};
  for (const field of fields) {
    if (field.defaultValue !== undefined) {
      initial[field.name] = field.defaultValue;
      continue;
    }
    initial[field.name] = field.type === "select" && field.options?.length
      ? field.options[0].value
      : "";
  }
  return initial;
}

export default function DeviceManagementActionForm({ action }) {
  const fields = action?.fields || [];
  const [values, setValues] = useState(() => getInitialValues(fields));
  const [statusMessage, setStatusMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Keep state in sync if route changes action.
  const stableFieldsKey = useMemo(
    () => fields.map((f) => f.name).join("|"),
    [fields]
  );
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const [resetKey, setResetKey] = useState(stableFieldsKey);
  if (resetKey !== stableFieldsKey) {
    // Simple reset when fields change between actions.
    setValues(getInitialValues(fields));
    setResetKey(stableFieldsKey);
  }

  function setFieldValue(name, value) {
    setValues((prev) => ({ ...prev, [name]: value }));
  }

  async function onSubmit(e) {
    e.preventDefault();
    if (!action) return;

    const apiRoot =
      process.env.NEXT_PUBLIC_PLATFORM_API_ROOT || "http://127.0.0.1:8000/api";
    const slug = action.slug || action.key || "";
    if (!slug) {
      setStatusMessage("Missing action slug; cannot submit.");
      return;
    }

    setIsSubmitting(true);
    setStatusMessage("Submitting…");
    try {
      const res = await fetch(`${apiRoot}/device-manager/actions/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          action: slug,
          payload: values,
        }),
      });

      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        const detail = data?.detail || `HTTP ${res.status}`;
        setStatusMessage(`Failed: ${detail}`);
        return;
      }

      setStatusMessage("Saved to device-manager.");
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error("[DeviceManagementActionForm] submit failed", err);
      setStatusMessage("Failed: network or backend error.");
    } finally {
      setIsSubmitting(false);
    }
  }

  if (!action) return null;

  return (
    <form className="dm-action-form" onSubmit={onSubmit}>
      {fields.length ? null : (
        <p className="dm-action-note">No form fields configured for this action.</p>
      )}

      {fields.map((field) => {
        const common = {
          id: `dm-field-${field.name}`,
          name: field.name,
          value: values[field.name] ?? "",
          onChange: (e) => setFieldValue(field.name, e.target.value),
          placeholder: field.placeholder,
          required: Boolean(field.required),
        };

        return (
          <div className="dm-field" key={field.name}>
            <label htmlFor={common.id}>{field.label}</label>
            {field.type === "textarea" ? (
              <textarea
                {...common}
                className="dm-input"
                rows={field.rows || 4}
              />
            ) : field.type === "select" ? (
              <select {...common} className="dm-input">
                {(field.options || []).map((opt) => (
                  <option value={opt.value} key={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            ) : (
              <input
                {...common}
                className="dm-input"
                type={field.type === "number" ? "number" : "text"}
              />
            )}
            {field.help ? <small className="dm-help">{field.help}</small> : null}
          </div>
        );
      })}

      <div className="dm-form-actions">
        <button className="ui-button ui-button-pill" type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Submitting…" : "Submit"}
        </button>
        {statusMessage ? <span className="dm-status">{statusMessage}</span> : null}
      </div>
    </form>
  );
}

