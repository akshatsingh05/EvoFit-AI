export default function Card({ children, className = '', padded = true }) {
  return (
    <div
      className={`
        bg-surface-container-lowest rounded-lg shadow-card
        ${padded ? 'p-lg' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  )
}
