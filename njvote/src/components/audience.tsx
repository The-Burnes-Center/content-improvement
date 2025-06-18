import { useEffect, useState } from 'react';
import { DownOutlined, InfoCircleFilled } from '@ant-design/icons';
import PersonaDisplay from './personaDisplay';
import { Space, Dropdown, MenuProps, Modal, Button, Input, Checkbox, message, Popover} from 'antd'; 


interface AudienceProps {
  personas: Persona[];
  url: string;
  projectId: number | null
}

interface Persona {
  key: string;
  label: string,
  persona: string
  positives: string;
  challenges: string;
}

const Audience = (props: AudienceProps) => {

  const [personas, setPersonas] = useState<Persona[]>([]);
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(personas[0] || null);
  const [openPersonaModal, setOpenPersonaModal] = useState(false);
  const [useAIPersonaGen, setUseAIPersonaGen] = useState(false);
  const [personaName, setPersonaName] = useState('');
  const [personaContent, setPersonaContent] = useState('');
  const [isEditMode, setIsEditMode] = useState(false);
  const { TextArea } = Input;
  const [loading, setLoading] = useState(false);

  

  const InfoContent = (
  <div style={{ maxWidth: 500 }}>
    <p style={{ margin: 0 }}>Name:</p>
    <p style={{ margin: 0 }}>Age:</p>
    <p style={{ margin: 0 }}> Gender: </p>
    <p style={{ margin: 0 }}> Occupation:</p>
    <p style={{ margin: 0 }}>Income Level:</p>
    <p style={{ margin: 0 }}>Education Level:</p>
    <p style={{ margin: 0 }}>Tech Savviness: Beginner/ Moderate / Intermediate / Advance </p>
    <p> Include Goals, Needs, and Potential Challenges </p>
    
  </div>
)



  useEffect(() => {
    const fetchPersonas = async () => {
      try {
        let personaItems: MenuProps['items'] = [];
        personaItems = props.personas.map((item: any) => ({
          key: String(item[0]),
          label: item[1],
          persona: item[3],
          positives: item[4],
          challenges: item[5],
        }));
        personaItems?.push({ type: 'divider' });
        personaItems?.push({ key: 'new', label: 'New User Persona' });
        setPersonas((personaItems || []).filter((item): item is Persona => !!item && 'key' in item && 'label' in item));
        const firstPersona = personaItems?.find((item): item is Persona => !!item && 'label' in item);
        setSelectedPersona(firstPersona || null);
      } catch (err) {
        console.error(err);
        message.error('An error occurred while fetching personas.');
      }
    };
    fetchPersonas();
  }, [props.personas, props.url]);

  const toggleUseAIPersonaGen = () => {
    setUseAIPersonaGen(!useAIPersonaGen);
  };

  const showPersonaModal = () => {
    setOpenPersonaModal(true);
  };

  const closePersonaModal = () => {
    setOpenPersonaModal(false);
    setPersonaName('');
    setUseAIPersonaGen(false);
  };

  const handleMenuClick: MenuProps['onClick'] = (e) => {
    const selectedItem = personas?.find(item => item?.key === e.key);
    if (e.key === 'new') {
      setIsEditMode(false);
      setPersonaName('');
      setPersonaContent('');
      showPersonaModal();
    } else if (selectedItem && 'label' in selectedItem) {
      setSelectedPersona(selectedItem);
      setIsEditMode(true);
      setPersonaName(selectedItem.label);         
      setPersonaContent(selectedItem.persona);    
      showPersonaModal()
    }
  };

 const analyzePersona = async (personaName: string, personaContent: string ) => {
  let newId = "-1";
  try {
    
    const response = await fetch('https://a8b6filf5e.execute-api.us-east-1.amazonaws.com/audience', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: props.url,
        persona: personaContent,
        name: personaName,
        projectId: props.projectId,
        usePersonaGenerator: useAIPersonaGen
      }),
    });

    const text = await response.json();
    newId = text[2];
    const newPersona = { key: newId, label: personaName, persona: personaContent, positives: text.positives, challenges: text.challenges };
    setPersonas((prevPersonas) => [
                  ...(prevPersonas ?? []).slice(0, -1), // Exclude the last two items (divider and "New User Persona")
                  newPersona,
                  { key: 'new', label: 'New User Persona', persona: '', positives: '', challenges: '' },
                ]);
    setSelectedPersona(newPersona);
    setLoading(false);
  } catch (err) {
    console.error(err);
    updatePersonaField(parseInt(newId), 'output', 'Error fetching data from API.');
    setLoading(false);
  }
};

  const createPersona = async () => {
    setOpenPersonaModal(false);
    setPersonaName('');
    setUseAIPersonaGen(false)
    setLoading(true);
    try {


      await analyzePersona(personaName, personaContent);
      closePersonaModal();


    } catch (err) {
      console.error(err);
      message.error('An error occurred while creating the persona.');
    }

  };

  const updatePersonaField = (id: number, field: 'persona' | 'output', value: string) => {
    setPersonas((prevPersonas) =>
      prevPersonas.map((p) =>
        parseInt(p.key, 10) === id ? { ...p, [field]: value } : p
      )
    );
    if (selectedPersona && parseInt(selectedPersona.key, 10) === id) {
      setSelectedPersona((prev) => prev ? { ...prev, [field]: value } : prev);
    }
  };

  return (
    <>
      <div style={{ marginLeft: '1rem' }}>
        <h2>Understand how users interact with your website</h2>
        <Dropdown menu ={{ items: personas, onClick: handleMenuClick }} trigger={['click']} disabled={loading}>
          <Button>
          <a onClick={(e) => e.preventDefault()}>
            <Space>
              {selectedPersona?.label}
              <DownOutlined />
            </Space>
          </a>
          </Button>
        </Dropdown>
      </div>
       
      

      <PersonaDisplay 
        persona={selectedPersona?.persona}
        positives={selectedPersona?.positives || ''}
        challenges={selectedPersona?.challenges || ''}
        id={selectedPersona?.key ? parseInt(selectedPersona.key, 10) : undefined}
        updatePersonaField={updatePersonaField}
        loading={loading}
         />

      <Modal
        open={openPersonaModal}
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <span>Create New User Persona</span>
            <Popover
              content={InfoContent}
              title="An Example Persona Includes:"
              placement="right"
              trigger="click"
              align={{ offset: [20, 80] }} 
            >
            <InfoCircleFilled style={{ fontSize: '1rem', color: '#179ee2', cursor: 'pointer' }} />
          </Popover>
          </div>
        }

        onCancel={closePersonaModal}
        

        footer={[
          <Button type="primary" onClick={createPersona} disabled={!personaName} style={{ fontWeight: '500' }}>
            Analyze
          </Button>,
        ]}
      >
        <Checkbox onChange={toggleUseAIPersonaGen} checked={useAIPersonaGen}>
          Use AI Persona Generator
        </Checkbox>


        <div style={{ marginTop: '1rem' }}></div>
        <Input
          placeholder="Persona Name"
          value={personaName}
          onChange={(e) => {
          const newName = e.target.value;
          setPersonaName(newName);

          if (isEditMode && selectedPersona) {
            updatePersonaField(parseInt(selectedPersona.key), 'persona', newName);

          }
        }}
        />



         <div style={{ position: 'relative', width: '100%', marginTop: '1rem' }}>
         <TextArea
            key={useAIPersonaGen ? 'ai' : 'manual'}
            disabled={useAIPersonaGen}
            rows={12}
            placeholder= "Enter a User Persona"
            style={{ width: '100%', paddingBottom: '2rem' }}
            value={personaContent}
            onChange={(e) => setPersonaContent(e.target.value)}
          />
          </div>
      </Modal>
    </>
  );
};

export default Audience;