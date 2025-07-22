// utils/parsePartNumbersFromText.js

export function parsePartNumbersFromText(rawText) {
  if (!rawText) return [];

  const lines = rawText
    .split(/\r?\n/)
    .map(line => line.trim())
    .filter(Boolean);

  // Common part number patterns (customize more as needed)
  const partNumberRegexes = [
    /\b[A-Z0-9]{3,}[-\s]?[A-Z0-9]{2,}[-\s]?[A-Z0-9]{2,}\b/i,  // Example: 31100-RCA-A01 or 31100 RCA A01
    /\b\d{4,}-\d{2,}\b/,                                       // Example: 12345-67
    /\b[A-Z0-9]{6,}\b/i                                        // Loose: DENSO123456
  ];

  const matchedParts = new Set();

  for (const line of lines) {
    for (const regex of partNumberRegexes) {
      const match = line.match(regex);
      if (match) matchedParts.add(match[0].replace(/\s+/g, '-').toUpperCase());
    }
  }

  return Array.from(matchedParts);
}
