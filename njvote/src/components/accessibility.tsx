import { Collapse } from 'antd';
import AccessibilitySuggestion from './accessibilitySuggestion';
import { useState, useEffect } from 'react';

const { Panel } = Collapse;


export interface AccessibilityProps {
  projectId: number | null;
}

const Accessibility = (props: AccessibilityProps) => {

  interface Suggestion {
    label: string;
    original_content: string;
    revised_content: string;
    explanation: string;
  }


  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);

  const fetchAccessibilitySuggestions = async () => {
    // try {
    //     const response = await fetch('/api/accessibility', {
    //         method: 'POST',
    //         headers: {
    //             'Content-Type': 'application/json',
    //         },
    //         body: JSON.stringify({
    //             url: 'https://www.nj.gov/state/elections/vote.shtml',
    //         }),
    //     }).then(rsp => rsp.json()).then(rsp => {
    //       console.log(rsp)
    //         setSuggestions(rsp);
    //     })
    // } catch (err) {
    //     console.error(err);
    // }

    setSuggestions([]);
    try {
      const auditResponse = await fetch(`api/get_accessibility_audit?projectId=${props.projectId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      
      if (auditResponse.ok) {
        const auditData = await auditResponse.json();
        const accessibilityAuditId = auditData['accessibility_audit'][0];

        console.log(auditData)

        console.log("accessibilityAuditId", accessibilityAuditId)

        const response = await fetch(`api/get_accessibility_suggestions?accessibilityAuditId=${accessibilityAuditId}`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        });

        const data = await response.json();

        console.log(data['suggestions'])

        if (response.ok) {
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
    }
    catch (err) {
      console.error(err);
      console.error('An error occurred while fetching web design suggestions.');
    }
  };

  useEffect(() => {
    fetchAccessibilitySuggestions();
  }, []);


  return (
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
  );
};

export default Accessibility;
