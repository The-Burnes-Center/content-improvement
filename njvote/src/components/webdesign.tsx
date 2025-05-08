import { useState, useEffect } from 'react';
import { Table, Typography } from 'antd';
import {
  ExclamationCircleOutlined,
  SearchOutlined,
  ToolOutlined,
  BulbOutlined,
} from '@ant-design/icons';

const { Title } = Typography;

interface WebDesignSuggestion {
  label: string;
  area: string;
  suggestion: string;
  reason: string;
}

export interface WebDesignProps {
  projectId: number | null;
}

const WebDesign = (props: WebDesignProps) => {
  const [suggestions, setSuggestions] = useState<WebDesignSuggestion[]>([]);


  const fetchWebDevSuggestions = async () => {
    setSuggestions([]);
    try {
      const auditResponse = await fetch(`api/get_webdesign_audit?projectId=${props.projectId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (auditResponse.ok) {
        const auditData = await auditResponse.json();
        const webDesignAuditId = auditData['web_design_audit'][0];

        console.log("webdesignAuditId", webDesignAuditId)

        const response = await fetch(`api/get_webdesign_suggestions?webDesignAuditId=${webDesignAuditId}`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        });

        const data = await response.json();
        if (response.ok) {
          const suggestions = data['suggestions'].map((item: any) => ({
            label: item[0],
            area: item[2],
            suggestion: item[3],
            reason: item[4],
          }));
          setSuggestions(suggestions);
        } else {
          console.error('Failed to fetch web design suggestions.');
        }

      } else {
        console.error('Failed to fetch web design audit.');
      }
    } catch (err) {
      console.error(err);
      console.error('An error occurred while fetching web design suggestions.');
    }
  };

  useEffect(() => {
    console.log('Fetching web design suggestions...');
    fetchWebDevSuggestions();
  }, [props.projectId]);

  const columns = [
    {
      title: (
        <span>
          <SearchOutlined /> Area
        </span>
      ),
      dataIndex: 'area',
      key: 'area',
      render: (text: string) => <strong>{text}</strong>,
    },
    {
      title: (
        <span>
          <ToolOutlined /> Suggestion
        </span>
      ),
      dataIndex: 'suggestion',
      key: 'suggestion',
    },
    {
      title: (
        <span>
          <BulbOutlined /> Reason
        </span>
      ),
      dataIndex: 'reason',
      key: 'reason',
    },
  ];

  return (
    <div style={{ padding: '1rem' }}>
      <h2> Improve the placement of your content</h2>
      <Title level={4}>
        <ExclamationCircleOutlined style={{ color: '#faad14', marginRight: '0.5rem' }} />
        Suggested Improvements (with reasoning)
      </Title>
      <Table columns={columns} dataSource={suggestions} pagination={false} />
    </div>
  );
};

export default WebDesign;
