import './App.css'
import { useEffect, useState } from 'react';
import { Input, Layout, Menu, Radio, Modal, Button, Tooltip } from "antd";
import Audience from './components/audience';
import { PlusSquareOutlined } from '@ant-design/icons';
import ContentClarity from './components/contentclarity';
import WebDesign from './components/webdesign';
import Accessibility from './components/accessibility';

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
  const [webDevSuggestions, setWebDevSuggestions] = useState<any[]>([]);
  const [allProjects, setAllProjects] = useState<any[]>([]);

  const showProjModal = () => {
    setProjModalOpen(true);
  };

  const closeProjModal = () => {
    setProjModalOpen(false);
  }

  useEffect(() => {
    const fetchPersonas = async () => {
      try {
        let menuItemsTemp = [];
        const response = await fetch(`http://127.0.0.1:5000/get_projects?userId=${1}`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        });
        const data = await response.json();
        if (response.ok) {
          menuItemsTemp = data['projects'].map((item: any) => ({
            key: item[0],
            label: item[3],
          }));
        } else {
          console.error('Failed to fetch personas.');
        }
        setMenuItems(menuItemsTemp);
        if (menuItemsTemp.length > 0) {
          setSelectedProjectId(Number(menuItemsTemp[0].key));
        }
        setAllProjects(data['projects']);
      } catch (err) {
        console.error(err);
        console.error('An error occurred while fetching personas.');
      }
    };
    fetchPersonas();
  }, []);

  const createProject = async () => {
    try {
      // Step 1: Add the project
      const response = await fetch('/api/add_project', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: 1,
          url: url,
          name: name,
        }),
      });

      let newProjectId = 0;

      if (response.ok) {
        const data = await response.json();
        const newMenuItem = {
          key: String(data['project'][0]),
          label: name,
        };
        setMenuItems((prevMenuItems) => [...prevMenuItems, { ...newMenuItem, key: Number(newMenuItem.key) }]);
        newProjectId = data['project'][0]; // Assuming the API returns the new project's ID as `projectId`
        console.log('New Project ID:', newProjectId);
        setSelectedProjectId(newProjectId);
      } else {
        throw new Error('Failed to create project');
      }
  
      if (!response.ok) {
        throw new Error('Failed to create project');
      }
  
      // Step 2: Call /webdesign with the URL
      const webdesignResponse = await fetch('/api/webdesign', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: url,
          projectId: newProjectId,
        }),
      });
  
      if (!webdesignResponse.ok) {
        throw new Error('Failed to analyze web design');
      }
  
      const webdesignData = await webdesignResponse.json();

      if (Array.isArray(webdesignData)) {
        const withKeys = webdesignData.map(item => ({
          ...item,
          key: item.key.toString(), // Convert int -> string for AntD
        }));
        setWebDevSuggestions(withKeys);
      } else {
        console.error("Unexpected response format:", webdesignData);
      }
  
      // Now you have the feedback saved locally
      console.log('Web Design Feedback:', webdesignData);

      const accessabilityResponse = await fetch('/api/accessibility', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: url,
          projectId: newProjectId,
        }),
      });
      if (!accessabilityResponse.ok) {
        throw new Error('Failed to analyze accessability');
      }
  
      // Step 3: Close the modal
      closeProjModal();
  
      // (Optional) You could also do something with webdesignData here
    } catch (err) {
      console.error('Error creating project or analyzing web design:', err);
    }
  };
  
  

  return (
    <>
      <Layout style={{ height: '100vh' }}>
        <Header
          style={{
            display: 'flex',
            alignItems: 'center',
            padding: '0',
            position: 'relative',
          }}
        >
          <img src="images/logo.png" alt="Logo" style={{ height: '70px', width: 'auto' }} />
          <div
            style={{
              position: 'absolute',
              left: '50%',
              transform: 'translateX(-50%)',
            }}
          >
            <h1 style={{ color: 'white', margin: 0 }}>MAX (Machine Assistant for eXperience)</h1>
          </div>
        </Header>


        <Layout style={{ height: '100vh' }}>
          <Sider width={200} className="site-layout-background" theme='light'>
            <div style={{ display: 'flex' }}>
              <h2 style={{ color: 'rgb(4, 21, 39)', textAlign: 'left', marginTop: '1rem', marginLeft: '1rem' }}>Projects</h2>
              <div style={{ marginLeft: 'auto', marginTop: '1.25rem', marginRight: '1rem' }} onClick={showProjModal}>
                <PlusSquareOutlined />
              </div>
            </div>
            <Menu
                mode="inline"
                defaultSelectedKeys={['1']}
                defaultOpenKeys={['sub1']}
                style={{ height: '100%' }}
                items={menuItems}
                onClick={(e) => {
                  setSelectedProjectId(Number(e.key));
                }}
              />
          </Sider>
          <Content
            style={{
              padding: 24,
              margin: 0,
              minHeight: 280,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <h2>Project URL: {allProjects.find(project => project[0] === selectedProjectId)?.[2] || "No URL available"}</h2>
              {/* <Search placeholder='WEBSITE URL' style={{ width: '20rem' }} enterButton={<RightOutlined/>} /> */}
            </div>
            <div className='flex-center'>
              <Radio.Group defaultValue="audience" buttonStyle="solid" className="big-radio">
                <Radio.Button value="audience" onClick={() => setTab("audience")}>Audience</Radio.Button>
                <Radio.Button value="content-clarity" onClick={() => setTab("clarity")}>Content Clarity</Radio.Button>
                <Radio.Button value="web-design" onClick={() => setTab("design")}>Web Design</Radio.Button>
                <Radio.Button value="accessibility" onClick={() => setTab("accessibility")}>Code Accessibility</Radio.Button>

                {/*<Tooltip title="Understand how users interact with your website" placement="bottom"> 
                  <Radio.Button value="audience" onClick={() => setTab("audience")}>Audience</Radio.Button>
                </Tooltip>
                <Tooltip title="Help users understand your content" placement="bottom">
                  <Radio.Button value="content-clarity" onClick={() => setTab("clarity")}>Content Clarity</Radio.Button>
                </Tooltip>
                <Tooltip title="Improve the placement of your content" placement="bottom">
                  <Radio.Button value="web-design" onClick={() => setTab("design")}>Web Design</Radio.Button>
                </Tooltip>
                <Tooltip title="Make sure your content is aligned with WCAG guidelines" placement="bottom">
                  <Radio.Button value="accessibility" onClick={() => setTab("accessibility")}>Code Accessibility</Radio.Button>
                </Tooltip>*/}
              </Radio.Group>
            </div>
            {tab == "audience" ? <Audience projectId={selectedProjectId} /> : <></>}
            {tab == "clarity" ? <ContentClarity/> : <></>} 
            {tab == "design" ? <WebDesign projectId={selectedProjectId}/> : <></>}
            {tab == "accessibility" ? <Accessibility projectId={selectedProjectId}/> : <></>}
          </Content>
        </Layout>
      </Layout>

      <Modal
        open={openProjModal}
        title="Create New Project"
        onOk={closeProjModal}
        onCancel={closeProjModal}
        footer={[
          <Button type="primary" onClick={createProject}>
            Create Project
          </Button>
        ]}
      >
        <Input placeholder="Project Name" value={name} onChange={(e) => setName(e.target.value)} />
        <Input placeholder="URL" style={{marginTop: '1rem'}} value={url} onChange={(e) => setUrl(e.target.value)} />
      </Modal>
    </>
  )
}

export default App
