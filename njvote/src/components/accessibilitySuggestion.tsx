// Import necessary Ant Design components and icons
import { Typography, Row, Col, message } from 'antd';
import {
  ExclamationCircleFilled,
  CheckCircleFilled,
  CopyOutlined,
  BulbOutlined,
} from '@ant-design/icons';

const { Text } = Typography;

// Props interface definition
export interface AccessibilitySuggestionProps {
  original: string;
  revised: string;
  explanation: string;
}

// Style for <pre> elements to ensure proper text wrapping and scroll behavior
const preStyle: React.CSSProperties = {
  whiteSpace: 'pre-wrap',
  wordBreak: 'break-word',
  overflow: 'auto',
};

// Main component to display an accessibility suggestion
const AccessibilitySuggestion = (props: AccessibilitySuggestionProps) => {
  const [messageApi, contextHolder] = message.useMessage(); // AntD message hook for feedback

  // Displays a "Copied to clipboard" success message
  const copied = () => {
    messageApi.open({
      type: 'success',
      content: 'Copied to clipboard',
      duration: 1,
    });
  };

  return (
    <>
      {/* Enables context for AntD message feedback */}
      {contextHolder}

      {/* First row: Original and Revised text side-by-side */}
      <Row gutter={16}>
        {/* Original Text Column */}
        <Col span={12}>
          <Text strong>
            <ExclamationCircleFilled style={{ color: 'red' }} /> Original
          </Text>
          <pre style={preStyle}>{props.original}</pre>
        </Col>

        {/* Revised Text Column */}
        <Col span={12}>
          <div style={{ position: 'relative' }}>
            <Text strong>
              <CheckCircleFilled style={{ color: 'green' }} /> Revised
            </Text>

            {/* Copy to clipboard icon, positioned in the top-right of the column */}
            <CopyOutlined
              style={{
                position: 'absolute',
                top: 0,
                right: 0,
                transform: 'translateY(0.15rem)', // Vertically align with text
                cursor: 'pointer',
                fontSize: '16px',
                color: '#1890ff',
              }}
              onClick={() => {
                copied();
                navigator.clipboard.writeText(props.revised);
              }}
            />

            <pre style={preStyle}>{props.revised}</pre>
          </div>
        </Col>
      </Row>

      {/* Second row: Explanation of the suggestion */}
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
