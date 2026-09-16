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

export default function RecordForm({ values, onChange, onSubmit, onLoadExample, loading }) {
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

      {FIELD_GROUPS.map((group) => (
        <fieldset key={group.title} className="field-group">
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
      ))}

      <button type="submit" className="btn btn-primary" disabled={loading}>
        {loading ? "Classifying..." : "Classify record"}
      </button>
    </form>
  );
}
