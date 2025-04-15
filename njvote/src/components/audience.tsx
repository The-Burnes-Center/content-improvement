import { useState } from 'react';
import { DownOutlined } from '@ant-design/icons';
import PersonaDisplay from './personaDisplay';
import { Space, Dropdown, MenuProps, Modal, Button, Input, Checkbox } from 'antd';

const Audience = () => {
  const personas: MenuProps['items'] = [
    {
      key: '1',
      label: 'Voter',
    },
    {
      key: '2',
      label: 'Election Official',
    },
    {
      type: 'divider',
    },
    {
      key: 'new',
      label: 'New User Persona',
    },
  ];

  const [selectedPersona, setSelectedPersona] = useState(personas[0]?.label as string);
  const [openPersonaModal, setOpenPersonaModal] = useState(false);
  const [useAIPersonaGen, setUseAIPersonaGen] = useState(false);

  const toggleUseAIPersonaGen = () => {
    setUseAIPersonaGen(!useAIPersonaGen);
  };

  const showPersonaModal = () => {
    setOpenPersonaModal(true);
  };

  const closePersonaModal = () => {
    setOpenPersonaModal(false);
  };

  const handleMenuClick: MenuProps['onClick'] = (e) => {
    const selectedItem = personas.find(item => item?.key === e.key);
    if (e.key === 'new') {
      showPersonaModal();
    }
    else if (selectedItem && 'label' in selectedItem) {
      setSelectedPersona(selectedItem.label as string);
    }
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
            <Button type='primary' onClick={closePersonaModal}>
              Create
            </Button>
        ]}
      >
        <Input placeholder="Persona Name" />
        <Checkbox onChange={toggleUseAIPersonaGen} style={{marginTop: '1rem'}}>Use AI Persona Generator</Checkbox>
      </Modal>
    </>
  );
};

export default Audience;
