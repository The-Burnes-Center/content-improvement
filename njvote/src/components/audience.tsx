import { useState } from 'react';
import { Button } from 'antd';
import PersonaDisplay from './personaDisplay';

const Audience = () => {
    const [personas, setPersonas] = useState([<PersonaDisplay key={0} />]);

    const addPersona = () => {
        setPersonas(prev => [
            ...prev,
            <PersonaDisplay key={prev.length} />
        ]);
    };

    return (
        <>
            {personas}
            <div className='flex-center' style={{ marginTop: '1%' }}>
                <Button type='primary' onClick={addPersona}>
                    Add User Persona
                </Button>
            </div>
        </>
    );
};

export default Audience;
