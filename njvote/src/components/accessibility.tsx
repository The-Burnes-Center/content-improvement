import { Collapse } from 'antd';
import { useState, useEffect } from 'react';
import AccessibilitySuggestion from './accessibilitySuggestion';

const { Panel } = Collapse;

// Props interface for the Accessibility component
export interface AccessibilityProps {
  projectId: number | null;
}

// Suggestion object structure returned by the backend
interface Suggestion {
  label: string;
  original_content: string;
  revised_content: string;
  explanation: string;
}

const Accessibility = ({ projectId }: AccessibilityProps) => {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);

  // Fetches accessibility audit suggestions from backend
  const fetchAccessibilitySuggestions = async () => {
    // Prevent fetch if projectId is not set
    if (!projectId) return;

    // Clear existing suggestions before fetching new ones
    setSuggestions([]);

    try {
      // Step 1: Get audit ID for the given project
      const auditRes = await fetch(`api/get_accessibility_audit?projectId=${projectId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!auditRes.ok) {
        console.error('Failed to fetch audit ID');
        return;
      }

      const auditData = await auditRes.json();
      const accessibilityAuditId = auditData?.accessibility_audit?.[0];

      // If audit ID is missing, stop execution
      if (!accessibilityAuditId) {
        console.error('No accessibility audit ID found.');
        return;
      }

      // Step 2: Use the audit ID to fetch the actual suggestions
      const suggestionsRes = await fetch(
        `api/get_accessibility_suggestions?accessibilityAuditId=${accessibilityAuditId}`,
        {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        }
      );

      if (!suggestionsRes.ok) {
        console.error('Failed to fetch accessibility suggestions');
        return;
      }

      const data = await suggestionsRes.json();

      // Transform backend response into the Suggestion format
      const parsedSuggestions = data.suggestions.map((item: any) => ({
        label: item[2],
        original_content: item[3],
        revised_content: item[4],
        explanation: item[5],
      }));

      // Store parsed suggestions in state
      setSuggestions(parsedSuggestions);
    } catch (err) {
      console.error('Error fetching accessibility suggestions:', err);
    }
  };

  // Automatically fetch suggestions when component mounts or when projectId changes
  useEffect(() => {
    fetchAccessibilitySuggestions();
  }, [projectId]);

  return (
    <>
      <h2>Make sure your content is aligned with WCAG guidelines</h2>

      {/* Accordion-style collapsible panels for each suggestion */}
      <Collapse accordion style={{ marginTop: '2rem' }}>
        {suggestions.map((s, i) => (
          <Panel header={s.label} key={i}>
            <AccessibilitySuggestion
              original={s.original_content}
              revised={s.revised_content}
              explanation={s.explanation}
            />
          </Panel>
        ))}
      </Collapse>
    </>
  );
};

export default Accessibility;
