import { Collapse } from 'antd';
import AccessibilitySuggestion from './accessibilitySuggestion';
import { useState, useEffect } from 'react';

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

const Accessibility = (props: AccessibilityProps) => {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);

  // Fetches accessibility audit suggestions from backend
  const fetchAccessibilitySuggestions = async () => {
    // Clear existing suggestions before fetching new ones
    setSuggestions([]);

    try {
      // Step 1: Get audit ID for the given project
      const auditResponse = await fetch(
        `api/get_accessibility_audit?projectId=${props.projectId}`,
        {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        }
      );

      if (auditResponse.ok) {
        const auditData = await auditResponse.json();
        const accessibilityAuditId = auditData['accessibility_audit'][0];

        // Step 2: Use the audit ID to fetch the actual suggestions
        const response = await fetch(
          `api/get_accessibility_suggestions?accessibilityAuditId=${accessibilityAuditId}`,
          {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
          }
        );

        const data = await response.json();

        if (response.ok) {
          // Transform backend response into the Suggestion format
          const suggestions = data['suggestions'].map((item: any) => ({
            label: item[2],
            original_content: item[3],
            revised_content: item[4],
            explanation: item[5],
          }));

          setSuggestions(suggestions);
        } else {
          console.error('Failed to fetch accessibility suggestions.');
        }
      }
    } catch (err) {
      console.error(err);
      console.error('An error occurred while fetching accessibility suggestions.');
    }
  };

  // Automatically fetch suggestions when component mounts
  useEffect(() => {
    fetchAccessibilitySuggestions();
  }, []);

  return (
    <>
      <h2>Make sure your content is aligned with WCAG guidelines</h2>

      <Collapse accordion style={{ marginTop: '2rem' }}>
        {suggestions.map((suggestion, index) => (
          <Panel header={suggestion.label} key={index}>
            <AccessibilitySuggestion
              original={suggestion.original_content}
              revised={suggestion.revised_content}
              explanation={suggestion.explanation}
            />
          </Panel>
        ))}
      </Collapse>
    </>
  );
};

export default Accessibility;
