import type { ImgHTMLAttributes } from 'react'

type AvatarProps = ImgHTMLAttributes<HTMLImageElement> & { initials?: string; size?: 'sm' | 'md' | 'lg' }

export function Avatar({ initials, alt = '', size = 'md', className = '', ...props }: AvatarProps) {
  const sizes = { sm: 'h-8 w-8 text-xs', md: 'h-10 w-10 text-sm', lg: 'h-14 w-14 text-lg' }
  if (props.src) return <img alt={alt} className={[sizes[size], 'rounded-full object-cover', className].join(' ')} {...props} />
  return <span role="img" aria-label={alt || initials} className={[sizes[size], 'grid place-items-center rounded-full bg-superficie-alt font-semibold text-texto', className].join(' ')}>{initials}</span>
}
