import { Input, Button } from 'antd';
import { useEffect, useState } from 'react';
import { LoadingOutlined } from '@ant-design/icons';

export interface PersonaDisplayProps {
    persona: string | undefined;
    output: string | undefined;
    id: number | undefined;
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
            const response = await fetch('http://localhost:5000/audience', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: 'https://www.nj.gov/state/elections/vote.shtml',
                    persona: persona,
                    personaAuditId: id
                }),
            }).then(response => response.text()).then(text => {
                console.log(text);
                setOutput(text);
                setLoading(false);
            });
        } catch (err) {
            console.error(err);
            setOutput('Error fetching data from API.');
        }
    };

    return (
        <>
            <div className='flex-center' style={{ marginTop: '2%' }}>
                <div style={{ flexDirection: 'column', alignItems: 'stretch', display: 'flex', justifyContent: 'center' }}>
                    <TextArea
                        rows={12}
                        placeholder="Enter a User Persona"
                        style={{ width: '37rem' }}
                        value={persona}
                        onChange={(e) => setPersona(e.target.value)}
                    />
                    <Button onClick={handleAudit} type="primary" style={{ marginTop: '1rem' }}>
                        Audit Site
                    </Button>
                </div>
                <div
                    className='grayBox'
                    style={{
                        width: '37rem',
                        height: '19.1rem',
                        overflowY: 'auto',
                        marginLeft: '2%',
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