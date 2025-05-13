import { Input, Button } from 'antd';
import { useEffect, useState } from 'react';
import { LoadingOutlined } from '@ant-design/icons';

export interface PersonaDisplayProps {
    persona: string | undefined;
    output: string | undefined;
    id: number | undefined;
    updatePersonaField: (id: number, field: 'persona' | 'output', value: string) => void;
}

const PersonaDisplay = (props: PersonaDisplayProps) => {
    const { TextArea } = Input;

    const [persona, setPersona] = useState(props.persona);
    const [output, setOutput] = useState(props.output);
    const [id, setId] = useState(props.id);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        setPersona(props.persona);
        setOutput(props.output);
        setId(props.id);
    }, [props.persona, props.output]);

    const handleAudit = async () => {
        setLoading(true);
        try {
          const response = await fetch('api/audience', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              url: 'https://www.nj.gov/state/elections/vote.shtml',
              persona: props.persona,
              personaAuditId: props.id
            }),
          });
          const text = await response.text();
          if (props.id !== undefined) {
            props.updatePersonaField(props.id, 'output', text);
          }
          setLoading(false);
        } catch (err) {
          console.error(err);
          if (props.id !== undefined) {
            props.updatePersonaField(props.id, 'output', 'Error fetching data from API.');
          }
          setLoading(false);
        }
      };
      

    return (
        <>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '2rem', marginTop: '2%' }}>
                <div
                  style={{
                    //flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between', 
                    height: '19.1rem', // same height as the right gray box
                    width: '25rem',
                    padding: '1rem',
                    backgroundColor: 'white', // optional
                    borderRadius: '5px', // optional styling
                    
                  }}
                >
                  <TextArea
                    rows={12}
                    placeholder="Enter a User Persona"
                    style={{ width: '100%' }}
                    value={props.persona}
                    onChange={(e) => {
                      if (props.id !== undefined) {
                        props.updatePersonaField(props.id, 'persona', e.target.value);
                      }
                    }}
                  />

                  <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                    <Button onClick={handleAudit} type="primary">
                      Audit Site
                    </Button>
                  </div>
                </div>
                <div
                    className='grayBox'
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
                    }}>
                        {loading ? <LoadingOutlined /> : output}
                </div>

            </div>
        </>
    );
};

export default PersonaDisplay;