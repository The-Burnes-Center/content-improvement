import './App.css';
import { useEffect, useState } from 'react';
import { Input, Layout, Menu, Radio, Modal, Button, Progress, Popconfirm } from "antd";
import { PlusSquareOutlined, CloseOutlined } from '@ant-design/icons';

import Audience from './components/audience';
import ContentClarity from './components/contentclarity';
import WebDesign from './components/webdesign';
import Accessibility from './components/accessibility';
import GettingStarted from './components/gettingStarted';

interface MenuProps {
  key: number;
  label: string;
}

function App() {
  const { Header, Content, Sider } = Layout;

  const [openProjModal, setProjModalOpen] = useState(false);
  const [tab, setTab] = useState('audience');
  const [url, setUrl] = useState('');
  const [name, setName] = useState('');
  const [menuItems, setMenuItems] = useState<MenuProps[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [allProjects, setAllProjects] = useState<any[]>([]);
  const [isLoadingNewProj, setIsLoadingNewProj] = useState(false);
  const [loadingPercent, setLoadingPercent] = useState(0);
  const [loadingText, setLoadingText] = useState('');
  const [isDoneCreatingProject, setIsDoneCreatingProject] = useState(false);
  const [hoveredKey, setHoveredKey] = useState<number | null>(null);

  const showProjModal = () => setProjModalOpen(true);

  const closeProjModal = () => {
    if (!isLoadingNewProj) {
      setProjModalOpen(false);
      setIsDoneCreatingProject(false);
      setLoadingPercent(0);
      setLoadingText('');
      setName('');
      setUrl('');
    }
  };

  useEffect(() => {
    const fetchPersonas = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:5000/get_projects?userId=1`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) throw new Error('Failed to fetch personas');

        const data = await response.json();
        const menuItemsTemp = data.projects.map((item: any) => ({
          key: item[0],
          label: item[3],
        }));

        setMenuItems(menuItemsTemp);
        setAllProjects(data.projects);
        if (menuItemsTemp.length > 0) {
          setSelectedProjectId(Number(menuItemsTemp[0].key));
        }
      } catch (err) {
        console.error(err);
      }
    };

    fetchPersonas();
  }, []);

  const handleDeleteProject = async (e: React.MouseEvent, projectId: number) => {
    e.stopPropagation(); // prevent triggering `onClick` for the Menu.Item
    try {
      const response = await fetch('/api/delete_project', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ projectId }),
      });

      if (!response.ok) throw new Error('Failed to delete project');

      // Remove the deleted project from state
      const updatedMenu = menuItems.filter(item => item.key !== projectId);
      setMenuItems(updatedMenu);
      setAllProjects(prev => prev.filter(project => project[0] !== projectId));

      // If the deleted project was selected, reset selection
      if (selectedProjectId === projectId) {
        setSelectedProjectId(updatedMenu.length > 0 ? Number(updatedMenu[0].key) : null);
      }
    } catch (err) {
      console.error('Error deleting project:', err);
    }
  };


  const createProject = async () => {
    try {
      setIsLoadingNewProj(true);

      const response = await fetch('/api/add_project', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId: 1, url, name }),
      });

      if (!response.ok) throw new Error('Failed to create project');

      const data = await response.json();
      const newProjectId = data.project[0];

      setMenuItems((prev) => [...prev, { key: newProjectId, label: name }]);


      setLoadingText('Analyzing Web Design...');
      await fetch('/api/webdesign', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, projectId: newProjectId }),
      });

      setLoadingText('Analyzing Accessibility');
      setLoadingPercent(33);

      await fetch('/api/accessibility', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, projectId: newProjectId }),
      });

      setLoadingText('Analyzing Content Clarity');
      setLoadingPercent(66);

      await fetch('/api/content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, projectId: newProjectId }),
      });

      const updatedProjects = await fetch(`http://127.0.0.1:5000/get_projects?userId=1`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (updatedProjects.ok) {
        const data = await updatedProjects.json();
        const menuItemsTemp = data.projects.map((item: any) => ({
          key: item[0],
          label: item[3],
        }));
        setMenuItems(menuItemsTemp);
        setAllProjects(data.projects);
      }

      setLoadingPercent(100);
      setLoadingText('Done');
      setIsDoneCreatingProject(true);
      setIsLoadingNewProj(false);
      setSelectedProjectId(newProjectId);
    } catch (err) {
      console.error('Error creating project or analyzing:', err);
    }
  };

  return (
    <>
      <Layout style={{ height: '100vh' }}>
        <Header style={{ display: 'flex', alignItems: 'center', padding: 0, position: 'relative' }}>
          <img src="images/logo.png" alt="Logo" style={{ height: '90px', width: 'auto' }} />
          <div style={{ position: 'absolute', left: '50%', transform: 'translateX(-50%)' }}>
            <h1 style={{ color: 'white', margin: 0 }}>Machine Assistant for eXperience (MAX)</h1>
          </div>
        </Header>

        <Layout style={{ height: '100vh' }}>
          <Sider width={200} className="site-layout-background" theme="light">
            <div style={{ display: 'flex' }}>
              <h2 style={{ color: 'rgb(4, 21, 39)', marginTop: '1rem', marginLeft: '1rem' }}>Projects</h2>
              <div style={{ marginLeft: 'auto', marginTop: '1.25rem', marginRight: '1rem' }} onClick={showProjModal}>
                <PlusSquareOutlined />
              </div>
            </div>
            <Menu
              mode="inline"
              selectedKeys={[String(selectedProjectId)]}
              style={{ height: '100%' }}
            >
              {menuItems.map(item => (
                <Menu.Item
                  key={item.key}
                  onMouseEnter={() => setHoveredKey(item.key)}
                  onMouseLeave={() => setHoveredKey(null)}
                  onClick={() => setSelectedProjectId(Number(item.key))}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span
                      style={{
                        flex: 1,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {item.label}
                    </span>
                    {hoveredKey === item.key && (
                      <Popconfirm
                        title="Are you sure to delete this project?"
                        onConfirm={() => handleDeleteProject(new MouseEvent('click') as any, item.key)}
                        okText="Yes"
                        cancelText="No"
                      >
                        <CloseOutlined 
                          style={{ fontSize: '16px', flexShrink: 0 }}/>
                      </Popconfirm>
                    )}
                  </div>
                </Menu.Item>
              ))}
            </Menu>

          </Sider>

          {allProjects.length === 0 ? (
            <Content style={{ padding: 24, margin: 0, height: 'calc(100vh - 64px)' }}>
              <div className="flex items-center justify-center w-full h-full">
                <GettingStarted />
              </div>
            </Content>
          ) : (
            <Content style={{ padding: 24, margin: 0, minHeight: 280 }}>
              <div style={{ display: 'flex', justifyContent: 'center' }}>
                <h2>
                  Project URL:{' '}
                  {allProjects.find((project) => project[0] === selectedProjectId)?.[2] || "No URL available"}
                </h2>
              </div>

              <div className="flex-center">
                <Radio.Group defaultValue="audience" buttonStyle="solid" className="big-radio">
                  <Radio.Button value="audience" onClick={() => setTab("audience")}>Audience</Radio.Button>
                  <Radio.Button value="content-clarity" onClick={() => setTab("clarity")}>Content Clarity</Radio.Button>
                  <Radio.Button value="web-design" onClick={() => setTab("design")}>Web Design</Radio.Button>
                  <Radio.Button value="accessibility" onClick={() => setTab("accessibility")}>Code Accessibility</Radio.Button>
                </Radio.Group>
              </div>

              {tab === "audience" && <Audience projectId={selectedProjectId} />}
              {tab === "clarity" && <ContentClarity projectId={selectedProjectId} />}
              {tab === "design" && <WebDesign projectId={selectedProjectId} />}
              {tab === "accessibility" && <Accessibility projectId={selectedProjectId} />}
            </Content>
          )}
        </Layout>
      </Layout>

      <Modal
        open={openProjModal}
        title="Create New Project"
        onOk={closeProjModal}
        onCancel={closeProjModal}
        footer={[
          <Button
            type="primary"
            onClick={isDoneCreatingProject ? closeProjModal : createProject}
            disabled={isLoadingNewProj}
            key="create"
          >
            {isDoneCreatingProject ? "Close" : "Create Project"}
          </Button>
        ]}
      >
        {(isLoadingNewProj || isDoneCreatingProject) ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 150 }}>
            <Progress type="circle" percent={loadingPercent} />
            <div style={{ marginLeft: '1rem' }}>
              <h3>{loadingText}</h3>
            </div>
          </div>
        ) : (
          <>
            <Input
              placeholder="Project Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            <Input
              placeholder="URL"
              style={{ marginTop: '1rem' }}
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
          </>
        )}
      </Modal>
    </>
  );
}

export default App;
