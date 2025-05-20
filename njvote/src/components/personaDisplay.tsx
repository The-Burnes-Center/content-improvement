import { Input, Button } from 'antd';
import { useEffect, useState } from 'react';
import { LoadingOutlined } from '@ant-design/icons';

export interface PersonaDisplayProps {
    persona: string | undefined;
    output: string | undefined;
    id: number | undefined;
    updatePersonaField: (id: number, field: 'persona' | 'output', value: string) => void;
    loading: boolean;
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
        setLoading(props.loading);
    }, [props.persona, props.output, props.loading, props.id]);
      
    return (
        <>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginTop: '2%' }}>
                <div
                    className='grayBox'
                    style={{
                        flex: 1, 
                        width: '37rem',
                        height: '25rem',
                        overflowY: 'auto',
                        marginLeft: '2%',
                        marginTop: '-0.03rem', 
                        padding: '1rem',
                        backgroundColor: 'white',
                        whiteSpace: 'pre-wrap',
                        wordWrap: 'break-word',  
                        display: 'block',
                        font: '13px "Helvetica Neue"'
                 
                    }}>
                        {loading ? <LoadingOutlined /> : output}
                </div>
            </div>
        </>
    );
};

export default PersonaDisplay;