import { FIELD_GROUPS } from "../fields";

function FieldInput({ field, value, onChange }) {
  const commonProps = {
    id: field.name,
    name: field.name,
    value,
    onChange: (e) => onChange(field.name, e.target.value),
  };

  if (field.type === "select") {
    return (
      <select {...commonProps}>
        {field.options.map((opt) => (
          <option key={opt} value={opt}>
            {opt}
          </option>
        ))}
      </select>
    );
  }

  if (field.type === "text-suggest") {
    const listId = `${field.name}-options`;
    return (
      <>
        <input {...commonProps} type="text" list={listId} autoComplete="off" />
        <datalist id={listId}>
          {field.options.map((opt) => (
            <option key={opt} value={opt} />
          ))}
        </datalist>
      </>
    );
  }

  // number-int / number-float
  return (
    <input
      {...commonProps}
      type="number"
      step={field.step}
      min={field.min}
      max={field.max}
    />
  );
}

function FieldGroup({ group, values, onChange }) {
  return (
    <fieldset className="field-group">
      <legend>{group.title}</legend>
      {group.help && <p className="group-help">{group.help}</p>}
      <div className="field-grid">
        {group.fields.map((field) => (
          <label key={field.name} className="field-label" htmlFor={field.name}>
            <span>{field.label}</span>
            <FieldInput field={field} value={values[field.name]} onChange={onChange} />
          </label>
        ))}
      </div>
    </fieldset>
  );
}

export default function RecordForm({ values, onChange, onSubmit, onLoadExample, loading }) {
  const essentialGroups = FIELD_GROUPS.filter((group) => !group.advanced);
  const advancedGroups = FIELD_GROUPS.filter((group) => group.advanced);
  const advancedFieldCount = advancedGroups.reduce((n, group) => n + group.fields.length, 0);

  return (
    <form className="record-form" onSubmit={onSubmit}>
      <div className="example-buttons">
        <span className="example-label">Quick fill:</span>
        <button type="button" className="btn btn-ghost" onClick={() => onLoadExample("normal")}>
          Normal-looking example
        </button>
        <button type="button" className="btn btn-ghost" onClick={() => onLoadExample("attack")}>
          Attack-looking example
        </button>
        <span className="example-note">illustrative only, not pulled from the dataset -- every field stays editable</span>
      </div>

      {essentialGroups.map((group) => (
        <FieldGroup key={group.title} group={group} values={values} onChange={onChange} />
      ))}

      <details className="advanced-section">
        <summary className="advanced-summary">
          Advanced: traffic &amp; host statistics
          <span className="advanced-summary-note">
            ({advancedFieldCount} fields, pre-filled with typical values -- optional)
          </span>
        </summary>
        {advancedGroups.map((group) => (
          <FieldGroup key={group.title} group={group} values={values} onChange={onChange} />
        ))}
      </details>

      <button type="submit" className="btn btn-primary" disabled={loading}>
        {loading ? "Classifying..." : "Classify record"}
      </button>
    </form>
  );
}
