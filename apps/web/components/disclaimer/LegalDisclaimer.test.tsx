import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { LegalDisclaimer } from './LegalDisclaimer';

describe('LegalDisclaimer', () => {
  it('renders the disclaimer text properly', () => {
    render(<LegalDisclaimer />);
    
    // Check if the exact text exists
    expect(screen.getByText(/Legal information only — not legal advice\./i)).toBeInTheDocument();
    expect(screen.getByText(/Consider consulting a qualified lawyer/i)).toBeInTheDocument();
  });
});
