import * as React from 'react'
import { Label } from '@/components/ui/label'
import { cn } from '@/lib/utils'

export function RequiredMark({ className }: { className?: string }) {
  return <span className={cn('text-destructive', className)} aria-hidden="true">*</span>
}

export type FormLabelProps = React.ComponentPropsWithoutRef<typeof Label> & {
  required?: boolean
}

export function FormLabel({ required, children, className, ...props }: FormLabelProps) {
  return (
    <Label className={cn('form-field-label', className)} {...props}>
      {children}
      {required && <RequiredMark />}
    </Label>
  )
}
