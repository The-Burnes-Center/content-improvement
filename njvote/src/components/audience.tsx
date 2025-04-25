import { useEffect, useState } from 'react';
import { DownOutlined } from '@ant-design/icons';
import PersonaDisplay from './personaDisplay';
import { Space, Dropdown, MenuProps, Modal, Button, Input, Checkbox, message } from 'antd';

interface AudienceProps {
  projectId: number;
}

interface Persona {
  key: string;
  label: string,
  output: string,
  persona: string
}

const Audience = ({ projectId }: AudienceProps) => {

  const [personas, setPersonas] = useState<Persona[]>([]);
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(personas[0] || null);
  const [openPersonaModal, setOpenPersonaModal] = useState(false);
  const [useAIPersonaGen, setUseAIPersonaGen] = useState(false);
  const [personaName, setPersonaName] = useState('');

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
        console.log(personaItems)
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
    console.log(e.key)
    if (e.key === 'new') {
      showPersonaModal();
    } else if (selectedItem && 'label' in selectedItem) {
      setSelectedPersona(selectedItem);
    }
  };

  const createPersona = async () => {
    try {
      const res = await fetch('/api/create_persona_audit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: personaName, projectId }),
      });

      if (res.ok) {
        message.success('Persona created successfully!');
        const newPersona = { key: String(Date.now()), label: personaName, output: '', persona: '' };
        setPersonas((prevPersonas) => [
                  ...(prevPersonas ?? []).slice(0, -2), // Exclude the last two items (divider and "New User Persona")
                  newPersona,
                  { key: 'divider', label: 'Divider', output: '', persona: '' },
                  { key: 'new', label: 'New User Persona', output: '', persona: '' },
                ]);
        setSelectedPersona(newPersona);
        closePersonaModal();
      } else {
        message.error('Failed to create persona.');
      }
    } catch (err) {
      console.error(err);
      message.error('An error occurred while creating the persona.');
    }
    setOpenPersonaModal(false);
    setPersonaName('');
    setUseAIPersonaGen(false);
  };

  return (
    <>
      <div style={{ marginLeft: '2rem' }}>
        <Dropdown menu={{ items: personas, onClick: handleMenuClick }} trigger={['click']}>
          <a onClick={(e) => e.preventDefault()}>
            <Space>
              {selectedPersona?.label}
              <DownOutlined />
            </Space>
          </a>
        </Dropdown>
      </div>

      <PersonaDisplay 
        persona={selectedPersona?.persona}
        output={selectedPersona?.output}
        id={selectedPersona?.key ? parseInt(selectedPersona.key, 10) : undefined}
         />

      <Modal
        open={openPersonaModal}
        title="Create New User Persona"
        onCancel={closePersonaModal}
        footer={[
          <Button type="primary" onClick={createPersona} disabled={!personaName}>
            Create
          </Button>,
        ]}
      >
        <Input
          placeholder="Persona Name"
          value={personaName}
          onChange={(e) => setPersonaName(e.target.value)}
        />
        <Checkbox onChange={toggleUseAIPersonaGen} style={{ marginTop: '1rem' }}>
          Use AI Persona Generator
        </Checkbox>
      </Modal>
    </>
  );
};

export default Audience;