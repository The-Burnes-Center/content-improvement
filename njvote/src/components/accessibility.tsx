import { Collapse, Button } from 'antd';
import { useState, useEffect } from 'react';
import AccessibilitySuggestion from './accessibilitySuggestion';
import { DeleteOutlined } from '@ant-design/icons';


const { Panel } = Collapse;

export interface AccessibilityProps {
  projectId: number | null;
}

interface Suggestion {
  key: number;
  label: string;
  original_content: string;
  revised_content: string;
  explanation: string;
}

const Accessibility = ({ projectId }: AccessibilityProps) => {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);

  const fetchAccessibilitySuggestions = async () => {
    if (!projectId) return;
    setSuggestions([]);

    try {
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

      if (!accessibilityAuditId) {
        console.error('No accessibility audit ID found.');
        return;
      }

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

      const parsedSuggestions = data.suggestions.map((item: any) => ({
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
  }, [projectId]);

  const handleDelete = (key: number) => {
    setSuggestions(prev => prev.filter(s => s.key !== key));
    fetch('/api/delete_accessibility_suggestion', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ accessibilitySuggestionId: key }),
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
