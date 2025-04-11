import { Input, Button } from 'antd';

const PersonaDisplay = () => {

    const { TextArea } = Input;
    
    return (
        <>
            <div className='flex-center' style={{ marginTop: '2%' }}>
                <div style={{ flexDirection: 'column', alignItems: 'stretch', display: 'flex', justifyContent: 'center' }}>
                    <TextArea
                        rows={12}
                        placeholder="Enter a User Persona"
                        style={{ width: '37rem' }}/>
                    <Button color="green" variant="solid">
                        Audit Site
                    </Button>
                </div>
                <div className='grayBox' style={{ width: '37rem', height: '19.1rem', overflowY: 'scroll', marginLeft: '2%' }}>
                        
                </div>
            </div>
        </>
    )
}

export default PersonaDisplay;