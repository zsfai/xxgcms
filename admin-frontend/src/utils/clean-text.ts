export const cleanInvisibleChars = (text: string) => {
  if (typeof text !== 'string') return text
  return text
    .replace(/[\u200B-\u200D\uFEFF]/g, '')
    .replace(/[\u0000-\u001F\u007F-\u009F]/g, '')
    .replace(/&nbsp;|&#160;/g, ' ')
    .replace(/&ZeroWidthSpace;|&#8203;/g, '')
    .trim()
}
