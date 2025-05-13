import { Typography, Row, Col, message } from 'antd';
import { ExclamationCircleFilled, CheckCircleFilled, CopyOutlined, BulbOutlined } from '@ant-design/icons';

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
  const [messageApi, contextHolder] = message.useMessage();

  const copied = () => {
    messageApi.open({
      type: 'success',
      content: 'Copied to clipboard',
      duration: 1,
    });
  };

  return (
    <>
      {contextHolder}
      <Row gutter={16}>
        <Col span={12}>
          <Text strong>
            <ExclamationCircleFilled style={{ color: 'red' }} /> Original
          </Text>
          <pre style={preStyle}>{props.original}</pre>
        </Col>
        <Col span={12}>
          <div style={{ position: 'relative' }}>
            <Text strong>
              <CheckCircleFilled style={{ color: 'green' }} /> Revised
            </Text>

            <CopyOutlined
              style={{
                position: 'absolute',
                top: 0,
                right: 0,
                transform: 'translateY(0.15rem)', // fine-tune vertical alignment with text
                cursor: 'pointer',
                fontSize: '16px',
                color: '#1890ff',
              }}
              onClick={() => {
                copied();
                navigator.clipboard.writeText(props.revised)}
              }
            />

            <pre style={preStyle}>{props.revised}</pre>
          </div>
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
