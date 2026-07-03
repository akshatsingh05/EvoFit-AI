export default function WelcomeHeader({ fullName }) {
  const firstName = fullName?.split(' ')[0] || 'there'
  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening'

  return (
    <div className="mb-lg">
      <h1 className="text-headline-md text-on-surface">{greeting}, {firstName}</h1>
      <p className="text-body-md text-on-surface-variant mt-xs">Here's where things stand today.</p>
    </div>
  )
}
