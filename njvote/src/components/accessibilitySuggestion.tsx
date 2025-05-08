import { Typography, Row, Col } from 'antd';
import { ExclamationCircleFilled, CheckCircleFilled, QuestionCircleOutlined, QuestionCircleTwoTone, BulbOutlined } from '@ant-design/icons';

const { Text } = Typography;

export interface AccessibilitySuggestionProps {
  original: string;
  revised: string;
  explanation: string;
}

const preStyle: React.CSSProperties = {
  whiteSpace: 'pre-wrap',
  wordBreak: 'break-word',
  overflow: 'auto',
};

const AccessibilitySuggestion = (props: AccessibilitySuggestionProps) => {
  return (
    <>
      <Row gutter={16}>
        <Col span={12}>
          <Text strong>
            <ExclamationCircleFilled style={{ color: 'red' }} /> Original
          </Text>
          <pre style={preStyle}>{props.original}</pre>
        </Col>
        <Col span={12}>
          <Text strong>
            <CheckCircleFilled style={{ color: 'green' }} /> Revised
          </Text>
          <pre style={preStyle}>{props.revised}</pre>
        </Col>
      </Row>
      <Row gutter={16}>
        <Text strong>
          <BulbOutlined style={{ color: '#e6e615' }} /> Why?
        </Text>
        <pre style={preStyle}>{props.explanation}</pre>
      </Row>
    </>
  );
};

export default AccessibilitySuggestion;
