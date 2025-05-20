import { useEffect, useState } from 'react';
import { DownOutlined } from '@ant-design/icons';
import PersonaDisplay from './personaDisplay';
import {
  Space,
  Dropdown,
  MenuProps,
  Modal,
  Button,
  Input,
  Checkbox,
  message,
} from 'antd';

// Props passed into the Audience component
interface AudienceProps {
  projectId: number | null;
}

// Structure for each persona
interface Persona {
  key: string;
  label: string;
  output: string;
  persona: string;
}

const Audience = ({ projectId }: AudienceProps) => {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(null);
  const [openPersonaModal, setOpenPersonaModal] = useState(false);
  const [useAIPersonaGen, setUseAIPersonaGen] = useState(false);
  const [personaName, setPersonaName] = useState('');

  // Fetch personas when projectId changes
  useEffect(() => {
    const fetchPersonas = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:5000/get_personas?projectId=${projectId}`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) {
          message.error('Failed to fetch personas.');
          return;
        }

        const data = await response.json();
        const personaItems = data['personas'].map((item: any) => ({
          key: String(item[0]),
          label: item[1],
          output: item[4],
          persona: item[3],
        }));

        // Add divider and "new" option
        const enrichedItems = [
          ...personaItems,
          { type: 'divider' },
          { key: 'new', label: 'New User Persona' },
        ];

        // Filter and cast items to Persona
        const validPersonas = enrichedItems.filter(
          (item): item is Persona => !!item && 'key' in item && 'label' in item
        );

        setPersonas(validPersonas);

        // Default selection
        const firstPersona = validPersonas.find((item) => !!item && 'label' in item);
        setSelectedPersona(firstPersona || null);
      } catch (err) {
        console.error(err);
        message.error('An error occurred while fetching personas.');
      }
    };

    fetchPersonas();
  }, [projectId]);

  // Toggle checkbox state
  const toggleUseAIPersonaGen = () => {
    setUseAIPersonaGen((prev) => !prev);
  };

  // Open persona modal
  const showPersonaModal = () => {
    setOpenPersonaModal(true);
  };

  // Close persona modal and reset fields
  const closePersonaModal = () => {
    setOpenPersonaModal(false);
    setPersonaName('');
    setUseAIPersonaGen(false);
  };

  // Handle persona selection or creation from dropdown
  const handleMenuClick: MenuProps['onClick'] = (e) => {
    if (e.key === 'new') {
      showPersonaModal();
    } else {
      const selectedItem = personas.find((item) => item.key === e.key);
      if (selectedItem) setSelectedPersona(selectedItem);
    }
  };

  // Create a new persona and add to list
  const createPersona = async () => {
    try {
      const res = await fetch('/api/create_persona_audit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: personaName, projectId }),
      });

      if (!res.ok) {
        message.error('Failed to create persona.');
        return;
      }

      message.success('Persona created successfully!');
      const newPersona = {
        key: String(Date.now()),
        label: personaName,
        output: '',
        persona: '',
      };

      setPersonas((prev) => [
        ...(prev ?? []).slice(0, -2),
        newPersona,
        { key: 'divider', label: 'Divider', output: '', persona: '' },
        { key: 'new', label: 'New User Persona', output: '', persona: '' },
      ]);

      setSelectedPersona(newPersona);
      closePersonaModal();
    } catch (err) {
      console.error(err);
      message.error('An error occurred while creating the persona.');
    }
  };

  // Update a field (persona or output) in the selected persona
  const updatePersonaField = (id: number, field: 'persona' | 'output', value: string) => {
    setPersonas((prev) =>
      prev.map((p) => (parseInt(p.key, 10) === id ? { ...p, [field]: value } : p))
    );
    if (selectedPersona && parseInt(selectedPersona.key, 10) === id) {
      setSelectedPersona((prev) => (prev ? { ...prev, [field]: value } : prev));
    }
  };

  return (
    <>
      <h2>Understand how users interact with your website</h2>

      {/* Dropdown for selecting personas */}
      <div style={{ marginLeft: '2rem' }}>
        <Dropdown menu={{ items: personas, onClick: handleMenuClick }} trigger={['click']}>
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

      {/* Persona viewer/editor */}
      <PersonaDisplay
        persona={selectedPersona?.persona}
        output={selectedPersona?.output}
        id={selectedPersona?.key ? parseInt(selectedPersona.key, 10) : undefined}
        updatePersonaField={updatePersonaField}
      />

      {/* Modal to create new persona */}
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
