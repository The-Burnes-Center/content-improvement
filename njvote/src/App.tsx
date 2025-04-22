import './App.css'
import { useState } from 'react';
import { Input, Layout, Menu, Radio, Modal, Button, Tooltip } from "antd";
import Audience from './components/audience';
import { PlusSquareOutlined } from '@ant-design/icons';
import ContentClarity from './components/contentclarity';
import WebDesign from './components/webdesign';
import Accessibility from './components/accessibility'

function App() {

  const { Header, Content, Sider } = Layout;

  const { Search } = Input;

  const menuItems = [{key: '1', label: 'Home page'}, {key: '2', label: 'Register page'}]

  const [openProjModal, setProjModalOpen] = useState(false);

  const [tab, setTab] = useState('audience');

  const showProjModal = () => {
    setProjModalOpen(true);
  };

  const closeProjModal = () => {
    setProjModalOpen(false);
  }

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
              <h2 style={{ marginRight: '2%' }}>Project URL: URL here</h2>
              {/* <Search placeholder='WEBSITE URL' style={{ width: '20rem' }} enterButton={<RightOutlined/>} /> */}
            </div>
            <div className='flex-center'>
              <Radio.Group defaultValue="audience" buttonStyle="solid" className="big-radio">
                <Tooltip title="Understand how users interact with your website" placement="bottom">
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
                </Tooltip>
              </Radio.Group>
            </div>
            {tab == "audience" ? <Audience /> : <></>}
            {tab == "clarity" ? <ContentClarity/> : <></>} 
            {tab == "design" ? <WebDesign/> : <></>}
            {tab == "accessibility" ? <Accessibility/> : <></>}
          </Content>
        </Layout>
      </Layout>

      <Modal
        open={openProjModal}
        title="Create New Project"
        onOk={closeProjModal}
        onCancel={closeProjModal}
        footer={[
          <Button type="primary" onClick={closeProjModal}>
            Create Project
          </Button>
        ]}
      >
        <Input placeholder="Project Name" />
        <Input placeholder="URL" style={{marginTop: '1rem'}} />
      </Modal>
    </>
  )
}

export default App
