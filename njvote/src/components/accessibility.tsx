import { ExclamationCircleFilled, CheckCircleFilled } from '@ant-design/icons';
import { Collapse, Typography, Row, Col } from 'antd';

const { Panel } = Collapse;
const { Text } = Typography;

const Accessibility = () => {
  return (
    <Collapse accordion style={{ marginTop: '2rem' }}>
      <Panel header="Add a language attribute to the html tag" key="1">
        <Row gutter={16}>
          <Col span={12}>
            <Text strong><ExclamationCircleFilled style={{color: 'red'}}/> Original</Text>
            <pre>{`<html>`}</pre>
          </Col>
          <Col span={12}>
            <Text strong><CheckCircleFilled style={{color: 'green'}}/> Revised</Text>
            <pre>{`<html lang="en">`}</pre>
          </Col>
        </Row>
      </Panel>

      <Panel header="Use semantic headings in a logical order" key="2">
        <Text>
          Ensure headings are used in order without skipping levels.
        </Text>
        <Row gutter={16} style={{ marginTop: '1rem' }}>
          <Col span={12}>
            <Text strong><ExclamationCircleFilled style={{color: 'red'}}/> Original</Text>
            <pre>{`<img src="assets/images/njvotes-header-logo.png" 
  alt="NJVotes Logo" 
  title="N-Votes Logo" 
  class="njdos-logo">`}</pre>
          </Col>
          <Col span={12}>
            <Text strong><CheckCircleFilled style={{color: 'green'}}/> Revised</Text>
            <pre>{`<img src="assets/images/njvotes-header-logo.png" 
  alt="New Jersey Votes Logo" 
  class="njdos-logo">`}</pre>
          </Col>
        </Row>
      </Panel>

      <Panel header="Remove redundant title attributes" key="3">
        <Row gutter={16}>
          <Col span={12}>
            <Text strong><ExclamationCircleFilled style={{color: 'red'}}/> Original</Text>
            <pre>{`<img src="assets/images/njvotes-header-logo.png" 
  alt="New Jersey Votes Logo" 
  title="New Jersey Votes Logo" 
  class="njdos-logo">`}</pre>
          </Col>
          <Col span={12}>
            <Text strong><CheckCircleFilled style={{color: 'green'}}/> Revised</Text>
            <pre>{`<label for="qt">Search</label>
<input type="text" 
  class="form-control p-i" 
  placeholder="Type Search Here" 
  id="qt" name="qt" />`}</pre>
          </Col>
        </Row>
      </Panel>

      <Panel header="Add labels to form inputs" key="4">
        <Row gutter={16}>
          <Col span={12}>
            <Text strong><ExclamationCircleFilled style={{color: 'red'}}/> Original</Text>
            <pre>{`<input type="text" class="form-control p-i">`}</pre>
          </Col>
          <Col span={12}>
            <Text strong><CheckCircleFilled style={{color: 'green'}}/> Revised</Text>
            <pre>{`<label for="qt">Search</label>
<input type="text" class="form-control p-i" id="qt" name="qt">`}</pre>
          </Col>
        </Row>
      </Panel>
    </Collapse>
  );
};

export default Accessibility;
