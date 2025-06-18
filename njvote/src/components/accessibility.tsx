import { Collapse, Button } from 'antd';
import { useState, useEffect } from 'react';
import AccessibilitySuggestion from './accessibilitySuggestion';
import { DeleteOutlined } from '@ant-design/icons';


const { Panel } = Collapse;

export interface AccessibilityProps {
  suggestions: Suggestion[];
}

interface Suggestion {
  key: number;
  label: string;
  original_content: string;
  revised_content: string;
  explanation: string;
}

const Accessibility = (props: AccessibilityProps) => {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);

  const fetchAccessibilitySuggestions = async () => {
    setSuggestions([]);

    try {
      const parsedSuggestions = props.suggestions.map((item: any) => ({
        key: item[0],
        label: item[2],
        original_content: item[3],
        revised_content: item[4],
        explanation: item[5],
      }));

      setSuggestions(parsedSuggestions);
    } catch (err) {
      console.error('Error fetching accessibility suggestions:', err);
    }
  };

  useEffect(() => {
    fetchAccessibilitySuggestions();
  }, [props.suggestions]);

  const handleDelete = (key: number) => {
    setSuggestions(prev => prev.filter(s => s.key !== key));
    fetch('/api/delete', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ accessibilitySuggestionId: key, toDelete: "accessibility_suggestion" }),
    })
      .then(res => {
        if (!res.ok) {
          console.error('Failed to delete accessibility suggestion');
        }
      })
      .catch(err => {
        console.error('Error deleting accessibility suggestion:', err);
      });
  };

  return (
    <>
      <h2>Make sure your content is aligned with WCAG guidelines</h2>
      <Collapse accordion style={{ marginTop: '2rem' }}>
        {suggestions.map((s) => (
          <Panel
            key={s.key}
            header={
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
                onMouseEnter={(e) => {
                  const btn = e.currentTarget.querySelector('.inline-delete-button') as HTMLElement;
                  if (btn) btn.style.visibility = 'visible';
                }}
                onMouseLeave={(e) => {
                  const btn = e.currentTarget.querySelector('.inline-delete-button') as HTMLElement;
                  if (btn) btn.style.visibility = 'hidden';
                }}
              >
                <span>{s.label}</span>
                <Button
                  type="text"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(s.key);
                  }}
                  style={{
                    visibility: 'hidden',
                    fontSize: '16px',
                    fontWeight: 'bold',
                    color: '#333',
                  }}
                  className="inline-delete-button"
                >
                  <DeleteOutlined />
                </Button>
              </div>
            }
          >
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
