import { useEffect, useState } from 'react';
import { DownOutlined, LoadingOutlined   } from '@ant-design/icons';
import PersonaDisplay from './personaDisplay';
import { Space, Dropdown, MenuProps, Modal, Button, Input, Checkbox, message } from 'antd';


export interface PersonaDisplayProps {
  persona: string | undefined;
  output: string | undefined;
  id: number | undefined;
  updatePersonaField: (id: number, field: 'persona' | 'output', value: string) => void;
}


interface AudienceProps {
  projectId: number | null;
  url: string;
}

interface Persona {
  key: string;
  label: string,
  output: string,
  persona: string
}

const Audience = ({ projectId, url }: AudienceProps) => {

  const [personas, setPersonas] = useState<Persona[]>([]);
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(personas[0] || null);
  const [openPersonaModal, setOpenPersonaModal] = useState(false);
  const [useAIPersonaGen, setUseAIPersonaGen] = useState(false);
  const [personaName, setPersonaName] = useState('');
  const [personaContent, setPersonaContent] = useState('');
  const [isEditMode, setIsEditMode] = useState(false);
  const { TextArea } = Input;
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchPersonas = async () => {
      try {
        let personaItems: MenuProps['items'] = [];
        const response = await fetch(`http://127.0.0.1:5000/get_personas?projectId=${projectId}`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        });
        const data = await response.json();
        if (response.ok) {
          personaItems = data['personas'].map((item: any) => ({
            key: String(item[0]),
            label: item[1],
            output: item[4],
            persona: item[3],
          }));
          personaItems?.push({ type: 'divider' });
          personaItems?.push({ key: 'new', label: 'New User Persona' });
        } else {
          message.error('Failed to fetch personas.');
        }
        setPersonas((personaItems || []).filter((item): item is Persona => !!item && 'key' in item && 'label' in item));
        const firstPersona = personaItems?.find((item): item is Persona => !!item && 'label' in item);
        setSelectedPersona(firstPersona || null);
      } catch (err) {
        console.error(err);
        message.error('An error occurred while fetching personas.');
      }
    };
    fetchPersonas();
  }, [projectId]);

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

 const analyzePersona = async (key: string ,personaName: string, personaContent: string ) => {
  try {
    
    const response = await fetch('/api/audience', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: url,
        persona: personaContent,
        personaAuditId: key,
      }),
    });

    const text = await response.text();
    const newPersona = { key: key, label: personaName, output: text, persona: personaContent };
    setPersonas((prevPersonas) => [
              ...(prevPersonas ?? []).slice(0, -2), // Exclude the last two items (divider and "New User Persona")
              newPersona,
              { key: 'divider', label: 'Divider', output: '', persona: '' },
              { key: 'new', label: 'New User Persona', output: '', persona: '' },
            ]);
    setSelectedPersona(newPersona);
    setLoading(false);
  } catch (err) {
    console.error(err);
    updatePersonaField(parseInt(key), 'output', 'Error fetching data from API.');
    setLoading(false);
  }
};

  const createPersona = async () => {
    setOpenPersonaModal(false);
    setPersonaName('');
    setUseAIPersonaGen(false)
    setLoading(true);
    try {
      let text = "";
      
      if (useAIPersonaGen) {
        const res = await fetch(`/api/generate-sample-persona?url=${url}`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        });
        text = await res.text();
        setPersonaContent(text);
      }
      else {
        text = personaContent;
      }
      else{
        text = personaContent;

      }
        const res = await fetch('/api/create_persona_audit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: personaName, projectId }),
      });

      if (res.ok) {
        message.success('Persona created successfully!');
        const data = await res.json()
        // const newPersona = { key: data.id , label: personaName, output: '', persona: personaContent };
        // setPersonas((prevPersonas) => [
        //           ...(prevPersonas ?? []).slice(0, -2), // Exclude the last two items (divider and "New User Persona")
        //           newPersona,
        //           { key: 'divider', label: 'Divider', output: '', persona: '' },
        //           { key: 'new', label: 'New User Persona', output: '', persona: '' },
        //         ]);
        // setSelectedPersona(newPersona);
        closePersonaModal();

        await analyzePersona(data.id ,personaName, text);


      } else {
        message.error('Failed to create persona.');
      }

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



// const PersonaDisplay = (props: PersonaDisplayProps) => {
//     const { TextArea } = Input;

//     const [persona, setPersona] = useState(props.persona);
//     const [output, setOutput] = useState(props.output);
//     const [id, setId] = useState(props.id);
//     const [loading, setLoading] = useState(false);

//     useEffect(() => {
//         setPersona(props.persona);
//         setOutput(props.output);
//         setId(props.id);
//     }, [props.persona, props.output]);

//     const handleAudit = async () => {
//         setLoading(true);
//         try {
//           const response = await fetch('api/audience', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({
//               url: 'https://www.nj.gov/state/elections/vote.shtml',
//               persona: props.persona,
//               personaAuditId: props.id
//             }),
//           });
//           const text = await response.text();
//           if (props.id !== undefined) {
//             props.updatePersonaField(props.id, 'output', text);
//           }
//           setLoading(false);
//         } catch (err) {
//           console.error(err);
//           if (props.id !== undefined) {
//             props.updatePersonaField(props.id, 'output', 'Error fetching data from API.');
//           }
//           setLoading(false);
//         }
//       };

//   // {showPersonaBox && (
//   // <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginTop: '2%' }}>
//   //   <div
//   //     style={{
//   //       marginLeft: '1rem',
//   //       display: 'flex',
//   //       flexDirection: 'column',
//   //       justifyContent: 'space-between',
//   //       height: '19.1rem',
//   //       width: '25rem',
//   //       padding: '1rem',
//   //       backgroundColor: 'white',
//   //       borderRadius: '5px',
//   //     }}
//   //      >

//     </div>
//   </div>
// )}
  
  

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
        output={selectedPersona?.output}
        id={selectedPersona?.key ? parseInt(selectedPersona.key, 10) : undefined}
        updatePersonaField={updatePersonaField}
        loading={loading}
         />

      <Modal
        open={openPersonaModal}
        title="Create New User Persona"
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