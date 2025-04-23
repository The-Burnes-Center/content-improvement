import { useEffect, useState } from 'react';
import { DownOutlined } from '@ant-design/icons';
import PersonaDisplay from './personaDisplay';
import { Space, Dropdown, MenuProps, Modal, Button, Input, Checkbox, message } from 'antd';

interface AudienceProps {
  projectId: number;
}

const Audience = ({ projectId }: AudienceProps) => {
  const personas: MenuProps['items'] = [
    { key: '1', label: 'Voter' },
    { key: '2', label: 'Election Official' },
    { type: 'divider' },
    { key: 'new', label: 'New User Persona' },
  ];

  const [selectedPersona, setSelectedPersona] = useState(personas[0]?.label as string);
  const [openPersonaModal, setOpenPersonaModal] = useState(false);
  const [useAIPersonaGen, setUseAIPersonaGen] = useState(false);
  const [personaName, setPersonaName] = useState('');

  useEffect(() => {
    const fetchPersonas = async () => {
      try {
        const response = await fetch(`/api/get_personas?projectId=${projectId}`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        });
        const data = await response.json();
        if (response.ok) {
          const personaItems = data.map((item: any) => ({
            key: item.id,
            label: item.name,
          }));
          setSelectedPersona(personaItems[0]?.label as string);
        } else {
          message.error('Failed to fetch personas.');
        }
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
    const selectedItem = personas.find(item => item?.key === e.key);
    if (e.key === 'new') {
      showPersonaModal();
    } else if (selectedItem && 'label' in selectedItem) {
      setSelectedPersona(selectedItem.label as string);
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
              {selectedPersona}
              <DownOutlined />
            </Space>
          </a>
        </Dropdown>
      </div>

      <PersonaDisplay />

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
