import { forwardRef, useId } from 'react'

const Input = forwardRef(function Input(
  { label, error, type = 'text', placeholder, className = '', id, ...rest },
  ref
) {
  const generatedId = useId()
  const errorId = error ? `${id || generatedId}-error` : undefined

  return (
    <label className="block">
      {label ? (
        <span className="block mb-sm font-body text-label-md text-on-surface-variant">{label}</span>
      ) : null}
      <input
        ref={ref}
        id={id}
        type={type}
        placeholder={placeholder}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={errorId}
        className={`
          w-full h-[56px] px-md
          bg-input-fill rounded-md
          font-body text-body-md text-on-surface
          border-2 border-transparent
          focus:outline-none focus:border-primary focus:bg-surface-container-lowest
          transition-colors duration-150
          ${error ? 'border-error' : ''}
          ${className}
        `}
        {...rest}
      />
      {error ? (
        <span id={errorId} role="alert" className="block mt-xs text-body-sm text-error">
          {error}
        </span>
      ) : null}
    </label>
  )
})

export default Input
