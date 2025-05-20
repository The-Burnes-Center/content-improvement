import { Input, Button } from 'antd';
import { useEffect, useState } from 'react';
import { LoadingOutlined } from '@ant-design/icons';

// Props for the PersonaDisplay component
export interface PersonaDisplayProps {
  persona: string | undefined;
  output: string | undefined;
  id: number | undefined;
  updatePersonaField: (id: number, field: 'persona' | 'output', value: string) => void;
}

const PersonaDisplay = ({ persona, output: propOutput, id, updatePersonaField }: PersonaDisplayProps) => {
  const { TextArea } = Input;

  // Local state to mirror props
  const [output, setOutput] = useState(propOutput);
  const [loading, setLoading] = useState(false);

  // Sync local state with props when props change
  useEffect(() => {
    setOutput(propOutput);
  }, [persona, propOutput]);

  // Trigger API call to audit the site for this persona
  const handleAudit = async () => {
    if (id === undefined) return;

    setLoading(true);
    try {
      const response = await fetch('api/audience', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: 'https://www.nj.gov/state/elections/vote.shtml',
          persona,
          personaAuditId: id,
        }),
      });

      const text = await response.text();
      updatePersonaField(id, 'output', text);
    } catch (err) {
      console.error(err);
      updatePersonaField(id, 'output', 'Error fetching data from API.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        gap: '2rem',
        marginTop: '2%',
      }}
    >
      {/* Left input card for entering user persona */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          height: '19.1rem',
          width: '25rem',
          padding: '1rem',
          backgroundColor: 'white',
          borderRadius: '5px',
        }}
      >
        <TextArea
          rows={12}
          placeholder="Enter a User Persona"
          style={{ width: '100%' }}
          value={persona}
          onChange={(e) => {
            if (id !== undefined) {
              updatePersonaField(id, 'persona', e.target.value);
            }
          }}
        />
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button onClick={handleAudit} type="primary">
            Audit Site
          </Button>
        </div>
      </div>

      {/* Right output box for showing audit result */}
      <div
        className="grayBox"
        style={{
          flex: 1,
          width: '37rem',
          height: '19.1rem',
          overflowY: 'auto',
          marginLeft: '2%',
          marginTop: '-0.03rem',
          padding: '1rem',
          backgroundColor: 'lightgray',
          whiteSpace: 'pre-wrap',
          wordWrap: 'break-word',
          display: 'block',
        }}
      >
        {loading ? <LoadingOutlined /> : output}
      </div>
    </div>
  );
};

export default PersonaDisplay;
