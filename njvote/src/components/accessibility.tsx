import { Collapse } from 'antd';
import AccessibilitySuggestion from './accessibilitySuggestion';
import { useState, useEffect } from 'react';

const { Panel } = Collapse;

const Accessibility = () => {

  interface Suggestion {
    label: string;
    original_content: string;
    revised_content: string;
    explanation: string;
  }

  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);

  const handleAudit = async () => {
    try {
        const response = await fetch('api/webdesign', {

            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: 'https://www.nj.gov/state/elections/vote.shtml',
            }),
        }).then(rsp => rsp.json()).then(rsp => {
          console.log(rsp)
            setSuggestions(rsp);
        })
    } catch (err) {
        console.error(err);
    }
  };

  useEffect(() => {
    handleAudit();
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
